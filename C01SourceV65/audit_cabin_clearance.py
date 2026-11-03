"""Sweep all new cabin panels against existing static source solids."""
import json
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root/'C01SourceV65/Tools/v5_dependencies'))
from ship_geometry import overlap_poly
from validate_ship_v5 import solids

base=json.loads((root/'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf-8'))
new=json.loads((root/'Assets/C01ShipV65/Data/polish_v65.json').read_text(encoding='utf-8'))
old_lifts={l['id']:l for l in base['lifts']}
owners={p['id']:p for p in base['placements']}
errors=[]; checked=0
keep_old='--with-old-buttons' in sys.argv
mutate='--mutate' in sys.argv
for pose in (0,.25,.5,.75,1):
    obstacles=[s for s in solids(base,pose) if not owners[s['owner']].get('parent')
               and (keep_old or s['owner'] not in new['removedLandingButtons'])]
    for lift in new['lifts']:
        original=old_lifts[lift['id']]
        for panel in lift['panels']:
            x,y,z=panel['center'];sx,sy,sz=panel['size']
            if mutate and lift['id']=='BRIDGE_PASSENGER': x-=.2
            x+=original['x'];z+=original['z']
            bounds=[x-sx/2,x+sx/2,z-sz/2,z+sz/2]
            low=min(original['elevations'])+y-sy/2;high=max(original['elevations'])+y+sy/2
            poly=[[bounds[0],bounds[2]],[bounds[1],bounds[2]],[bounds[1],bounds[3]],[bounds[0],bounds[3]]]
            for s in obstacles:
                if min(high,s['hi'])-max(low,s['lo'])<1e-5: continue
                if min(bounds[1],s['x1'])-max(bounds[0],s['x0'])<1e-5: continue
                if min(bounds[3],s['z1'])-max(bounds[2],s['z0'])<1e-5: continue
                checked+=1
                if overlap_poly(poly,s['poly']):
                    errors.append(dict(lift=lift['id'],panel=panel['id'],other=s['owner'],part=s['part'],gate_pose=pose))

report=dict(status='PASS' if not errors else 'FAIL',poses=[0,.25,.5,.75,1],
            swept_lift_count=len(new['lifts']),broad_phase_candidates=checked,penetrations=len(errors),
            categories=dict(Counter(owners[e['other']]['category'] for e in errors)),
            owners=dict(Counter(e['other'] for e in errors)),examples=errors[:50])
dest=root/'C01ShipV65_QA';dest.mkdir(exist_ok=True)
name='cabin_clearance_old_buttons.json' if keep_old else 'cabin_clearance_mutation.json' if mutate else 'cabin_swept_clearance.json'
(dest/name).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
if errors: sys.exit(1)
