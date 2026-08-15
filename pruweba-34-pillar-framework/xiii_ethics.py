# PILLAR XIII: ETHICS CONSTRAINT
class EthicsConstraint:
    def __init__(s):s.rules={};s.immutable=True
    def add(s,name,fn):s.rules[name]=fn
    def verify(s,state):fails=[n for n,f in s.rules.items()if not f(state)[0]];return len(fails)==0,fails
    def hardcoded(s):return{'no_untested_deploy':lambda s:s.get('tests_passed',0)==s.get('tests_total',1),'require_consent':lambda s:s.get('consent',False),'human_approval_critical':lambda s:not s.get('critical',False)or s.get('human_ok',False)}
print('[XIII] Ethics Constraint: ready')
