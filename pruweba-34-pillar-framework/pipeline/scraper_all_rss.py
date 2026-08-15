#!/usr/bin/env python3
"""Run all job scrapers, apply preferences, and save unified output."""
import importlib, json, os, time

BASE = os.path.dirname(__file__)
OUT = os.path.join(BASE, "all_jobs.json")
FILTERED_OUT = os.path.join(BASE, "filtered_jobs.json")

SCRAPERS = [
    ("onlinejobs", "scraper"),
    ("weworkremotely", "scraper_weworkremotely"),
    ("remotive", "scraper_remotive"),
    ("remoteok", "scraper_remoteok"),
    ("workingnomads", "scraper_workingnomads"),
    ("virtualstaff", "scraper_virtualstaff"),
]

from blocked_platforms import try_retry_blocked, load_blocked
from filter_engine import load_preferences, filter_jobs
from tier_engine import classify_tiers

all_jobs = []

for platform, module_name in SCRAPERS:
    try:
        mod = importlib.import_module(module_name)

        def _scrape(module=mod):
            return module.scrape()

        blocked_data = load_blocked()
        if platform in blocked_data:
            jobs = try_retry_blocked(platform, _scrape)
        else:
            result = _scrape()
            if isinstance(result, tuple) and len(result) == 2:
                jobs, status = result
                if status != "ok" and not jobs:
                    from blocker_handler import add_blocked
                    add_blocked(platform, f"scrape_failed:{status}")
            else:
                jobs = result

        if isinstance(jobs, list):
            print(f"[ALL] {platform}: {len(jobs)} jobs")
            all_jobs.extend(jobs)
        else:
            print(f"[ALL] {platform}: unexpected jobs type {type(jobs).__name__}")
        time.sleep(1)
    except Exception as e:
        print(f"[ALL][ERR] {platform}: {e}")

# Deduplicate by link
seen = set()
uniq = []
for j in all_jobs:
    if j["link"] not in seen:
        seen.add(j["link"])
        uniq.append(j)

prefs = load_preferences()
filtered = filter_jobs(uniq, prefs)
classified = classify_tiers(uniq, prefs)
free_jobs = [j for j in classified if j.get("tier") == "free"]
premium_jobs = [j for j in classified if j.get("tier") == "premium"]

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(classified, f, indent=2, ensure_ascii=False)

with open(FILTERED_OUT, "w", encoding="utf-8") as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open(os.path.join(BASE, "free_jobs.json"), "w", encoding="utf-8") as f:
    json.dump(free_jobs, f, indent=2, ensure_ascii=False)

with open(os.path.join(BASE, "premium_jobs.json"), "w", encoding="utf-8") as f:
    json.dump(premium_jobs, f, indent=2, ensure_ascii=False)

print(f"[ALL] Saved {len(classified)} tier-classified jobs -> {OUT}")
print(f"[ALL] Saved {len(filtered)} filtered jobs -> {FILTERED_OUT}")
print(f"[ALL] Saved {len(free_jobs)} free jobs -> free_jobs.json")
print(f"[ALL] Saved {len(premium_jobs)} premium jobs -> premium_jobs.json")
