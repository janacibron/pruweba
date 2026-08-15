import json, subprocess, os, time, re

BASE_PROFILE = '''Jan Michael Acibron ? Governance Systems Architect | AI Automation Engineer
acibronjan@gmail.com | Philippines | US hours | pruweba.com/#pillars
Built: 34-pillar governance framework, autonomous pipelines, research engine, LLM bridge, client onboarding. Skills: Python, JavaScript, SQL, REST APIs, Webhooks, GoHighLevel, Zapier, Make, n8n, Claude, ChatGPT, Ollama.'''

def clean(text):
    text = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', text)
    text = re.sub(r'\[[0-9]+[A-Z]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

jobs = json.load(open(r'C:\Users\Jan\Documents\AOP\olj_scraper\classified_jobs.json'))
top = [j for j in jobs if j.get('score', 0) >= 80]
top.sort(key=lambda x: -x['score'])

def generate(job):
    prompt = f'''{BASE_PROFILE}

Write a job application for this role:
Job: {job["title"]}
Description: {job.get("description", "")[:500]}

Rules:
- Start with a strong hook about building verified systems
- Match the job tone
- Lead with proof, not introduction
- No generic language
- Plain text, max 250 words
- End with: Jan Michael Acibron, acibronjan@gmail.com'''
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral:7b', prompt],
            capture_output=True, text=True, timeout=180, encoding='utf-8', errors='ignore'
        )
        return clean(result.stdout)
    except Exception as e:
        return 'Generation failed: ' + str(e)

for i, job in enumerate(top):
    print('[' + str(i+1) + '/9] ' + job['title'][:50])
    app = generate(job)
    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', job['title'][:40])
    fname = str(job['score']) + '_' + safe + '.txt'
    fpath = os.path.join(r'C:\Users\Jan\Documents\AOP\olj_scraper\applications', fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write('JOB: ' + job['title'] + '\n')
        f.write('LINK: ' + job['link'] + '\n')
        f.write('SCORE: ' + str(job['score']) + '\n')
        f.write('='*50 + '\n\n')
        f.write(app)
    print('  Saved: ' + fname)
    time.sleep(2)

print('\n[DONE] 9 applications regenerated with Mistral')
