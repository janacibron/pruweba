class ExplainabilityEngine:
    def explain(s,decision):return f'Decision: {decision.get("governance_decision","?")}. Risk: {decision.get("risk_level","?")}. Confidence: {decision.get("confidence","?")}. Reasoning: {decision.get("reasoning","none provided")}.'
    def plain(s,decision):d=decision;return f'The system says {d.get("governance_decision","?")} because {d.get("reasoning","no reason given")}. Risk is {d.get("risk_level","?")}. I am {float(d.get("confidence",0))*100:.0f}% confident.'
print('[XXV] Explainability Engine: ready')
