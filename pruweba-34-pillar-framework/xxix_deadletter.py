import json,time
class DeadLetterHandler:
    def __init__(s):s.dead=[];s.retry_max=3
    def handle(s,evidence,error):s.dead.append({"evidence":str(evidence)[:500],"error":str(error),"ts":time.time(),"retries":0});return len(s.dead)
    def retry(s,idx,processor):e=s.dead[idx];e["retries"]+=1;return processor(json.loads(e["evidence"]))if e["retries"]<=s.retry_max else"PERMANENT_FAILURE"
    def pending(s):return len([d for d in s.dead if d["retries"]<s.retry_max])
print('[XXIX] Dead Letter Handler: ready')
