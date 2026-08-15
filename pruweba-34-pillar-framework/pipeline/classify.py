import subprocess, json, time, re, os

jobs = json.load(open(r'C:\Users\Jan\Documents\AOP\olj_scraper\ranked_jobs_full.json'))

def classify(job_title):
    prompt = 'Score this job for a Python automation engineer. Reply with ONLY a number 0-100: ' + job_title
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:3b', prompt],
            capture_output=True, text=True, timeout=30,
            encoding='utf-8', errors='ignore'
        )
        numbers = re.findall(r'\d+', result.stdout)
        if numbers:
            score = int(numbers[0])
            return min(max(score, 0), 100)
    except Exception as e:
        print('  ERR: ' + str(e)[:100])
    return 50

results = []
for i, job in enumerate(jobs):
    title = job['title']
    print('[' + str(i+1) + '/14] ' + title[:50])
    s = classify(title)
    job['score'] = s
    job['apply'] = s >= 70
    results.append(job)
    print('  Score: ' + str(s))
    time.sleep(1)

out = r'C:\Users\Jan\Documents\AOP\olj_scraper\classified_jobs.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

ranked = sorted(results, key=lambda x: -x['score'])
print('\nTOP MATCHES:')
for j in ranked[:7]:
    print('  [' + str(j['score']) + '] ' + j['title'])
