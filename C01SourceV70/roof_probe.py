"""Probe whether making low sector roofs flush would intersect real geometry."""
from collections import defaultdict
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV68/Tools/v5_dependencies'))
from validate_ship_v5 import solids
from ship_geometry import overlap_poly

data=json.loads((ROOT/'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
bodies=solids(data);low=[s for s in bodies if s['category']=='Ceilings' and abs(s['hi']-6.2)<1e-5]
other=[s for s in bodies if not(s['category']=='Ceilings' and abs(s['hi']-6.2)<1e-5) and s['hi']>6.2+1e-5 and s['lo']<6.6-1e-5]
bins=defaultdict(list)
for s in other:
    for x in range(math.floor(s['x0']/3),math.floor(s['x1']/3)+1):
        for z in range(math.floor(s['z0']/3),math.floor(s['z1']/3)+1):bins[x,z].append(s)
hits=set()
for a in low:
    candidates=[]
    for x in range(math.floor(a['x0']/3),math.floor(a['x1']/3)+1):
        for z in range(math.floor(a['z0']/3),math.floor(a['z1']/3)+1):candidates+=bins[x,z]
    for b in candidates:
        if min(a['x1'],b['x1'])-max(a['x0'],b['x0'])<1e-5 or min(a['z1'],b['z1'])-max(a['z0'],b['z0'])<1e-5:continue
        if overlap_poly(a['poly'],b['poly']):hits.add((a['owner'],b['owner'],b['category']))
result={'low_roof_parts':len(low),'collision_pairs_if_thickened':len(hits),'by_category':{},'examples':sorted(hits)[:20]}
for _,_,cat in hits:result['by_category'][cat]=result['by_category'].get(cat,0)+1
out=ROOT/'C01ShipV70_QA/roof_probe.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
