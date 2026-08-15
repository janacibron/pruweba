# PILLAR XV: CAPACITY PLANNER
import numpy as np,time
class CapacityPlanner:
    def __init__(s):s.metrics=[];s.thresholds={'cpu':80,'mem':80,'disk':90}
    def record(s,m):s.metrics.append({'t':time.time(),**m});s.metrics=s.metrics[-1000:]
    def forecast(s,hours=24):return{'current_load':s.metrics[-1]if s.metrics else{},'trend':'increasing'if len(s.metrics)>1 and s.metrics[-1].get('cpu',0)>s.metrics[0].get('cpu',0)else'stable','scale_trigger':any(s.metrics[-1].get(k,0)>v for k,v in s.thresholds.items())if s.metrics else False,'recommendation':'scale_up'if s.metrics and any(s.metrics[-1].get(k,0)>v for k,v in s.thresholds.items())else'adequate'}
print('[XV] Capacity Planner: ready')
