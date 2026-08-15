class RedundancyPlanner:
    def __init__(s):s.pillars={};s.failovers={}
    def register(s,name,primary,backup):s.pillars[name]={'primary':primary,'backup':backup,'active':'primary'}
    def failover(s,name):
        if name in s.pillars:
            s.pillars[name]['active']='backup'
        return s.pillars.get(name)
    def status(s):return{n:p['active']for n,p in s.pillars.items()}
print('[XXVII] Redundancy Planner: ready')
