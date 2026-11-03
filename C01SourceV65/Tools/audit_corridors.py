"""Independent cell-based check of actual floor solids in one-tile corridors."""
import json,math,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'v5_dependencies'))
from validate_ship_v5 import solids,difference
from ship_geometry import polygon_area
import grid_layout

root=Path(__file__).resolve().parents[2]
data=json.loads((root/'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf8'))
mutate='--mutate' in sys.argv
if mutate:
    before=len(data['placements'])
    data['placements']=[p for p in data['placements'] if p['id']!='F_1_0_14']
    if len(data['placements'])!=before-1:raise RuntimeError('Mutation target missing')
plan=grid_layout.build();zones={z['id']:z for z in plan['zones']};bins=defaultdict(list)
for solid in solids(data):
    if solid['category']!='Floors':continue
    for deck,y in enumerate(plan['elevations']):
        if abs(solid['hi']-y)>1e-5:continue
        for x in range(math.floor(solid['x0']/3),math.floor(solid['x1']/3)+1):
            for z in range(math.floor(solid['z0']/3),math.floor(solid['z1']/3)+1):bins[deck,x,z].append(solid['poly'])
missing=[];count=0
for c in plan['corridors']:
    z=zones[c['id']];deck=z['deck']
    for x in range(z['x0'],z['x1']):
        for zz in range(z['z0'],z['z1']):
            count+=1;x0=x*3+.151;x1=x*3+2.849;z0=zz*3+.151;z1=zz*3+2.849
            remain=[[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]]
            for floor in bins[deck,x,zz]:
                remain=[p for r in remain for p in difference(r,floor)]
                if not remain:break
            area=sum(polygon_area(p) for p in remain)
            if area>1e-5:missing.append(dict(corridor=c['id'],x=x,z=zz,area=area))
report=dict(status='PASS' if not missing else 'FAIL',corridors=len(plan['corridors']),cells=count,
            missing=len(missing),examples=missing[:30])
out=root/'C01ShipV65_QA';out.mkdir(exist_ok=True)
(out/('corridor_floor_mutation.json' if mutate else 'corridor_floor_coverage.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2));sys.exit(1 if missing else 0)
