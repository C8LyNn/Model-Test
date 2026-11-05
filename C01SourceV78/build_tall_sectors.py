"""Raise the six shared sector roofs by one 3 m architectural module."""
import copy
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = json.loads((root/'C01SourceV77/Data/ship_v77.json').read_text(encoding='utf8'))
sectors = [z for z in data['zones'] if z['kind'] == 'sector']
assert len(sectors) == 6 and all(z['height'] == 6 for z in sectors)
edges, nodes = {}, {}
for zone in sectors:
    zone['height'] = 9
    x0,x1,z0,z1 = map(int,zone['bounds'])
    for x in range(x0,x1,3):
        for z in (z0,z1): edges.setdefault(('H',x,z),zone['id'])
    for x in (x0,x1):
        for z in range(z0,z1,3): edges.setdefault(('V',x,z),zone['id'])
    for x in range(x0,x1+1,3):
        for z in (z0,z1): nodes.setdefault((x,z),zone['id'])
    for x in (x0,x1):
        for z in range(z0,z1+1,3): nodes.setdefault((x,z),zone['id'])

roof=[]; removed=[]
kept=[]
sector_ids={z['id'] for z in sectors}
for p in data['placements']:
    if p['category']=='Ceilings' and p['zone'] in sector_ids and p['y']==6.2:
        roof.append(p['id']);p['y']=9.2
    axis = 'V' if p['yaw']==-90 else 'H'
    if p['category']=='Walls' and p['y']>=6.4 and (axis,p['x'],p['z']) in edges:
        removed.append(p['id']);continue
    if p['category']=='Nodes' and p['y']>=6 and (p['x'],p['z']) in nodes:
        removed.append(p['id']);continue
    kept.append(p)
assert len(roof)>400 and removed
data['placements']=kept
added=[]
def placement(ident,model,cat,zone,x,z,yaw):
    return dict(id=ident,model=model,category=cat,zone=zone,deck=2,x=x,y=6,z=z,yaw=yaw,parent='',gate='',buttonGate='',buttonLift='',buttonFloor=0,travel=[0,0,0])
for (axis,x,z),zone in sorted(edges.items()):
    p=placement(f'V78_W_{axis}_{x}_{z}','W78_H2600','Walls',zone,x,z,-90 if axis=='V' else 0);p['y']=6.4;p['axis']=axis;added.append(p)
for (x,z),zone in sorted(nodes.items()):
    lower=[p for p in kept if p['category']=='Nodes' and p['x']==x and p['z']==z and 2.99<=p['y']<6]
    start=max((p['y']+3 for p in lower),default=6)
    p=placement(f'V78_N_{x}_{z}','N_H2600' if start>6.1 else 'N_H3000','Nodes',zone,x,z,0);p['y']=start;added.append(p)
data['placements']+=added;data['version']='C01.SHIP.7.8'
wall=copy.deepcopy(next(m for m in data['models'] if m['id']=='W3_H3000'));wall['id']='W78_H2600';wall['nominal'][1]=2.6
for part in wall['parts']:
    if part['y1']>1:part['y1']=round(part['y1']-.4,6)
    if part['y0']>1:part['y0']=round(part['y0']-.4,6)
data['models'].append(wall)
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from validate_ship_v5 import solids, difference
from ship_geometry import overlap_poly, polygon_area
bodies=solids(data); structural=[s for s in bodies if s['owner'].startswith('V78_')]
by_ceiling={}
for s in bodies:
    if s['category']!='Ceilings' or not s['owner'].startswith('C2_'):continue
    cuts=[]
    for t in structural:
        if min(s['hi'],t['hi'])-max(s['lo'],t['lo'])<1e-5 or min(s['x1'],t['x1'])-max(s['x0'],t['x0'])<1e-5 or min(s['z1'],t['z1'])-max(s['z0'],t['z0'])<1e-5:continue
        if overlap_poly(s['poly'],t['poly']):cuts.append(t['poly'])
    if cuts:by_ceiling[s['owner']]=cuts
models={m['id']:m for m in data['models']};ceiling_changes=[];new_models=[wall];cache={}
for p in data['placements']:
    if p['id'] not in by_ceiling:continue
    original=models[p['model']];assert p['yaw']==0
    new=copy.deepcopy(original);parts=[]
    for part in original['parts']:
        poly=[[part['outline'][i]+p['x'],part['outline'][i+1]+p['z']] for i in range(0,len(part['outline']),2)]
        fragments=[poly]
        for cut in by_ceiling[p['id']]:fragments=[piece for f in fragments for piece in difference(f,cut)]
        for fragment in fragments:
            if polygon_area(fragment)<1e-7:continue
            q=copy.deepcopy(part);q['outline']=[round(v,6) for x,z in fragment for v in (x-p['x'],z-p['z'])];parts.append(q)
    assert parts,p['id'];new['parts']=parts
    signature=json.dumps((original['id'],parts),sort_keys=True)
    if signature not in cache:
        new['id']=f'C78_Trim_{len(cache):03d}';cache[signature]=new['id'];new_models.append(new);data['models'].append(new)
    old=p['model'];p['model']=cache[signature];ceiling_changes.append(dict(id=p['id'],oldModel=old,newModel=p['model']))
plan=dict(roof=roof,removed=removed,added=added,sectors=sorted(sector_ids),models=new_models,ceilingChanges=ceiling_changes)
for path,obj in ((root/'C01SourceV78/Data/ship_v78.json',data),(root/'Assets/C01ShipV78/Data/tall_sectors.json',plan)):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('roof',len(roof),'replaced',len(removed),'new',len(added),'trimmed ceilings',len(ceiling_changes),'models',len(new_models))
