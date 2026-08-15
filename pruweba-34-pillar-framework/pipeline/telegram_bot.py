# Telegram Bot for Job Pipeline
# Save as: telegram_bot.py
# Run: python telegram_bot.py

import json, os, time, subprocess
import urllib.request

TOKEN = '8625372758:AAHw9k1X_t-ZmNGSbxiRUffTcb8K5j0ehDw'
API = f'https://api.telegram.org/bot{TOKEN}'
PREFS_FILE = 'user_preferences.json'

def send_message(chat_id, text):
    data = json.dumps({'chat_id': chat_id, 'text': text}).encode()
    req = urllib.request.Request(
        f'{API}/sendMessage',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)

def get_updates(offset=None):
    url = f'{API}/getUpdates'
    if offset:
        url += f'?offset={offset}'
    data = json.loads(urllib.request.urlopen(url).read())
    return data.get('result', [])

def load_prefs():
    if os.path.exists(PREFS_FILE):
        return json.load(open(PREFS_FILE))
    return {}

def save_prefs(prefs):
    json.dump(prefs, open(PREFS_FILE, 'w'), indent=2)

def handle_message(chat_id, text):
    prefs = load_prefs()
    user_id = str(chat_id)
    
    if text == '/start':
        send_message(chat_id, 'Hi! I find jobs and write applications for you.\n\nWhat role are you looking for?')
        prefs[user_id] = {'step': 'role'}
        save_prefs(prefs)
    
    elif text == '/help':
        send_message(chat_id, '/jobs - show matching jobs\n/preferences - view your settings')
    
    elif text == '/jobs':
        role = prefs.get(user_id, {}).get('role', 'automation')
        result = subprocess.run(['python', 'scraper.py', role, '1'], capture_output=True, text=True)
        jobs_file = f'olj_{role}.json'
        if os.path.exists(jobs_file):
            jobs = json.load(open(jobs_file))[:5]
            msg = 'Top matching jobs:\n\n'
            for i, job in enumerate(jobs, 1):
                msg += f'{i}. {job["title"]}\n   {job["link"]}\n\n'
            send_message(chat_id, msg)
        else:
            send_message(chat_id, 'No jobs found yet.')
    
    elif text == '/preferences':
        p = prefs.get(user_id, {})
        msg = f'Role: {p.get("role", "not set")}\nRate: {p.get("rate", "not set")}\nType: {p.get("type", "not set")}'
        send_message(chat_id, msg)
    
    else:
        user_prefs = prefs.get(user_id, {})
        step = user_prefs.get('step', '')
        
        if step == 'role':
            user_prefs['role'] = text
            user_prefs['step'] = 'rate'
            save_prefs(prefs)
            send_message(chat_id, 'What salary range do you expect?')
        
        elif step == 'rate':
            user_prefs['rate'] = text
            user_prefs['step'] = 'type'
            save_prefs(prefs)
            send_message(chat_id, 'Full-time or part-time?')
        
        elif step == 'type':
            user_prefs['type'] = text
            user_prefs['step'] = 'done'
            prefs[user_id] = user_prefs
            save_prefs(prefs)
            send_message(chat_id, 'Got it! Type /jobs to see matches.')
        
        else:
            send_message(chat_id, 'Type /help for commands.')

offset = 0
while True:
    try:
        updates = get_updates(offset)
        for update in updates:
            offset = update['update_id'] + 1
            message = update.get('message')
            if message:
                chat_id = message['chat']['id']
                text = message.get('text', '')
                handle_message(chat_id, text)
        time.sleep(2)
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(5)