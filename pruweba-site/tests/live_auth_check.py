"""Live auth check: real Supabase users, real JWTs, real HTTP handler.

Non-destructive: provisions a sandbox project + two throwaway auth users,
exercises the 401/403/200 matrix, then deletes everything.

Requires SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env, and the
assigned_user_email column (see supabase_schema.sql).
Run: .venv/Scripts/python.exe tests/live_auth_check.py
"""

import json
import os
import sys
import threading
import urllib.error
import urllib.request
import uuid
from http.server import HTTPServer

sys.path.insert(0, os.path.dirname(__file__))
from _onboarding import MerkleSeal
from portal import MILESTONES, PROJECTS, _supabase, handler

CLIENT = "ZZ_Auth_Sandbox"
OTHER = "ZZ_Auth_Sandbox_Other"
PHASES = ["Alpha scope", "Beta build", "Gamma handover"]
PORT = 8801
BASE = f"http://127.0.0.1:{PORT}"
PW = "Sandbox!" + uuid.uuid4().hex[:12]
OWNER = f"owner+{uuid.uuid4().hex[:8]}@example.com"
INTRUDER = f"intruder+{uuid.uuid4().hex[:8]}@example.com"


def call(path, token=None, data=None, method=None):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def make_user(sb, email):
    res = sb.auth.admin.create_user(
        {"email": email, "password": PW, "email_confirm": True}
    )
    return res.user.id


def token_for(email):
    from supabase import create_client

    anon = (
        os.environ.get("SUPABASE_ANON_KEY")
        or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    )
    c = create_client(os.environ["SUPABASE_URL"], anon)
    res = c.auth.sign_in_with_password({"email": email, "password": PW})
    return res.session.access_token


def cleanup(sb, uids):
    for row in sb.table(PROJECTS).select("id").in_("client_name", [CLIENT, OTHER]).execute().data or []:
        sb.table(MILESTONES).delete().eq("project_id", row["id"]).execute()
        sb.table(PROJECTS).delete().eq("id", row["id"]).execute()
    for uid in uids:
        try:
            sb.auth.admin.delete_user(uid)
        except Exception:
            pass


def main():
    sb = _supabase()
    print("[1] connected ->", os.environ["SUPABASE_URL"][:34] + "...")

    uids = []
    cleanup(sb, [])
    try:
        uids.append(make_user(sb, OWNER))
        uids.append(make_user(sb, INTRUDER))
        print("[2] users created:", OWNER, "/", INTRUDER)

        pid = sb.table(PROJECTS).insert(
            {
                "client_name": CLIENT,
                "assigned_user_email": OWNER,
                "problem_statement": "auth sandbox",
                "current_phase": 1,
            }
        ).execute().data[0]["id"]
        sb.table(MILESTONES).insert(
            [
                {"project_id": pid, "phase_id": i, "name": n,
                 "status": "active" if i == 1 else "pending", "client_signed": False}
                for i, n in enumerate(PHASES, 1)
            ]
        ).execute()
        oid = sb.table(PROJECTS).insert(
            {"client_name": OTHER, "assigned_user_email": INTRUDER,
             "problem_statement": "auth sandbox (other tenant)", "current_phase": 1}
        ).execute().data[0]["id"]
        sb.table(MILESTONES).insert(
            [{"project_id": oid, "phase_id": 1, "name": "Other alpha",
              "status": "active", "client_signed": False}]
        ).execute()
        print("[3] sandbox projects", pid, "(owner) +", oid, "(intruder)")

        owner_tok = token_for(OWNER)
        intruder_tok = token_for(INTRUDER)
        print("[4] real JWTs issued (owner len", len(owner_tok), ")")

        srv = HTTPServer(("127.0.0.1", PORT), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            # --- unauthenticated ---
            assert call(f"/api/portal?client={CLIENT}")[0] == 401
            assert call(f"/api/portal?client={CLIENT}", token="garbage.token.here")[0] == 401
            assert call("/api/portal/sign", data={"milestone": PHASES[0]})[0] == 401
            print("[5] no token / bad token -> 401 ✓")

            # --- wrong user ---
            # The intruder owns their OWN project, so a 403 here proves real
            # cross-tenant isolation, not merely "user has no project".
            s, b = call(f"/api/portal?client={CLIENT}", token=intruder_tok)
            assert s == 403, (s, b)
            s2, b2 = call("/api/portal/sign", token=intruder_tok,
                          data={"client": CLIENT, "milestone": PHASES[0]})
            assert s2 == 403, (s2, b2)
            print("[6] intruder read/write -> 403 ✓ :", b.get("error"))

            # ...and the intruder's own project resolves fine (no false lockout)
            s6, b6 = call(f"/api/portal?client={OTHER}", token=intruder_tok)
            assert s6 == 200 and b6["client"] == OTHER, (s6, b6)
            print("[6b] intruder sees only their own project ->", b6["client"], "✓")

            # --- owner ---
            s3, b3 = call(f"/api/portal?client={CLIENT}", token=owner_tok)
            assert s3 == 200 and b3["user"] == OWNER, (s3, b3)
            print("[7] owner GET -> 200, percent", b3["progress"]["percent"])

            # token-only: client inferred from the JWT
            s4, b4 = call("/api/portal", token=owner_tok, data={})
            assert s4 == 200 and b4["client"] == CLIENT, (s4, b4)
            print("[8] owner POST (no client, inferred) -> 200,", b4["client"])

            s5, b5 = call("/api/portal/sign", token=owner_tok,
                          data={"client": CLIENT, "milestone": PHASES[0]})
            assert s5 == 200, (s5, b5)
            print("[9] owner sign -> 200, proof", b5["proof"]["hash"][:16], "…",
                  b5["progress"]["percent"], "%")

            assert call("/api/portal/sign", token=owner_tok,
                        data={"client": CLIENT, "milestone": PHASES[0]})[0] == 409
            print("[10] replay -> 409 ✓")

            # intruder still cannot see the sealed data
            assert call(f"/api/portal?client={CLIENT}", token=intruder_tok)[0] == 403
            print("[11] intruder still blocked after seal ✓")

            # Chain must survive decomposition into rows and reassembly.
            for n in PHASES[1:2]:
                assert call("/api/portal/sign", token=owner_tok,
                            data={"client": CLIENT, "milestone": n})[0] == 200
            s7, b7 = call(f"/api/portal?client={CLIENT}", token=owner_tok)
            proofs = b7["progress"]["proofs"]
            prev = MerkleSeal.GENESIS
            for pr in proofs:
                assert pr["prev"] == prev, f"broken link at {pr['milestone']}"
                prev = pr["hash"]
            assert len(proofs) == 2 and b7["progress"]["chain_valid"], b7["progress"]
            print("[12] chain linked + valid across DB reload (2 proofs) ✓")

            raw = sb.table(MILESTONES).select("name,client_signed,proof_hash").eq(
                "project_id", pid).order("phase_id").execute().data
            assert [r["client_signed"] for r in raw] == [True, True, False], raw
            assert [r["proof_hash"] for r in raw[:2]] == [p["hash"] for p in proofs], raw
            print("[13] DB rows persisted + match returned proofs ✓")
        finally:
            srv.shutdown()
    finally:
        cleanup(sb, uids)
        print("[14] sandbox + users removed")

    print("LIVE_AUTH_OK")


if __name__ == "__main__":
    main()
