#!/usr/bin/env python3
"""Learning loop: track outcomes and recalibrate scoring."""
import json, os
from datetime import datetime, timezone
from collections import defaultdict

LEARNING_FILE = os.path.join(os.path.dirname(__file__), "learning_data.json")


def load_learning():
    if not os.path.exists(LEARNING_FILE):
        return {"outcomes": [], "platform_stats": {}, "last_updated": None}
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_learning(data):
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_outcome(job_link, outcome, platform=None, notes=None):
    data = load_learning()
    entry = {
        "job_link": job_link,
        "platform": platform,
        "outcome": outcome,
        "notes": notes or "",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    data["outcomes"].append(entry)
    save_learning(data)
    return entry


def recalculate_platform_stats():
    data = load_learning()
    stats = defaultdict(lambda: {"total": 0, "responses": 0, "interviews": 0, "offers": 0, "response_rate": 0.0, "interview_rate": 0.0, "offer_rate": 0.0})
    for o in data.get("outcomes", []):
        p = o.get("platform") or "unknown"
        stats[p]["total"] += 1
        outcome = o.get("outcome")
        if outcome == "response":
            stats[p]["responses"] += 1
        elif outcome == "interview":
            stats[p]["interviews"] += 1
            stats[p]["responses"] += 1
        elif outcome == "offer":
            stats[p]["offers"] += 1
            stats[p]["interviews"] += 1
            stats[p]["responses"] += 1
    for p, s in stats.items():
        if s["total"] > 0:
            s["response_rate"] = s["responses"] / s["total"]
            s["interview_rate"] = s["interviews"] / s["total"]
            s["offer_rate"] = s["offers"] / s["total"]
    data["platform_stats"] = dict(stats)
    save_learning(data)
    return data["platform_stats"]


def generate_learning_report():
    data = load_learning()
    stats = recalculate_platform_stats()
    report = {
        "total_outcomes": len(data.get("outcomes", [])),
        "platform_stats": stats,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return report
