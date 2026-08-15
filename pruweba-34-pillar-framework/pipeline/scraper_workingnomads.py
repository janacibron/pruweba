#!/usr/bin/env python3
"""Working Nomads jobs feed scraper - no login required.

Note: The site currently blocks direct non-browser access to `/jobsapi/home`
(405 on GET, 403 on POST) and does not expose a public RSS/Atom feed under
common paths. This scraper preserves the interface so the orchestrator can
continue, but currently returns 0 jobs with a documented blocker.
"""
import json, os, re, time, urllib.request, urllib.error

URL = "https://www.workingnomads.com/jobsapi/home"
OUT = os.path.join(os.path.dirname(__file__), "all_jobs.json")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse(text):
    jobs = []
    # Best-effort: parse RSS-like items if present
    if "<item>" in text:
        items = re.split(r"(?=<item>)", text)
        for item in items:
            title_m = re.search(r"<title>(.*?)</title>", item, re.S)
            link_m = re.search(r"<link>(.*?)</link>", item, re.S)
            pub_m = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
            desc_m = re.search(r"<description>(.*?)</description>", item, re.S)
            if title_m and link_m:
                title = re.sub(r"<.*?>", "", title_m.group(1)).strip()
                link = link_m.group(1).strip()
                posted = pub_m.group(1).strip() if pub_m else None
                desc = re.sub(r"<.*?>", " ", desc_m.group(1)).strip() if desc_m else ""
                jobs.append({
                    "title": title,
                    "link": link,
                    "platform": "workingnomads",
                    "posted_date": posted,
                    "description": desc[:500],
                })
        return jobs

    # Fallback: try to extract JSON data embedded in page text
    m = re.search(r"(\[.*?\])", text, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            for row in data:
                title = row.get("title") or row.get("job_title") or ""
                link = row.get("url") or row.get("link") or ""
                if title and link:
                    jobs.append({
                        "title": title,
                        "link": link,
                        "platform": "workingnomads",
                        "posted_date": row.get("pub_date") or row.get("posted_at") or None,
                        "description": (row.get("description") or row.get("text") or "")[:500],
                    })
        except Exception:
            pass
    return jobs


def scrape():
    print("[workingnomads] Fetching...")
    try:
        text = fetch()
        jobs = parse(text)
        status = "ok" if jobs else "empty"
        print(f"[workingnomads] Parsed {len(jobs)} jobs")
        return jobs, status
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        print(f"[workingnomads][BLOCKER] {e.code} {e.reason}: {body}")
        return [], f"http_{e.code}"
    except Exception as e:
        print(f"[workingnomads][ERR] {e}")
        return [], "error"


if __name__ == "__main__":
    jobs, status = scrape()
    out = os.path.join(os.path.dirname(__file__), "workingnomads.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"status": status, "jobs": jobs}, f, indent=2, ensure_ascii=False)
    print(f"[workingnomads] {status}: {len(jobs)} jobs -> {out}")
