"""Live end-to-end check against real Supabase + the real HTTP handler.

Non-destructive: operates on a disposable client, then deletes it.
Requires SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env.
Run: .venv/Scripts/python.exe tests/live_check.py
"""

import json
import os
import pathlib
import sys
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"'))

from _onboarding import MerkleSeal  # noqa: E402
from portal import PROJECTS, MILESTONES, _supabase, handler  # noqa: E402

CLIENT = "ZZ_Verify_Sandbox"
PHASES = ["Alpha scope", "Beta build", "Gamma handover"]
PORT = 8799
BASE = f"http://127.0.0.1:{PORT}"


def call(path, data=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def setup(sb):
    teardown(sb)
    pid = sb.table(PROJECTS).insert(
        {"client_name": CLIENT, "problem_statement": "verification sandbox", "current_phase": 1}
    ).execute().data[0]["id"]
    sb.table(MILESTONES).insert(
        [
            {"project_id": pid, "phase_id": i, "name": n,
             "status": "active" if i == 1 else "pending", "client_signed": False}
            for i, n in enumerate(PHASES, 1)
        ]
    ).execute()
    return pid


def teardown(sb):
    for row in sb.table(PROJECTS).select("id").eq("client_name", CLIENT).execute().data or []:
        sb.table(MILESTONES).delete().eq("project_id", row["id"]).execute()
        sb.table(PROJECTS).delete().eq("id", row["id"]).execute()


def main():
    sb = _supabase()
    print("[1] connected ->", os.environ["SUPABASE_URL"][:34] + "...")
    pid = setup(sb)
    print("[2] sandbox project", pid)

    srv = HTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        s, b = call(f"/api/portal?client={CLIENT}")
        assert s == 200, b
        print("[3] GET ->", s, "| percent", b["progress"]["percent"])

        assert call("/api/portal")[0] == 400
        assert call(f"/api/portal?client=NoSuch__{CLIENT}")[0] == 404
        assert call("/api/portal/sign", {"client": CLIENT})[0] == 400
        assert call("/api/portal/sign", {"client": CLIENT, "milestone": "nope"})[0] == 404
        print("[4] guards -> 400/404/400/404 ok")

        for n in PHASES[:2]:
            s2, b2 = call("/api/portal/sign", {"client": CLIENT, "milestone": n})
            assert s2 == 200, b2
            print(f"[5] sealed {n!r} -> {b2['proof']['hash'][:16]}… ({b2['progress']['percent']}%)")

        assert call("/api/portal/sign", {"client": CLIENT, "milestone": PHASES[0]})[0] == 409
        print("[6] double sign -> 409")

        # Chain must survive decomposition into rows and reassembly from the DB.
        s3, b3 = call(f"/api/portal?client={CLIENT}")
        p = b3["progress"]
        prev = MerkleSeal.GENESIS
        for pr in p["proofs"]:
            assert pr["prev"] == prev, f"broken link at {pr['milestone']}"
            prev = pr["hash"]
        assert p["chain_valid"] and len(p["proofs"]) == 2, p
        print("[7] reload -> 2 proofs, chain linked + valid,", p["percent"], "%")

        raw = sb.table(MILESTONES).select("name,status,client_signed,proof_hash").eq(
            "project_id", pid
        ).order("phase_id").execute().data
        assert [r["client_signed"] for r in raw] == [True, True, False], raw
        assert raw[0]["proof_hash"] == p["proofs"][0]["hash"]
        assert raw[2]["status"] == "active", "next phase must be promoted"
        print("[8] raw DB rows consistent; next phase promoted to active")
    finally:
        srv.shutdown()
        teardown(sb)
        print("[9] sandbox removed")

    print("LIVE_OK")


if __name__ == "__main__":
    main()
