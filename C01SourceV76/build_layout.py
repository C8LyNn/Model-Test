"""Rezone support rooms and give the evacuation shuttle a clear side launch."""
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from models_v5 import box
data=json.loads((root/'C01SourceV75/Data/ship_v75.json').read_text(encoding='utf8'))
zones={z['id']:z for z in data['zones']}
pairs=[('L2_S_SUPPORT_03','L2_S_SUPPORT_11'),('L2_N_SUPPORT_08','L2_S_SUPPORT_12'),('L2_N_SUPPORT_07','L2_S_SUPPORT_07')]
swap={a:b for a,b in pairs for a,b in ((a,b),(b,a))};moves=[];labels=[]
for a,b in pairs:
    labels.extend([{'id':a,'fromLabel':zones[a]['label'],'label':zones[b]['label']},
                   {'id':b,'fromLabel':zones[b]['label'],'label':zones[a]['label']}])
for p in data['placements']:
    if p['category']!='Props' or p['zone'] not in swap:continue
    src=zones[p['zone']];dst=zones[swap[p['zone']]];old=[p['x'],p['y'],p['z'],p['yaw']]
    p['x']=round(p['x']+dst['bounds'][0]-src['bounds'][0],6)
    p['z']=round(p['z']+dst['bounds'][2]-src['bounds'][2],6)
    original=p['zone'];p['zone']=dst['id']
    moves.append({'id':p['id'],'model':p['model'],'fromZone':original,'toZone':p['zone'],'before':old,'after':[p['x'],p['y'],p['z'],p['yaw']]})
for label in labels:zones[label['id']]['label']=label['label']
ship=next(p for p in data['placements'] if p['id']=='L0_EVAC_HANGAR_EVAC_SHUTTLE')
before=[ship['x'],ship['y'],ship['z'],ship['yaw']]
ship.update(x=113,y=-3.4,z=57,yaw=-90)
moves.append({'id':ship['id'],'model':ship['model'],'fromZone':ship['zone'],'toZone':ship['zone'],'before':before,'after':[ship['x'],ship['y'],ship['z'],ship['yaw']]})
removed=['W_H_108_72_-3.4','W_H_111_72_-3.4','N_111_72_-3.4']
for ident in removed:
    found=[p for p in data['placements'] if p['id']==ident]
    if len(found)!=1:raise ValueError('Missing launch wall '+ident)
    data['placements'].remove(found[0])
models=[
 {'id':'G76_LaunchLeft','family':'gate','nominal':[3,3,.3],'sockets':[],
  'parts':[box('METAL',[.15,0,-.15],[.3,3,.15]),box('METAL',[.3,2.9,-.15],[3,3,.15])]},
 {'id':'G76_LaunchRight','family':'gate','nominal':[3,3,.3],'sockets':[],
  'parts':[box('METAL',[2.7,0,-.15],[2.85,3,.15]),box('METAL',[0,2.9,-.15],[2.7,3,.15])]},
 {'id':'G76_LaunchLeaf','family':'gate','nominal':[.47,2.9,.018],'sockets':[],
  'parts':[box('PANEL',[0,0,-.009],[.47,2.9,.009])]}
]
data['models'].extend(models);added=[]
def place(ident,model,x,y,z,category,zone='L0_EVAC_HANGAR',yaw=0,**extra):
    p=dict(id=ident,model=model,category=category,zone=zone,deck=0,x=round(x,6),y=round(y,6),z=round(z,6),yaw=yaw,parent='',gate='',buttonGate='',buttonLift='',buttonFloor=0,travel=[0,0,0]);p.update(extra)
    added.append(p);data['placements'].append(p)
place('L0_LAUNCH_FRAME_L','G76_LaunchLeft',108,-3.4,72,'GateFrames')
place('L0_LAUNCH_FRAME_R','G76_LaunchRight',111,-3.4,72,'GateFrames')
leaves=[]
for side in (0,1):
    for i in range(6):
        x=108.31+side*2.67+i*.445;target=108.31 if side==0 else 113.2
        ident=f'L0_LAUNCH_LEAF_{side}_{i}';leaves.append(ident)
        place(ident,'G76_LaunchLeaf',x,-3.4,71.82+i*.04,'GateLeaves',gate='L0_LAUNCH_GATE',travel=[round(target-x,6),0,0])
buttons=[]
for i,(x,z,yaw) in enumerate(((107.7,71.85,180),(107.48,72.15,0))):
    ident=f'L0_LAUNCH_BUTTON_{i}';buttons.append(ident)
    place(ident,'P_Button',x,-2.3,z,'Buttons',yaw=yaw,buttonGate='L0_LAUNCH_GATE',buttonFloor=0)
for x in (108,111):
    for z in (72,75,78,81):
        place(f'L0_LAUNCH_APRON_{x}_{z}','F_47e7295d38df',x,-3.4,z,'Floors',zone='L0_LAUNCH_EXIT')
gate={'id':'L0_LAUNCH_GATE','deck':0,'x':108,'y':-3.4,'z':72,'yaw':0,'width':6,'height':3,
      'zones':['L0_EVAC_HANGAR','L0_LAUNCH_EXIT'],'leaves':leaves,'buttons':buttons,'airlock':'','lift':'','floor':-1,'initialOpen':0}
data['gates'].append(gate)
exit_zone={'id':'L0_LAUNCH_EXIT','label':'WYLOT PROMU','kind':'exterior','parent':'','deck':0,'floor':-3.4,'height':3,'bounds':[108,114,72,84],'waypoint':[111,-3.4,76]}
data['zones'].append(exit_zone);data['links'].append({'a':'L0_EVAC_HANGAR','b':'L0_LAUNCH_EXIT','kind':'gate','gate':'L0_LAUNCH_GATE'})
data['version']='C01.SHIP.7.6'
plan={'version':data['version'],'labels':labels,'moves':moves,'removed':removed,'added':added,'gate':gate,'models':models,'exitZone':exit_zone}
(root/'Assets/C01ShipV76/Data/operations.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),encoding='utf8')
(root/'C01SourceV76/Data/ship_v76.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Moved',len(moves),'relabelled',len(labels),'new modules',len(added))
