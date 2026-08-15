import collections
class BiasDetector:
    def __init__(s,w=100):s.decisions=[];s.window=w
    def observe(s,decision):s.decisions.append(decision);s.decisions=s.decisions[-s.window:]
    def detect(s):c=collections.Counter(d.get("governance_decision","?")for d in s.decisions);total=sum(c.values());return{"distribution":{k:v/total for k,v in c.items()},"drift":max(c.values())/total>0.9 if total>10 else False,"alert":"Bias detected"if total>10 and max(c.values())/total>0.9 else"Nominal"}
print('[XXVI] Bias Detector: ready')
