import sys, os, pathlib
sys.stdout.reconfigure(encoding="utf-8")
root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "api"))
for line in (root / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"'))

from portal import _supabase, PROJECTS, MILESTONES

PHASES = ["Discovery & scoping", "Contract sealed", "Core module built",
          "Integration tests green", "Production handover"]
sb = _supabase()
res = sb.table(PROJECTS).select("*").eq("client_name", "Paydora_Payments").limit(1).execute()
row = (res.data or [None])[0]
if row is None:
    row = sb.table(PROJECTS).insert({
        "client_name": "Paydora_Payments",
        "problem_statement": "Payment reconciliation platform delivery",
        "success_criteria": "All 5 phases sealed with verifiable proofs",
        "constraints": "Fixed scope, governed sign-off",
        "current_phase": 1,
    }).execute().data[0]
    print("created project", row["id"])
else:
    print("project exists", row["id"])

have = {m["name"] for m in (sb.table(MILESTONES).select("name").eq("project_id", row["id"]).execute().data or [])}
todo = [{"project_id": row["id"], "phase_id": i, "name": n,
         "status": "active" if i == 1 else "pending", "client_signed": False}
        for i, n in enumerate(PHASES, 1) if n not in have]
if todo:
    sb.table(MILESTONES).insert(todo).execute()
print("milestones inserted:", len(todo), "| existing:", len(have))
