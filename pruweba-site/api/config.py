"""GET /api/config -> public Supabase config for the browser.

Static HTML has no build step, so `process.env` does not exist client-side.
This endpoint hands the browser ONLY the publishable/anon key, which is
designed to be public and is constrained by RLS. The service_role key is
never exposed here.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler


def public_config() -> tuple[int, dict]:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = (
        os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )
    if not url or not key:
        return 500, {"ok": False, "error": "public Supabase config is not set"}
    return 200, {"ok": True, "supabaseUrl": url, "supabaseAnonKey": key}


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self._send(204, {})

    def do_GET(self):  # noqa: N802
        try:
            status, payload = public_config()
        except Exception as exc:  # noqa: BLE001
            status, payload = 500, {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._send(status, payload)
