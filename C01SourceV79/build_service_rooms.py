"""Draft: convert upper cabins to service rooms; shipwide ducts are NOT built yet."""
import copy, json
from pathlib import Path

root=Path(__file__).resolve().parent.parent
data=json.loads((root/'C01SourceV78/Data/ship_v78.json').read_text(encoding='utf8'))
rooms=[z for z in data['zones'] if z['deck']==2 and z['kind']=='cabin']
assert len(rooms)==12
baths={z['id']:z['parent'] for z in data['zones'] if z['deck']==2 and z['kind']=='bathroom'}
assert len(baths)==12
roomids={z['id'] for z in rooms};gateids={g['id'] for g in data['gates'] if any(z in baths for z in g['zones'])}
assert len(gateids)==12
removed=set(); walls=set(); nodes=set()
for z in rooms:
    x0,x1,z0,z1=map(int,z['bounds']);north='_N_' in z['id'];bz=z0+3 if north else z0+6
    for x in (x0,x0+3):walls.add(('H',x,bz))
    walls.add(('V',x0+6,z0 if north else z0+6))
    nodes.update({(x0+3,bz),(x0+6,bz)})
    z['kind']='ventilation_service';z['label']='WENTYLACJA '+z['id'].split('_')[-1]
    z['height']=3
for p in data['placements']:
    gatepart=any(p['id'].startswith(g+'_') for g in gateids)
    axis='V' if p['yaw']==-90 else 'H'
    # Preserve the fascia occupying the 0.4 m floor/ceiling thickness: its top
    # is flush with the deck and it closes the cut tiles on both sides.
    insidewall=p['deck']==-1 and 3.4<=p['y']<6.4 and p['category']=='Walls' and (axis,p['x'],p['z']) in walls
    insidenode=p['deck']==-1 and 3.4<=p['y']<6.4 and p['category']=='Nodes' and (p['x'],p['z']) in nodes
    furnishing=(p['zone'] in roomids or p['zone'] in baths) and p['category']=='Props'
    if gatepart or insidewall or insidenode or furnishing:removed.add(p['id'])
    elif p['zone'] in baths:p['zone']=baths[p['zone']]
data['placements']=[p for p in data['placements'] if p['id'] not in removed]
data['gates']=[g for g in data['gates'] if g['id'] not in gateids]
data['zones']=[z for z in data['zones'] if z['id'] not in baths]
links=[]
for link in data['links']:
    link['a']=baths.get(link['a'],link['a']);link['b']=baths.get(link['b'],link['b'])
    if link['a']!=link['b'] and link['gate'] not in gateids:links.append(link)
data['links']=links
added=[]
for z in rooms:
    x0,x1,z0,z1=z['bounds']
    for i in range(2):
        p=dict(id='V79_VENT_'+z['id']+'_'+str(i),model='P_Vent_3m',category='Ventilation',zone=z['id'],deck=2,x=x0+.6+3*i,y=3.55,z=z0+1,yaw=0,parent='',gate='',buttonGate='',buttonLift='',buttonFloor=0,travel=[0,0,0])
        added.append(p)
data['placements']+=added;data['version']='C01.SHIP.7.9-DRAFT'
plan=dict(removed=sorted(removed),removedGates=sorted(gateids),removedZones=sorted(baths),zoneMap=[dict(oldId=k,newId=v) for k,v in baths.items()],rooms=[z['id'] for z in rooms],added=added)
for path,obj in ((root/'C01SourceV79/Data/ship_v79.json',data),(root/'Assets/C01ShipV79/Data/ventilation.json',plan)):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('rooms',len(rooms),'removed',len(removed),'added',len(added),'gate controllers',len(gateids))
