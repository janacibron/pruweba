#!/usr/bin/env python3
"""Shared cookie/session utilities using stdlib only."""
import json, os, time, urllib.request, urllib.error
from http.cookiejar import CookieJar, MozillaCookieJar

DEFAULT_COOKIE_POLICY = None

def load_cookies(path):
    if not os.path.exists(path):
        return []
    try:
        jar = MozillaCookieJar(path)
        jar.load(ignore_discard=True, ignore_expires=True)
        return list(jar)
    except Exception:
        return []


def save_cookies(path, cookies):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    jar = MozillaCookieJar(path)
    for c in cookies:
        try:
            jar.set_cookie(c)
        except Exception:
            pass
    jar.save(ignore_discard=True, ignore_expires=True)


def cookies_to_dict(cookies):
    return {c.name: c.value for c in cookies if c.name}


def build_cookie_header(path):
    cookies = load_cookies(path)
    return "; ".join(f"{c.name}={c.value}" for c in cookies)


def session_is_valid(url, cookies_path, timeout=30):
    """Return True if the current cookies let us fetch the target page."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Cookie": build_cookie_header(cookies_path),
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def refresh_session(url, cookies_path):
    """Placeholder: in real flows, perform login and save cookies.
    Here we report whether refresh is needed.
    """
    valid = session_is_valid(url, cookies_path)
    return {
        "valid": valid,
        "action": "none" if valid else "refresh_required",
        "checked_at": int(time.time()),
    }
