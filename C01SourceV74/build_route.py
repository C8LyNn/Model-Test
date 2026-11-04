"""Generate a forced pursuit route through three sectors using 3 m modules."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV71/Tools/v5_dependencies'))
from models_v5 import box

data=json.loads((ROOT/'C01SourceV73/Data/ship_v73.json').read_text(encoding='utf8'))
routes=[dict(name='GYM',x0=9,x1=33,z0=54,z1=57,side='N',branches=(1,2)),
        dict(name='ENGINE_CONTROL',x0=51,x1=75,z0=30,z1=33,side='S',branches=(3,4)),
        dict(name='MED',x0=93,x1=117,z0=54,z1=57,side='N',branches=(5,6))]
models={m['id']:m for m in data['models']}
models['G_V74_Frame']={'id':'G_V74_Frame','family':'gate','nominal':[3,2.6,.3],'sockets':[],
    'parts':[box('METAL',[.15,0,-.15],[.23,2.6,.15]),box('METAL',[2.77,0,-.15],[2.85,2.6,.15]),
             box('METAL',[.23,2.42,-.15],[2.77,2.6,.15])]}
models['G_V74_Leaf']={'id':'G_V74_Leaf','family':'gate','nominal':[.26,2.36,.022],'sockets':[],
    'parts':[box('ACCENT',[0,0,-.011],[.018,2.36,.011]),box('PANEL',[.018,0,-.011],[.242,2.36,.011]),
             box('ACCENT',[.242,0,-.011],[.26,2.36,.011])]}
data['models'] += [models['G_V74_Frame'],models['G_V74_Leaf']]
ids={p['id'] for p in data['placements']};removed=[];added=[];gate_records=[]
def place(ident,model,x,y,z,yaw=0,category='Props',zone='',deck=2,**extra):
    if ident in ids:raise ValueError('Duplicate '+ident)
    p=dict(id=ident,model=model,category=category,zone=zone,deck=deck,x=round(x,6),y=round(y,6),z=round(z,6),yaw=yaw,
           parent='',gate='',buttonGate='',buttonLift='',buttonFloor=0,travel=[0,0,0]);p.update(extra)
    added.append(p);data['placements'].append(p);ids.add(ident);return p

for route in routes:
    name,x0,x1,z0,z1,side=(route[k] for k in ('name','x0','x1','z0','z1','side'))
    zone='L2_'+name
    entry_z=z0 if side=='N' else z1
    target=next(z for z in data['zones'] if z['id']==zone);target['kind']='gallery';target['label']='TRASA '+name.replace('_',' ')
    for x in (x0,x1-3):
        ident=f'W_H_{x}_{entry_z}_3.4'
        old=next((p for p in data['placements'] if p['id']==ident),None)
        if old is None or old['model']!='W3_H3000':raise ValueError('Unexpected opening wall '+ident)
        data['placements'].remove(old);removed.append(ident)
        place(f'L2_ROUTE_{name}_HEAD_{x}','W3_H400',x,6.0,entry_z,category='Walls',zone=zone)
    floor='F_31fb4dc26a9f' if side=='N' else 'F_2e82f0a7ab08'
    far_z=z1 if side=='N' else z0
    for i,x in enumerate(range(x0,x1,3)):
        place(f'L2_ROUTE_{name}_FLOOR_{i}',floor,x,3.4,z0,category='Floors',zone=zone)
        place(f'L2_ROUTE_{name}_RAIL_{i}','P_Rail3',x,3.4,far_z,category='Railings',zone=zone)
    for i,x in enumerate((x0,x1)):
        place(f'L2_ROUTE_{name}_RAIL_END_{i}','P_Rail3',x,3.4,z0,-90,category='Railings',zone=zone)
    for i,x in enumerate(range(x0,x1+1,3)):
        place(f'L2_ROUTE_{name}_POST_{i}','P_RailPost',x,3.4,far_z,category='Railings',zone=zone)
    for i,x in enumerate((x0+6,x0+12,x0+18)):
        z=z0+(.22 if i%2==0 else 1.63)
        place(f'L2_ROUTE_{name}_OBSTACLE_{i}','P_ChaseCrate' if i!=1 else 'P_ChaseBarrier',
              x,3.4,z,category='ChaseObstacles',zone=zone)
    for label,x,branch in (('IN',x0,route['branches'][0]),('OUT',x1-3,route['branches'][1])):
        gid=f'L2_ROUTE_{name}_{label}'
        frame=place(gid+'_FRAME','G_V74_Frame',x,3.4,entry_z,category='GateFrames',zone=zone)
        leaves=[]
        for side_index in (0,1):
            for i in range(4):
                px=.5+i*.25 if side_index==0 else 1.5+i*.25
                target=.24 if side_index==0 else 2.5
                ident=f'{gid}_LEAF_{side_index}_{i}';leaves.append(ident)
                place(ident,'G_V74_Leaf',x+px,3.42,entry_z-.06+i*.04,category='GateLeaves',zone=zone,
                      gate=gid,travel=[round(target-px,6),0,0])
        buttons=[]
        for i in (0,1):
            ident=gid+'_BUTTON_'+str(i);buttons.append(ident)
            place(ident,'P_Button',x+(.24 if i==0 else .46),4.5,entry_z+(.15 if i==0 else -.15),
                  0 if i==0 else 180,category='Buttons',zone=zone,buttonGate=gid,buttonFloor=2)
        gate=dict(id=gid,deck=2,x=x,y=3.4,z=entry_z,yaw=0,width=3,height=2.6,
                  zones=['L2_'+route['side']+'_BRANCH_'+str(branch),zone],leaves=leaves,buttons=buttons,
                  airlock='',lift='',floor=-1,initialOpen=1)
        data['gates'].append(gate);gate_records.append(gate)
        data['links'].append(dict(a=gate['zones'][0],b=zone,kind='gate',gate=gid))
for x in (18,60,102):
    place('L2_ROUTE_BULKHEAD_'+str(x),'W3_H3000',x,3.4,42,-90,category='Walls',zone='L2_MAIN')
data['version']='C01.SHIP.7.4'
plan=dict(version=data['version'],routes=routes,removed=removed,added=added,gates=gate_records,
          models=[models['G_V74_Frame'],models['G_V74_Leaf']],
          zones=[z for z in data['zones'] if z['id'] in ('L2_GYM','L2_ENGINE_CONTROL','L2_MED')])
path=ROOT/'Assets/C01ShipV74/Data/pursuit.json';path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(plan,indent=2),encoding='utf8')
(ROOT/'C01SourceV74/Data/ship_v74.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('removed',len(removed),'added',len(added),'gates',len(gate_records))
