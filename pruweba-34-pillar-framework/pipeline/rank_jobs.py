import json
jobs = json.load(open('olj_automation.json'))
priority_words = ['automation', 'ai', 'systems', 'integration', 'gohighlevel', 'ghl', 'n8n', 'zapier', 'backend', 'workflow', 'rpa', 'technical']
ranked = []
for j in jobs:
    title = j['title'].lower()
    score = sum(1 for w in priority_words if w in title)
    if score >= 2:
        ranked.append((score, j))
ranked.sort(key=lambda x: -x[0])
print('Top matches: ' + str(len(ranked)))
for score, j in ranked:
    print('[' + str(score) + '] ' + j['title'])
    print('     ' + j['link'])
