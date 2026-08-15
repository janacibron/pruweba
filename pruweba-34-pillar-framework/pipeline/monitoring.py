#!/usr/bin/env python3
"""Health checks and dead letter queue for monitored pipeline."""
import json, os, time, urllib.request, urllib.error

BASE = os.path.dirname(__file__)
HEALTH_FILE = os.path.join(BASE, "health_checks.json")
DLQ_FILE = os.path.join(BASE, "dead_letter_queue.json")


def load_health():
    if not os.path.exists(HEALTH_FILE):
        return {"platforms": {}, "jobs_file": "all_jobs.json", "max_jobs": 2000, "check_interval_minutes": 60}
    with open(HEALTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_health(data):
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_dlq():
    if not os.path.exists(DLQ_FILE):
        return []
    with open(DLQ_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dlq(queue):
    with open(DLQ_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def send_to_dlq(item):
    queue = load_dlq()
    entry = dict(item)
    entry["queued_at"] = int(time.time())
    queue.append(entry)
    save_dlq(queue)
    return entry


def check_platform_health():
    config = load_health()
    platforms = config.get("platforms", {})
    results = {}
    for name, meta in platforms.items():
        url = meta.get("url")
        expected = meta.get("expected_status", 200)
        status = None
        ok = False
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                status = r.status
                ok = status == expected
        except urllib.error.HTTPError as e:
            status = e.code
            ok = e.code == expected
        except Exception:
            status = None
            ok = False
        results[name] = {
            "url": url,
            "status": status,
            "expected": expected,
            "healthy": ok,
            "checked_at": int(time.time()),
        }
    return results


def check_jobs_file():
    config = load_health()
    path = os.path.join(BASE, config.get("jobs_file", "all_jobs.json"))
    if not os.path.exists(path):
        return {"exists": False, "path": path}
    size = os.path.getsize(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data) if isinstance(data, list) else 0
    except Exception:
        count = None
    return {"exists": True, "path": path, "size_bytes": size, "job_count": count, "max_jobs": config.get("max_jobs")}


def run_health_checks():
    platform_health = check_platform_health()
    jobs_health = check_jobs_file()
    unhealthy = [p for p, m in platform_health.items() if not m.get("healthy")]
    report = {
        "platforms": platform_health,
        "jobs_file": jobs_health,
        "unhealthy_platforms": unhealthy,
        "overall_healthy": len(unhealthy) == 0 and jobs_health.get("exists") and (jobs_health.get("job_count") or 0) > 0,
        "checked_at": int(time.time()),
    }
    return report
