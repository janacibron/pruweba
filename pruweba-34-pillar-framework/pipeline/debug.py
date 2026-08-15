import requests, re, json

r = requests.get('https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=automation', headers={'User-Agent': 'Mozilla/5.0'})
text = r.text
open('olj_page.html', 'w', encoding='utf-8').write(text)
print(f'Saved {len(text)} bytes')

count_match = re.search(r'search_result_count[^0-9]+(\d+)', text)
print(f'Search result count: {count_match.group(1) if count_match else "not found"}')

# Find all hrefs that look like job links
hrefs = re.findall(r'href="([^"]+)"', text)
jobish = [h for h in hrefs if any(k in h.lower() for k in ['job', 'detail', 'post', 'position'])]
print(f'Job-like hrefs: {len(jobish)}')
for h in jobish[:20]:
    print(f'  {h}')
