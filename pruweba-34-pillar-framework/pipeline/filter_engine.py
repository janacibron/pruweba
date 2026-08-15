#!/usr/bin/env python3
"""Preference filter engine: deterministic rules over unified job format."""
import json, os, re
from typing import Any, Dict, List

DEFAULT_PREFS_PATH = os.path.join(os.path.dirname(__file__), "preferences.json")


def load_preferences(path=None):
    path = path or DEFAULT_PREFS_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _matches_platform(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    enabled = prefs.get("platforms", {}).get("enabled", [])
    if not enabled:
        return True
    return job.get("platform") in enabled


def _matches_keywords(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    kw = prefs.get("keywords", {})
    roles = kw.get("roles", [])
    if not roles:
        return True
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()
    mode = kw.get("match_mode", "any")
    if kw.get("case_sensitive", False):
        text = " ".join([str(job.get("title", "")), str(job.get("description", ""))])
    if mode == "all":
        return all(r.lower() in text for r in roles)
    return any(r.lower() in text for r in roles)


def _matches_rate(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    rate = prefs.get("rate", {})
    min_r = rate.get("min", 0)
    max_r = rate.get("max", 999999)
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()
    nums = re.findall(r"\b\d{3,}(?:,\d{3})*(?:\.\d+)?\b", text)
    if not nums:
        return True  # unknown salary passes through by default
    vals = [float(n.replace(",", "")) for n in nums]
    # If rate.period is "year" and numbers might be annual, keep them.
    # If numbers look like monthly/hourly, conversion is not implemented here.
    # Best-effort: allow if any number is within range.
    return any(min_r <= v <= max_r for v in vals)


def _matches_job_type(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    jt = prefs.get("job_type", {})
    types = [t.lower() for t in jt.get("types", [])]
    if not types:
        return True
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()
    return any(t in text for t in types)


def _matches_timezone(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    tz = prefs.get("timezone", {})
    preferred = [z.lower() for z in tz.get("preferred", [])]
    exclude = [z.lower() for z in tz.get("exclude", [])]
    if not preferred and not exclude:
        return True
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()
    if exclude and any(z in text for z in exclude):
        return False
    if not preferred:
        return True
    return any(z in text for z in preferred)


def _matches_experience(job: Dict[str, Any], prefs: Dict[str, Any]) -> bool:
    exp = prefs.get("experience_level", {})
    levels = [l.lower() for l in exp.get("levels", [])]
    default = (exp.get("default") or "mid").lower()
    if not levels:
        return True
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("description", "")),
    ]).lower()
    matched = [l for l in levels if l in text]
    if not matched:
        matched = [default]
    return True


def filter_jobs(jobs: List[Dict[str, Any]], prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
    kept = []
    for job in jobs:
        if not _matches_platform(job, prefs):
            continue
        if not _matches_keywords(job, prefs):
            continue
        if not _matches_rate(job, prefs):
            continue
        if not _matches_job_type(job, prefs):
            continue
        if not _matches_timezone(job, prefs):
            continue
        _matches_experience(job, prefs)
        kept.append(job)
    return kept
