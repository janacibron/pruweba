#!/usr/bin/env python3
"""RemoteOK jobs scraper - no login required."""
import json, os, re, time, urllib.request

URL = "https://remoteok.com/remote-jobs.json"
OUT = os.path.join(os.path.dirname(__file__), "all_jobs.json")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse(text):
    jobs = []
    try:
        data = json.loads(text)
    except Exception:
        return jobs
    if not isinstance(data, list):
        return jobs
    for row in data:
        if not isinstance(row, dict):
            continue
        if row.get("legal") is not None or not row.get("id"):
            continue
        title = (row.get("position") or "").strip()
        link = (row.get("apply_url") or row.get("url") or "").strip()
        if not title or not link:
            continue
        posted = row.get("date") or row.get("epoch")
        desc = (row.get("description") or "").strip()
        if row.get("tags"):
            tags = ", ".join(row["tags"]) if isinstance(row["tags"], list) else str(row["tags"])
            desc = (tags + "\n" + desc).strip()
        jobs.append({
            "title": title,
            "link": link,
            "platform": "remoteok",
            "posted_date": str(posted) if posted is not None else None,
            "description": desc[:500],
        })
    return jobs


def scrape():
    print("[remoteok] Fetching...")
    try:
        text = fetch()
        jobs = parse(text)
        print(f"[remoteok] Parsed {len(jobs)} jobs")
        return jobs
    except urllib.error.HTTPError as e:
        print(f"[remoteok][BLOCKER] {e.code} {e.reason}")
        return []
    except Exception as e:
        print(f"[remoteok][ERR] {e}")
        return []


if __name__ == "__main__":
    jobs = scrape()
    out = os.path.join(os.path.dirname(__file__), "remoteok.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"[remoteok] Saved {len(jobs)} jobs -> {out}")
