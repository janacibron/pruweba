#!/usr/bin/env python3
"""Blocked platforms manager with monthly retry logic."""
import json, os, time
from datetime import datetime, timezone

from blocker_handler import add_blocked, load_blocked, should_retry_blocked

BLOCKED_FILE = os.path.join(os.path.dirname(__file__), "blocked_platforms.json")


def register_if_blocked(platform, reason, retry_days=30):
    now = datetime.now(timezone.utc).isoformat()
    data = load_blocked()
    entry = data.get(platform)
    if entry and entry.get("reason") == reason:
        print(f"[blocked] {platform} already blocked for same reason")
        return False
    add_blocked(platform, reason, last_checked=now, next_check_days=retry_days)
    print(f"[blocked] Registered {platform}: {reason}")
    return True


def try_retry_blocked(platform, scraper_func):
    if not should_retry_blocked(platform):
        print(f"[blocked] {platform} in cooldown, skipping retry")
        return []
    print(f"[blocked] Retry window open for {platform}")
    try:
        result = scraper_func()
        if isinstance(result, tuple) and len(result) == 2:
            jobs, status = result
        else:
            jobs = result
            status = "ok"
        if jobs and status == "ok":
            print(f"[blocked] {platform} recovered: {len(jobs)} jobs")
            clear_blocked(platform)
            return jobs
    except Exception as e:
        print(f"[blocked] {platform} still blocked: {e}")
        now = datetime.now(timezone.utc).isoformat()
        add_blocked(platform, str(e), last_checked=now, next_check_days=30)
    return []


def clear_blocked(platform):
    data = load_blocked()
    if platform in data:
        del data[platform]
        with open(BLOCKED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[blocked] Cleared {platform}")


if __name__ == "__main__":
    # Example usage
    platforms = ["workingnomads", "virtualstaff"]
    for p in platforms:
        register_if_blocked(p, "http_405_or_403")
