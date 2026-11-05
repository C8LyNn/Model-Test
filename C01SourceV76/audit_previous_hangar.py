"""Measure the previous shuttle's straight route toward its old aft gate."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from validate_ship_v5 import solids
from ship_geometry import overlap_poly

data=json.loads((root/'C01SourceV75/Data/ship_v75.json').read_text(encoding='utf8'))
bodies=solids(data,1);craft=[s for s in bodies if s['owner']=='L0_EVAC_HANGAR_EVAC_SHUTTLE']
others=[s for s in bodies if s['owner']!='L0_EVAC_HANGAR_EVAC_SHUTTLE' and s['x1']>89 and s['x0']<174 and s['z1']>64.5 and s['z0']<68.5 and s['hi']>-3.4 and s['lo']<-.6]
hits=[]
for step in range(701):
    dx=step*.1
    for a in craft:
        for b in others:
            if min(a['hi'],b['hi'])-max(a['lo'],b['lo'])<1e-5 or min(a['x1']+dx,b['x1'])-max(a['x0']+dx,b['x0'])<1e-5 or min(a['z1'],b['z1'])-max(a['z0'],b['z0'])<1e-5:continue
            if overlap_poly([[x+dx,z] for x,z in a['poly']],b['poly']):hits.append({'distance':round(dx,1),'obstacle':b['owner']})
    if hits:break
report={'status':'BLOCKED' if hits else 'CLEAR','firstHits':hits[:10]}
(root/'C01ShipV76_QA/previous_shuttle_path.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
if not hits:raise SystemExit('Expected pre-existing obstruction was not detected')
