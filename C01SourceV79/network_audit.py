"""Measure physical duct connectivity; zone/door adjacency is deliberately ignored."""
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def audit(data):
    ducts=[p for p in data['placements'] if p['id'].startswith('V79_VENT_')]
    nodes=defaultdict(set)
    for p in ducts:
        if p['model']!='P_Vent_3m' or p['yaw']!=0:raise ValueError('Unsupported duct geometry '+p['id'])
        a=(round(p['x'],5),round(p['y'],5),round(p['z'],5));b=(round(p['x']+3,5),round(p['y'],5),round(p['z'],5))
        nodes[a].add(b);nodes[b].add(a)
    pending=set(nodes);components=[]
    while pending:
        start=next(iter(pending));visited={start};queue=deque([start]);pending.remove(start)
        while queue:
            for n in nodes[queue.popleft()]:
                if n in pending:pending.remove(n);visited.add(n);queue.append(n)
        components.append(visited)
    # No physical outlets/penetrations have yet been placed: room ownership
    # of a duct does not prove airflow or player access to the other rooms.
    targets=[z['id'] for z in data['zones'] if z['kind']!='exterior']
    outlets=[]
    result=dict(status='PASS' if len(components)==1 and len(outlets)==len(targets) else 'INCOMPLETE',
                duct_modules=len(ducts),physical_components=len(components),
                interior_zones=len(targets),connected_outlets=len(outlets),missing_outlets=targets)
    return result

if __name__=='__main__':
    p=json.loads((ROOT/'C01SourceV79/Data/ship_v79.json').read_text(encoding='utf8'))
    r=audit(p);(ROOT/'C01SourceV79/network_audit.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:v for k,v in r.items() if k!='missing_outlets'},ensure_ascii=False))
