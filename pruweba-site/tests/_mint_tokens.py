"""Issue real Supabase tokens for a throwaway user (jsdom callback test).

    python tests/_mint_tokens.py          -> creates user, writes tests/_tokens.json
    python tests/_mint_tokens.py cleanup  -> deletes that user, removes the file
"""

import json
import os
import pathlib
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from portal import _supabase

STATE = pathlib.Path(__file__).with_name("_tokens.json")

if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
    if STATE.exists():
        uid = json.loads(STATE.read_text())["user_id"]
        try:
            _supabase().auth.admin.delete_user(uid)
            print("deleted", uid)
        except Exception as exc:
            print("delete failed:", exc)
        STATE.unlink()
    sys.exit(0)

email = f"cbtest+{uuid.uuid4().hex[:8]}@example.com"
pw = "Sandbox!" + uuid.uuid4().hex[:12]

sb = _supabase()
uid = sb.auth.admin.create_user({"email": email, "password": pw, "email_confirm": True}).user.id

from supabase import create_client

sess = create_client(
    os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"]
).auth.sign_in_with_password({"email": email, "password": pw}).session

STATE.write_text(
    json.dumps(
        {
            "user_id": uid,
            "email": email,
            "access_token": sess.access_token,
            "refresh_token": sess.refresh_token,
            "supabase_url": os.environ["SUPABASE_URL"],
            "anon_key": os.environ["SUPABASE_ANON_KEY"],
        }
    ),
    encoding="utf-8",
)
print("created", email, uid)
