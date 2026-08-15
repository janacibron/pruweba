#!/usr/bin/env python3
"""We Work Remotely RSS scraper - no login required."""
import json, os, re, time, urllib.request


URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
OUT = os.path.join(os.path.dirname(__file__), "all_jobs.json")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse(text):
    jobs = []
    items = re.split(r"(?=<item>)", text)
    for item in items:
        title_m = re.search(r"<title>(.*?)</title>", item, re.S)
        link_m = re.search(r"<link>(.*?)</link>", item, re.S)
        if not title_m or not link_m:
            continue
        title = re.sub(r"<.*?>", "", title_m.group(1)).strip()
        link = link_m.group(1).strip()
        # Skip channel metadata: title equals channel page and link equals feed URL
        channel_title = "We Work Remotely: Remote jobs in design, programming, marketing and more"
        channel_link = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        if title == channel_title and link == channel_link:
            continue
        pub_m = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
        desc_m = re.search(r"<description>(.*?)</description>", item, re.S)
        posted = pub_m.group(1).strip() if pub_m else None
        desc = re.sub(r"<.*?>", " ", desc_m.group(1)).strip() if desc_m else ""
        jobs.append({
            "title": title,
            "link": link,
            "platform": "weworkremotely",
            "posted_date": posted,
            "description": desc[:500],
        })
    return jobs


def scrape():
    print("[weworkremotely] Fetching...")
    try:
        text = fetch()
        jobs = parse(text)
        print(f"[weworkremotely] Parsed {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"[weworkremotely][ERR] {e}")
        return []


if __name__ == "__main__":
    jobs = scrape()
    out = os.path.join(os.path.dirname(__file__), "weworkremotely.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"[weworkremotely] Saved {len(jobs)} jobs -> {out}")
