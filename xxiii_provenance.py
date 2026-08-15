import hashlib,time,os,socket
class ProvenanceTracker:
    def __init__(s):s.chain=[]
    def capture(s,evidence):e={"host":socket.gethostname(),"user":os.environ.get("USERNAME","?"),"cwd":os.getcwd(),"ts":time.time(),"evidence_hash":hashlib.sha256(str(evidence).encode()).hexdigest()};s.chain.append(e);return e
    def verify(s):return len(s.chain)>0 and all("host"in e for e in s.chain)
print('[XXIII] Provenance Tracker: ready')
