import json, os, time
from datetime import datetime

LEDGER = r'C:\Users\Jan\Documents\AOP\olj_scraper\ledger.json'

def load():
    if os.path.exists(LEDGER):
        return json.load(open(LEDGER))
    return {'applications': [], 'stats': {'total': 0, 'sent': 0, 'responses': 0, 'interviews': 0}}

def add(job, application_file):
    ledger = load()
    entry = {
        'title': job['title'],
        'link': job['link'],
        'score': job['score'],
        'application_file': application_file,
        'status': 'generated',
        'generated_at': datetime.utcnow().isoformat(),
        'applied_at': None,
        'response': None
    }
    ledger['applications'].append(entry)
    ledger['stats']['total'] = len(ledger['applications'])
    json.dump(ledger, open(LEDGER, 'w'), indent=2)
    return entry

# Track all 9 generated applications
import glob
for f in glob.glob(r'C:\Users\Jan\Documents\AOP\olj_scraper\applications\*.txt'):
    # Parse score and title from filename
    fname = os.path.basename(f)
    score = int(fname.split('_')[0])
    title = fname.replace('.txt', '').replace(str(score) + '_', '').replace('_', ' ')
    add({'title': title, 'link': '', 'score': score}, fname)

ledger = load()
print('Ledger: ' + str(ledger['stats']['total']) + ' applications tracked')
for a in ledger['applications']:
    print('  [' + str(a['score']) + '] ' + a['title'][:50] + ' - ' + a['status'])
