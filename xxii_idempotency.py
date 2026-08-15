import hashlib,time
class IdempotencyGuard:
    def __init__(s):s.seen={};s.ttl=3600
    def check(s,evidence):h=hashlib.sha256(str(evidence).encode()).hexdigest();now=time.time();s.seen={k:v for k,v in s.seen.items()if now-v<3600};return h not in s.seen,lambda:s.seen.update({h:now})if h not in s.seen else None
print('[XXII] Idempotency Guard: ready')
