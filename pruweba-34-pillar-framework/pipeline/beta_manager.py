#!/usr/bin/env python3
"""Beta tester registry and feedback collector."""
import json, os
from datetime import datetime, timezone

TESTERS_FILE = os.path.join(os.path.dirname(__file__), "beta_testers.json")
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "beta_feedback.json")


def load_testers():
    if not os.path.exists(TESTERS_FILE):
        return {"testers": [], "config": {"max_testers": 10, "premium_duration_days": 14, "feedback_fields": ["bugs", "usage", "testimonials"]}}
    with open(TESTERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_testers(data):
    with open(TESTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_tester(name, email, tier="premium"):
    data = load_testers()
    testers = data.get("testers", [])
    if any(t.get("email") == email for t in testers):
        return {"status": "exists", "message": "Tester already registered"}
    if len(testers) >= data.get("config", {}).get("max_testers", 10):
        return {"status": "full", "message": "Beta slots full"}
    entry = {
        "name": name,
        "email": email,
        "tier": tier,
        "joined_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }
    testers.append(entry)
    data["testers"] = testers
    save_testers(data)
    return {"status": "added", "tester": entry}


def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_feedback(feedback):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)


def submit_feedback(email, bugs=None, usage=None, testimonials=None):
    data = load_testers()
    testers = data.get("testers", [])
    if not any(t.get("email") == email for t in testers):
        return {"status": "not_found", "message": "Tester not registered"}
    feedback = load_feedback()
    entry = {
        "email": email,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "bugs": bugs or [],
        "usage": usage or "",
        "testimonials": testimonials or "",
    }
    feedback.append(entry)
    save_feedback(feedback)
    return {"status": "submitted", "feedback": entry}
