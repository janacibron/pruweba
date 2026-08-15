import requests, json, re, time, os

jobs = json.load(open('olj_automation.json'))
priority_words = ['automation', 'ai', 'systems', 'integration', 'gohighlevel', 'ghl', 'n8n', 'zapier', 'backend', 'workflow', 'rpa', 'technical']
ranked = []
for j in jobs:
    title = j['title'].lower()
    score = sum(1 for w in priority_words if w in title)
    if score >= 2:
        ranked.append(j)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

fetched = []
for i, job in enumerate(ranked):
    try:
        resp = requests.get(job['link'], headers=headers, timeout=30)
        print(f'[{i+1}/{len(ranked)}] {resp.status_code} - {job["title"]}')
        if resp.status_code == 200:
            text = resp.text
            # Extract the job description - look for common containers
            desc_match = re.search(r'(?s)(JOB OVERVIEW|Job Description|About the Role|Role Description)(.*?)(SKILL|ABOUT|REQUIREMENTS|APPLY)', text)
            description = desc_match.group(0)[:5000] if desc_match else text[:5000]
            job['description'] = description
            fetched.append(job)
        time.sleep(2)
    except Exception as e:
        print(f'[ERR] {job["title"]}: {e}')

out = os.path.join(os.path.dirname(__file__), 'ranked_jobs_full.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(fetched, f, indent=2)
print(f'\n[SAVED] {len(fetched)} full descriptions -> {out}')
