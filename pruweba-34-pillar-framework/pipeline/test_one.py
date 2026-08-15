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
job = [j for j in jobs if j.get('score', 0) >= 80][0]

prompt = f'''{BASE_PROFILE}

Write a job application for this role:
Job: {job["title"]}
Description: {job.get("description", "")[:500]}

Rules:
- Start with a strong hook about building verified systems
- Match the job tone
- Lead with proof, not introduction
- No generic language like "I would like to introduce myself"
- No repetition
- Plain text, max 250 words
- End with: Jan Michael Acibron, acibronjan@gmail.com'''

result = subprocess.run(
    ['ollama', 'run', 'llama3.2:3b', prompt],
    capture_output=True, text=True, timeout=120, encoding='utf-8', errors='ignore'
)

app = clean(result.stdout)
print(app)
