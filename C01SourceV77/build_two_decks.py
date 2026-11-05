"""Remove deck zero, preserve selected services and relocate the shuttle exit."""
import copy
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from models_v5 import box
from ship_geometry import clip_rect
data=json.loads((root/'C01SourceV76/Data/ship_v76.json').read_text(encoding='utf8'))
old={p['id']:p for p in data['placements']};moves=[]
def migrate(oldid,newid,zone,x,z,yaw=0):
    p=copy.deepcopy(old[oldid]);before=[p['x'],p['y'],p['z'],p['yaw']]
    p.update(id=newid,deck=1,zone=zone,x=x,y=0,z=z,yaw=yaw)
    moves.append({'oldId':oldid,'newId':newid,'model':p['model'],'zone':zone,'before':before,'after':[x,0,z,yaw]})
    return p
migrated=[]
for i in range(2):migrated.append(migrate(f'L0_ENGINE_ROOM_CORE_REACTOR_{i}',f'L1_ENGINE_REACTOR_{i}','L1_ENGINE_CONTROL',75+i*3,18))
for i in range(4):migrated.append(migrate(f'L0_PURIFICATION_PURIFIER_{i}',f'L1_LAB_PURIFIER_{i}','L1_LAB',64+i*5,67))
for i,(x,z) in enumerate(( (x,z) for z in (55.8,59,62.2) for x in (64,67,70,76,79) )):
    migrated.append(migrate(f'L0_HYDROPONICS_PLANT_{i}',f'L1_LAB_PLANT_{i}','L1_LAB',x,z))
for i in range(8):
    prefix='L0_FOOD_RESERVE' if i<4 else 'L0_CARGO';index=i%4
    migrated.append(migrate(f'{prefix}_CRATE_{index}',f'L1_CARGO_SUPPLY_{i}','L1_CARGO',116+(i%3)*3,18+(i//3)*3))
migrated.append(migrate('L0_EVAC_HANGAR_EVAC_SHUTTLE','L1_CARGO_EVAC_SHUTTLE','L1_CARGO',109,30,90))
def remove(p):
    return p['deck']==0 or (p['deck']==-1 and p['category'] in ('Walls','Nodes') and p['y']<-.401) or (p.get('buttonLift') and p['buttonFloor']==0)
removed=[p['id'] for p in data['placements'] if remove(p)]
data['placements']=[p for p in data['placements'] if not remove(p)]+migrated
removed_gates=[g['id'] for g in data['gates'] if g['deck']==0]
data['gates']=[g for g in data['gates'] if g['deck']!=0]
removed_zones=[z['id'] for z in data['zones'] if z['deck']==0]
data['zones']=[z for z in data['zones'] if z['deck']!=0]
data['links']=[l for l in data['links'] if l['a'] not in removed_zones and l['b'] not in removed_zones]
data['airlocks']=[a for a in data['airlocks'] if not any(g in removed_gates for g in a['gates'])]
data['decks']=[d for d in data['decks'] if d['id']!=0]
data['coverage']=[c for c in data['coverage'] if c['deck']!=0]
for lift in data['lifts']:
    lift['floors']=[1,2];lift['landings'][0]='';lift['waypoints']=lift['waypoints'][1:]
labels={'L1_ENGINE_CONTROL':'MASZYNOWNIA I STEROWANIE','L1_LAB':'LABORATORIUM I PODTRZYMANIE ZYCIA','L1_CARGO':'LADOWNIA I HANGAR'}
for z in data['zones']:
    if z['id'] in labels:z['label']=labels[z['id']]
remove_upper=['W_H_108_15_0','W_H_111_15_0','N_111_15_0']
for ident in remove_upper:
    found=[p for p in data['placements'] if p['id']==ident]
    if len(found)!=1:raise ValueError('Missing hangar wall '+ident)
    data['placements'].remove(found[0]);removed.append(ident)
models=[{'id':'P77_ShaftPassenger','family':'floor','nominal':[3,.2,3],'sockets':[],'parts':[box('METAL',[0,0,0],[2.58,.2,2.58])]},
        {'id':'P77_ShaftCargo','family':'floor','nominal':[3,.2,3],'sockets':[],'parts':[box('METAL',[0,0,0],[2.85,.2,2.85])]}]
edge=copy.deepcopy(next(m for m in data['models'] if m['id']=='F_47e7295d38df'));edge['id']='F77_LaunchEdge'
for part in edge['parts']:
    poly=clip_rect(list(zip(part['outline'][::2],part['outline'][1::2])),0,3,0,2.85)
    part['outline']=[v for point in poly for v in point]
edge['parts']=[p for p in edge['parts'] if p['outline']];models.append(edge)
data['models'].extend(models);added=[]
def add(p):added.append(p);data['placements'].append(p)
for lift in data['lifts']:
    x0,x1,z0,z1=lift['bounds'];cargo=lift['id'].startswith('STERN_CARGO')
    for i in range(2 if cargo else 1):
        for j in range(2 if cargo else 1):
            p={'id':f"{lift['id']}_SHAFT_BASE_{i}_{j}",'model':'P77_ShaftCargo' if cargo else 'P77_ShaftPassenger',
               'category':'ShaftBases','zone':'','deck':1,'x':round(x0+i*2.85,6),'y':-.4,'z':round(z0+j*2.85,6),'yaw':0,
               'parent':'','gate':'','buttonGate':'','buttonLift':'','buttonFloor':0,'travel':[0,0,0]};add(p)
oldplan=json.loads((root/'Assets/C01ShipV76/Data/operations.json').read_text(encoding='utf8'))
for p in oldplan['added']:
    q=copy.deepcopy(p);q['id']=p['id'].replace('L0_LAUNCH','L1_LAUNCH');q['deck']=1;q['y']=round(p['y']+3.4,6)
    q['zone']='L1_LAUNCH_EXIT' if p['category']=='Floors' else 'L1_CARGO';q['z']=round((84 if p['category']=='Floors' else 87)-p['z'],6)
    if p['category']=='Floors' and q['z']==12:q['model']='F77_LaunchEdge'
    if p['category']=='Buttons':
        q['yaw']=(p['yaw']+180)%360;q['x']=107.48 if q['yaw']==0 else 107.7
    if p['gate']:q['gate']='L1_LAUNCH_GATE'
    if p['buttonGate']:q['buttonGate']='L1_LAUNCH_GATE';q['buttonFloor']=1
    add(q)
g=copy.deepcopy(oldplan['gate']);g.update(id='L1_LAUNCH_GATE',deck=1,y=0,z=15,zones=['L1_CARGO','L1_LAUNCH_EXIT'])
g['leaves']=[x.replace('L0_LAUNCH','L1_LAUNCH') for x in g['leaves']];g['buttons']=[x.replace('L0_LAUNCH','L1_LAUNCH') for x in g['buttons']]
data['gates'].append(g)
exit_zone={'id':'L1_LAUNCH_EXIT','label':'WYLOT PROMU','kind':'exterior','parent':'','deck':1,'floor':0,'height':3,'bounds':[108,114,3,15],'waypoint':[111,0,6]}
data['zones'].append(exit_zone);data['links'].append({'a':'L1_CARGO','b':'L1_LAUNCH_EXIT','kind':'gate','gate':'L1_LAUNCH_GATE'})
data['version']='C01.SHIP.7.7'
plan={'version':data['version'],'removed':removed,'removedGates':removed_gates,'removedZones':removed_zones,'moves':moves,'labels':[{'id':k,'label':v} for k,v in labels.items()],
      'added':added,'models':models,'gate':g,'exitZone':exit_zone}
(root/'Assets/C01ShipV77/Data/two_decks.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
(root/'C01SourceV77/Data/ship_v77.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('removed',len(removed),'transferred',len(moves),'new modules',len(added),'gates removed',len(removed_gates))
