"""Vercel Python Serverless Function \u2014 Client Portal API (authenticated).

Routes (see vercel.json rewrites):
  GET  /api/portal?client=<name>  -> dashboard view + progress
  POST /api/portal                -> same as GET (token-only, client inferred)
  POST /api/portal/sign           -> seal a milestone, return updated view

AUTH: every request requires `Authorization: Bearer <supabase access token>`.
The token is verified with supabase.auth.get_user(); the caller may only touch
projects whose client_projects.assigned_user_email matches their verified email.
Anything else is 403.

Storage (live schema, verified by introspection):
  client_projects   (id uuid pk, client_name, assigned_user_email, problem_statement,
                     success_criteria, constraints, current_phase int, created_at)
  project_milestones(id uuid pk, project_id uuid fk, phase_id int, name, status,
                     client_signed bool, proof_hash text, completed_at, created_at)

Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (service_role bypasses RLS),
     SUPABASE_ANON_KEY (used only to validate user tokens).
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

try:
    from ._onboarding import ClientOnboarding, MerkleSeal, STATUS_DONE
except ImportError:  # pragma: no cover - Vercel loads this as a top-level module
    from _onboarding import ClientOnboarding, MerkleSeal, STATUS_DONE

PROJECTS = "client_projects"
MILESTONES = "project_milestones"


class AuthError(Exception):
    """Raised when a caller is unauthenticated (401)."""


class ForbiddenError(Exception):
    """Raised when an authenticated caller may not touch this project (403)."""


def _supabase():
    from supabase import create_client  # supabase-py

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    return create_client(url, key)


def _auth_client():
    """Anon-key client used purely to validate user access tokens."""
    from supabase import create_client

    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_ANON_KEY")
        or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and an anon/publishable key must be set")
    return create_client(url, key)


def bearer_token(headers) -> str:
    raw = ""
    if headers is not None:
        raw = headers.get("Authorization") or headers.get("authorization") or ""
    parts = raw.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise AuthError("missing or malformed Authorization: Bearer <token> header")
    return parts[1].strip()


def verify_user(token: str) -> str:
    """Verify a Supabase access token and return the caller's email."""
    try:
        res = _auth_client().auth.get_user(token)
    except Exception as exc:  # noqa: BLE001 - supabase raises varied auth errors
        raise AuthError(f"invalid or expired token: {type(exc).__name__}") from exc

    user = getattr(res, "user", None)
    email = getattr(user, "email", None) if user else None
    if not email:
        raise AuthError("token did not resolve to a user")
    return email.strip().lower()


def _normalize(name: str) -> str:
    return (name or "").strip().replace(" ", "_")


def _find_project(sb, client: str, email: str) -> dict:
    """Resolve the caller's project. Access is scoped by assigned_user_email.

    When `client` is empty the project is inferred from the token alone.

    SECURITY: when a client name IS supplied it is resolved against the whole
    projects table FIRST, and ownership is checked afterwards. Resolving only
    within the caller's own rows would let a prefix match silently redirect a
    request for "Acme" to the caller's own "Acme_Other" -- answering 200 for a
    project the caller never asked for, and masking the 403.
    """
    owned = (
        sb.table(PROJECTS).select("*").ilike("assigned_user_email", email).execute().data or []
    )

    if not client:
        if not owned:
            raise ForbiddenError(f"no project assigned to {email}")
        if len(owned) > 1:
            raise ForbiddenError("multiple projects assigned; specify ?client=")
        return owned[0]

    # Resolve the requested name globally: exact match, else unambiguous prefix.
    target = (sb.table(PROJECTS).select("*").eq("client_name", client)
              .limit(1).execute().data or [None])[0]
    if target is None:
        matches = (sb.table(PROJECTS).select("*").ilike("client_name", f"{client}%")
                   .execute().data or [])
        if len(matches) > 1:
            raise ForbiddenError(
                f"ambiguous client {client!r}; matches "
                + ", ".join(sorted(m["client_name"] for m in matches))
            )
        target = matches[0] if matches else None
    if target is None:
        raise LookupError(f"client not found: {client}")

    assigned = (target.get("assigned_user_email") or "").strip().lower()
    if assigned != email:
        raise ForbiddenError(f"{email} is not authorized for client {client!r}")
    return target


def _fetch_milestones(sb, project_id: str) -> list[dict]:
    res = (
        sb.table(MILESTONES).select("*").eq("project_id", project_id).order("phase_id").execute()
    )
    return res.data or []


def _load(sb, client: str, email: str) -> tuple[ClientOnboarding, dict, list[dict]]:
    project = _find_project(sb, client, email)
    rows = _fetch_milestones(sb, project["id"])

    milestones = [
        {
            "name": r["name"],
            "status": r.get("status") or "pending",
            "completed_at": r.get("completed_at"),
        }
        for r in rows
    ]

    # Reconstruct the seal chain from persisted proof hashes, in completion order.
    sealed = [r for r in rows if r.get("proof_hash")]
    sealed.sort(key=lambda r: (r.get("completed_at") or "", r.get("phase_id") or 0))
    proofs, prev = [], MerkleSeal.GENESIS
    for r in sealed:
        proofs.append(
            {
                "client": project["client_name"],
                "milestone": r["name"],
                "prev": prev,
                "sealed_at": r.get("completed_at"),
                "hash": r["proof_hash"],
            }
        )
        prev = r["proof_hash"]

    return ClientOnboarding(project["client_name"], milestones, proofs), project, rows


def _persist(sb, project: dict, rows: list[dict], onboarding: ClientOnboarding, milestone: str) -> None:
    """Write the newly sealed milestone back, using service_role to bypass RLS."""
    row = next((r for r in rows if r["name"] == milestone), None)
    if row is None:
        raise LookupError(f"milestone row not found: {milestone}")

    state = next(m for m in onboarding.milestones if m["name"] == milestone)
    proof = onboarding.proofs_json()[-1]

    sb.table(MILESTONES).update(
        {
            "status": STATUS_DONE,
            "client_signed": True,
            "proof_hash": proof["hash"],
            "completed_at": state["completed_at"],
        }
    ).eq("id", row["id"]).execute()

    nxt = next((m for m in onboarding.milestones if m["status"] != STATUS_DONE), None)
    if nxt is not None:
        nxt_row = next((r for r in rows if r["name"] == nxt["name"]), None)
        if nxt_row is not None:
            sb.table(MILESTONES).update({"status": "active"}).eq("id", nxt_row["id"]).execute()
            sb.table(PROJECTS).update({"current_phase": nxt_row.get("phase_id")}).eq(
                "id", project["id"]
            ).execute()


def _payload(onboarding: ClientOnboarding, email: str) -> dict:
    return {
        "ok": True,
        "client": onboarding.client_name,
        "user": email,
        "client_view": onboarding.client_view(),
        "progress": onboarding.progress(),
    }


# --------------------------------------------------------------------------
# Handlers
# --------------------------------------------------------------------------
def handle_get(client: str, token: str | None) -> tuple[int, dict]:
    try:
        email = verify_user(token or "")
    except AuthError as exc:
        return 401, {"ok": False, "error": str(exc)}

    sb = _supabase()
    try:
        onboarding, _project, _rows = _load(sb, _normalize(client), email)
    except ForbiddenError as exc:
        return 403, {"ok": False, "error": str(exc)}
    except LookupError as exc:
        return 404, {"ok": False, "error": str(exc)}
    return 200, _payload(onboarding, email)


def handle_sign(body: dict, token: str | None) -> tuple[int, dict]:
    try:
        email = verify_user(token or "")
    except AuthError as exc:
        return 401, {"ok": False, "error": str(exc)}

    client = _normalize(body.get("client", ""))
    milestone = (body.get("milestone") or "").strip()
    if not milestone:
        return 400, {"ok": False, "error": "body requires 'milestone'"}

    sb = _supabase()
    try:
        onboarding, project, rows = _load(sb, client, email)
    except ForbiddenError as exc:
        return 403, {"ok": False, "error": str(exc)}
    except LookupError as exc:
        return 404, {"ok": False, "error": str(exc)}

    try:
        proof = onboarding.complete_milestone(milestone)
    except KeyError as exc:
        return 404, {"ok": False, "error": str(exc)}
    except ValueError as exc:
        return 409, {"ok": False, "error": str(exc)}

    _persist(sb, project, rows, onboarding, milestone)
    out = _payload(onboarding, email)
    out["proof"] = proof
    return 200, out


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _token(self) -> str | None:
        try:
            return bearer_token(self.headers)
        except AuthError:
            return None

    def do_OPTIONS(self):  # noqa: N802
        self._send(204, {})

    def do_GET(self):  # noqa: N802
        try:
            qs = parse_qs(urlparse(self.path).query)
            status, payload = handle_get((qs.get("client") or [""])[0], self._token())
        except Exception as exc:  # noqa: BLE001
            status, payload = 500, {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._send(status, payload)

    def do_POST(self):  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw or b"{}")
            token = self._token()
            if urlparse(self.path).path.rstrip("/").endswith("/sign"):
                status, payload = handle_sign(body, token)
            else:
                status, payload = handle_get(body.get("client", ""), token)
        except json.JSONDecodeError:
            status, payload = 400, {"ok": False, "error": "invalid JSON body"}
        except Exception as exc:  # noqa: BLE001
            status, payload = 500, {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._send(status, payload)
