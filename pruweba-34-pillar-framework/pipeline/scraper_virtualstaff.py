#!/usr/bin/env python3
"""VirtualStaff.ph scraper with cookie persistence and blocker detection."""
import json, os, re, time, urllib.request

from cookie_manager import build_cookie_header, load_cookies, save_cookies
from blocker_handler import is_captcha, fetch_with_retry

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "virtualstaff_cookies.json")
JOBS_URL = "https://www.virtualstaff.ph/jobs"


def scrape():
    jobs = []
    cookies = load_cookies(COOKIES_FILE)
    cookie_header = "; ".join(f"{c.name}={c.value}" for c in cookies)

    try:
        status, body = fetch_with_retry(JOBS_URL, headers={
            "User-Agent": "Mozilla/5.0",
            "Cookie": cookie_header,
        }, max_retries=2)
        text = body.decode("utf-8", errors="replace")

        if is_captcha(text):
            print("[virtualstaff][CAPTCHA] Manual review required")
            return jobs, "captcha"

        if status == 200:
            # VirtualStaff is a JS-rendered Next.js app; static HTML may not contain jobs.
            # Best-effort regex extraction if present.
            titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', text, re.S)
            for t in titles:
                clean = re.sub(r"<.*?>", "", t).strip()
                if clean and len(clean) > 5:
                    jobs.append({
                        "title": clean,
                        "link": JOBS_URL,
                        "platform": "virtualstaff",
                        "posted_date": None,
                        "description": "",
                    })
        status = "ok" if jobs else "js_render_required"
    except urllib.error.HTTPError as e:
        print(f"[virtualstaff][BLOCKED] HTTP {e.code}: {e.reason}")
        return jobs, f"http_{e.code}"
    except Exception as e:
        print(f"[virtualstaff][ERR] {e}")
        return jobs, str(e)

    return jobs, status


if __name__ == "__main__":
    jobs, status = scrape()
    out = os.path.join(os.path.dirname(__file__), "virtualstaff_jobs.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"status": status, "jobs": jobs}, f, indent=2, ensure_ascii=False)
    print(f"[virtualstaff] {status}: {len(jobs)} jobs -> {out}")
