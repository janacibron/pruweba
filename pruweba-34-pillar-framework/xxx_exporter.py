import json,time
class UniversalExporter:
    def __init__(s):s.exports=[]
    def to_json(s,decision):return json.dumps(decision,indent=2)
    def to_markdown(s,decision):d=decision;return f'## Governance Decision\n\n| Field | Value |\n|-------|-------|\n| Decision | {d.get("governance_decision","?")} |\n| Risk | {d.get("risk_level","?")} |\n| Confidence | {d.get("confidence","?")} |\n\n**Reasoning:** {d.get("reasoning","")}\n'
    def to_slack(s,decision):d=decision;return f':white_check_mark: *{d.get("governance_decision","?")}* | Risk: {d.get("risk_level","?")} | Confidence: {float(d.get("confidence",0))*100:.0f}%\n>{d.get("reasoning","")[:200]}'
    def to_github_status(s,decision):d=decision;return{"state":"success"if d.get("governance_decision")=="APPROVE_DEPLOY"else"failure","description":d.get("reasoning","")[:140],"context":"ground-truth/governance"}
    def export(s,decision,formats=["json"]):r={};r["json"]=s.to_json(decision)if"json"in formats else None;r["markdown"]=s.to_markdown(decision)if"markdown"in formats else None;r["slack"]=s.to_slack(decision)if"slack"in formats else None;r["github"]=s.to_github_status(decision)if"github"in formats else None;s.exports.append({"ts":time.time(),"formats":formats});return r
print('[XXX] Universal Exporter: ready')
