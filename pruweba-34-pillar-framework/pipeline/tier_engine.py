#!/usr/bin/env python3
"""Tier classification engine: free vs premium access rules."""
import json, os, re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from filter_engine import load_preferences


def _parse_posted_date(value):
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    try:
        return parsedate_to_datetime(value)
    except Exception:
        return None


def _job_age_days(job):
    posted = job.get("posted_date")
    dt = _parse_posted_date(posted)
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    return max((now - dt).total_seconds() / 86400.0, 0.0)


def _matches_tier(job, prefs):
    tier = prefs.get("tier", {})
    mode = tier.get("mode", "free")
    if mode == "premium":
        job["tier"] = "premium"
        job["tier_reason"] = "premium_mode"
        return True
    age = _job_age_days(job)
    if age is None:
        job["tier"] = "free"
        job["tier_reason"] = "unknown_age"
        return True
    min_age = tier.get("free", {}).get("min_age_days", 7)
    if age >= min_age:
        job["tier"] = "free"
        job["tier_reason"] = f"age_{age:.1f}_days"
        return True
    job["tier"] = "premium"
    job["tier_reason"] = f"age_{age:.1f}_days"
    return False


def classify_tiers(jobs, prefs=None, path=None):
    prefs = prefs or load_preferences(path)
    tier_prefs = prefs.get("tier", {})
    mode = tier_prefs.get("mode", "free")
    free_min_age = tier_prefs.get("free", {}).get("min_age_days", 7)
    results = []
    for job in jobs:
        job = dict(job)
        if mode == "premium":
            job["tier"] = "premium"
            job["tier_reason"] = "premium_mode"
            results.append(job)
            continue
        age = _job_age_days(job)
        if age is None:
            job["tier"] = "free"
            job["tier_reason"] = "unknown_age"
            results.append(job)
            continue
        if age >= free_min_age:
            job["tier"] = "free"
            job["tier_reason"] = f"age_{age:.1f}_days"
        else:
            job["tier"] = "premium"
            job["tier_reason"] = f"age_{age:.1f}_days"
        results.append(job)
    return results


def get_free_jobs(jobs, prefs=None, path=None):
    classified = classify_tiers(jobs, prefs, path)
    return [j for j in classified if j.get("tier") == "free"]


def get_premium_jobs(jobs, prefs=None, path=None):
    classified = classify_tiers(jobs, prefs, path)
    return [j for j in classified if j.get("tier") == "premium"]
