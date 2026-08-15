# PILLAR XVII: GRACEFUL DEGRADER
import time
class GracefulDegrader:
    def __init__(s):s.circuits={};s.fallback={};s.state='full'
    def add_circuit(s,name,check_fn,fallback_fn):s.circuits[name]=check_fn;s.fallback[name]=fallback_fn
    def check(s):failed=[n for n,f in s.circuits.items()if not f()];s.state='degraded'if failed else'full';return{'state':s.state,'failed_circuits':failed,'active_fallbacks':[s.fallback[n]()for n in failed]}
    def safe_execute(s,fn,fallback):return fn()if s.state=='full'else fallback()
print('[XVII] Graceful Degrader: ready')
