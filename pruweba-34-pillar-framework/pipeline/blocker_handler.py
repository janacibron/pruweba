#!/usr/bin/env python3
"""Blocker handling: CAPTCHA detection, rate limiting, retries, blocked platform registry."""
import json, os, time, urllib.request, urllib.error
from datetime import datetime, timezone

BLOCKED_FILE = os.path.join(os.path.dirname(__file__), "blocked_platforms.json")


def load_blocked():
    if not os.path.exists(BLOCKED_FILE):
        return {}
    try:
        with open(BLOCKED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_blocked(data):
    with open(BLOCKED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_blocked(platform, reason, last_checked=None, next_check_days=30):
    data = load_blocked()
    data[platform] = {
        "reason": reason,
        "last_checked": last_checked or datetime.now(timezone.utc).isoformat(),
        "next_check_days": next_check_days,
        "retry_count": data.get(platform, {}).get("retry_count", 0) + 1,
    }
    save_blocked(data)


def should_retry_blocked(platform):
    data = load_blocked()
    entry = data.get(platform)
    if not entry:
        return True
    last = entry.get("last_checked")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        next_check = last_dt.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= next_check
    except Exception:
        return True


def is_captcha(text):
    if not text:
        return False
    lower = text.lower()
    markers = [
        "captcha",
        "recaptcha",
        "hcaptcha",
        "cloudflare",
        "access denied",
        "verify you are human",
        "are you a robot",
    ]
    return any(m in lower for m in markers)


def is_rate_limited(status):
    return status in (429, 503)


def fetch_with_retry(url, headers=None, max_retries=3, backoff_base=2, timeout=30):
    """Fetch URL with exponential backoff on rate limits / transient errors."""
    headers = headers or {"User-Agent": "Mozilla/5.0"}
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if is_rate_limited(e.code):
                sleep = backoff_base ** attempt
                print(f"[retry] {url} rate-limited ({e.code}); backing off {sleep}s")
                time.sleep(sleep)
                continue
            if e.code in (403, 405):
                # Do not retry method/auth errors; escalate instead
                raise
            # Retry 5xx
            if 500 <= e.code < 600:
                sleep = backoff_base ** attempt
                print(f"[retry] {url} server error {e.code}; backing off {sleep}s")
                time.sleep(sleep)
                continue
            raise
        except urllib.error.URLError as e:
            last_err = e
            sleep = backoff_base ** attempt
            print(f"[retry] {url} network error; backing off {sleep}s")
            time.sleep(sleep)
    raise last_err
