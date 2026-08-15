# PILLAR XVIII: KNOWLEDGE DISTILLER
import json,collections
class KnowledgeDistiller:
    def __init__(s):s.patterns=collections.Counter();s.templates=[]
    def ingest(s,audit_log):[s.patterns.update([e.get('action','?')])for e in audit_log]
    def extract_rules(s):return[{'pattern':p,'count':c,'frequency':c/sum(s.patterns.values())}for p,c in s.patterns.most_common(5)]
    def generate_template(s,name,from_patterns):t={'name':name,'rules':[f'rule_{p}'for p,_ in from_patterns[:3]],'generated_from':len(from_patterns)};s.templates.append(t);return t
print('[XVIII] Knowledge Distiller: ready')
