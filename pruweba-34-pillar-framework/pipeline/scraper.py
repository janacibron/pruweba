#!/usr/bin/env python3
"""OnlineJobs.ph Scraper with cookie persistence and session refresh."""
import json, os, re, time, urllib.request

from cookie_manager import build_cookie_header, load_cookies, save_cookies
from blocker_handler import fetch_with_retry, is_captcha

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "olj_cookies.json")
BASE = "https://www.onlinejobs.ph/jobseekers/jobsearch"


def scrape(keyword="automation", max_pages=3):
    jobs = []
    seen = set()
    cookies = load_cookies(COOKIES_FILE)
    cookie_header = "; ".join(f"{c.name}={c.value}" for c in cookies)

    for page in range(max_pages):
        offset = page * 30
        url = f"{BASE}/{offset}?jobkeyword={keyword}" if offset else f"{BASE}?jobkeyword={keyword}"
        try:
            status, body = fetch_with_retry(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Cookie": cookie_header,
            })
            text = body.decode("utf-8", errors="replace")

            if is_captcha(text):
                print("[olj][CAPTCHA] Manual review required")
                break

            print(f"[{status}] Page {page+1}: {keyword}")
            if status == 200:
                pattern = r'href="(/jobseekers/job/[^"]+)"'
                found = re.findall(pattern, text)
                for link in found:
                    if link not in seen:
                        seen.add(link)
                        job_id = re.search(r"(\d+)$", link)
                        title = re.sub(r"[-]+", " ", link.split("/")[-1].replace(job_id.group(1), "")).strip()
                        jobs.append({
                            "title": title,
                            "link": f"https://www.onlinejobs.ph{link}",
                            "platform": "onlinejobs",
                            "posted_date": None,
                            "description": "",
                        })
            time.sleep(2)
        except Exception as e:
            print(f"[olj][ERR] Page {page+1}: {e}")
    return jobs


if __name__ == "__main__":
    jobs = scrape()
    out = os.path.join(os.path.dirname(__file__), "olj_jobs.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"\n[olj] Saved {len(jobs)} jobs -> {out}")
