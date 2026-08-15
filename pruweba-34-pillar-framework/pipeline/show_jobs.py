import json
jobs = json.load(open('olj_automation.json'))
for j in jobs:
    print(j['title'])
    print('  ' + j['link'])
    print()
