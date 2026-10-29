"""Build one reference-backed region graph and geometry manifest; no visual-only offsets."""
import hashlib,json,math
from pathlib import Path
from ship_geometry import ccw,clip_rect,strip_polygons,triangulate
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT/'UnityProject'
OUT=PROJECT/'Assets/C01ShipV3/Data/ship.json'

def part(role,poly,y0,y1):return dict(role=role,outline=[v for p in ccw(poly) for v in p],y0=y0,y1=y1)
def box(role,lo,hi):return part(role,[[lo[0],lo[2]],[hi[0],lo[2]],[hi[0],hi[2]],[lo[0],hi[2]]],lo[1],hi[1])
def build(branch_length=9):
    if not isinstance(branch_length,int) or branch_length<3 or branch_length%3:
        raise ValueError('Side corridor length must be a positive multiple of 3 m, at least 3 m')
    main_s=6+branch_length;main_n=main_s+3;north=main_n+branch_length
    height=north+6;center=height/2;bridge_top=height-3
    zones=[];placements=[];mods=[];doors=[];openings=[]
    palette={'KOSZARY':[.34,.43,.3,1],'LAB':[.41,.34,.49,1],'MED':[.5,.36,.38,1],
             'CARGO':[.48,.4,.24,1],'ENGINEERING':[.48,.33,.24,1],'TECH':[.28,.4,.46,1],
             'cabin':[.48,.44,.33,1],'corridor':[.2,.36,.42,1],'airlock':[.18,.48,.44,1],'bridge':[.22,.37,.44,1]}
    def zone(zid,label,kind,bounds,waypoint=None,color=None):
        zones.append(dict(id=zid,label=label,kind=kind,bounds=bounds,waypoint=waypoint or [(bounds[0]+bounds[1])/2,0,(bounds[2]+bounds[3])/2],color=color or palette.get(zid,palette.get(kind,[.25,.34,.4,1]))))
    for idx,(top,bottom) in enumerate([('KOSZARY','CARGO'),('LAB','ENGINEERING'),('MED','TECH')]):
        x=idx*15
        labels={'KOSZARY':'KOSZARY','LAB':'LABORATORIUM','MED':'SEKTOR MEDYCZNY','CARGO':'MAGAZYN','ENGINEERING':'MASZYNOWNIA','TECH':'SEKTOR TECHNICZNY'}
        zone(top,labels[top],'sector',[x,x+15,north,height],waypoint=[x+7.5,0,north+3]);zone(bottom,labels[bottom],'sector',[x,x+15,0,6],waypoint=[x+7.5,0,3])
        for side,z0,base in [('N',main_n,0),('S',6,6)]:
            for offset,rx in enumerate([x,x+9]):
                num=base+idx*2+offset+1;zone(f'C{num:02d}',f'KAJUTA {num:02d}','cabin',[rx,rx+6,z0,z0+branch_length])
            zone(f'X{side}{idx+1}','KORYTARZ','corridor',[x+6,x+9,z0,z0+branch_length])
    for zid,label,bounds in [('MAIN_W','KORYTARZ GŁÓWNY',[0,12,main_s,main_n]),('D1','D1',[12,18,main_s,main_n]),('MAIN_M','KORYTARZ GŁÓWNY',[18,27,main_s,main_n]),('D2','D2',[27,33,main_s,main_n]),('MAIN_E','KORYTARZ GŁÓWNY',[33,45,main_s,main_n])]:
        zone(zid,label,'airlock' if zid.startswith('D') else 'corridor',bounds)
    zone('STERN','RUFA / WĘZEŁ ŚLUZ','corridor',[45,48,3,bridge_top],waypoint=[46.5,0,center])
    zone('D3','D3','airlock',[45,48,bridge_top,height]);zone('D4','D4','airlock',[45,48,0,3])
    zone('BRIDGE','MOSTEK','bridge',[-12,0,3,bridge_top],waypoint=[-3,0,center])
    zone('EXIT_N','WYJŚCIE 1','exterior',[45,48,height,height+3]);zone('EXIT_S','WYJŚCIE 2','exterior',[45,48,-3,0])
    zmap={z['id']:z for z in zones}
    def place(pid,mid,pos,yaw,cat,zid='',**extra):placements.append(dict(id=pid,module=mid,x=pos[0],y=pos[1],z=pos[2],yaw=yaw,category=cat,zone=zid,**extra))
    def module(mid,parts):mods.append(dict(id=mid,parts=parts));return mid
    def prism(mid,poly,y0,y1,role,category,zid=''):
        anchor=poly[0];local=[[p[0]-anchor[0],p[1]-anchor[1]] for p in poly]
        module(mid,[part(role,local,y0,y1)]);place(mid,mid,[anchor[0],0,anchor[1]],0,category,zid)
    def door(did,a,b,axis,x,z,airlock='',reverse=False):
        yaw=(180 if axis=='H' else 90) if reverse else (0 if axis=='H' else -90)
        doors.append(dict(id=did,zones=[a,b],axis=axis,x=x,z=z,yaw=yaw,root_x=x+(3 if reverse and axis=='H' else 0),root_z=z+(3 if reverse and axis=='V' else 0),airlock=airlock))
    for idx in range(3):
        x=idx*15
        door_offset=((branch_length//3-1)//2)*3
        for row,z,offset,prefix in [('N',main_n+door_offset,0,'XN'),('S',6+door_offset,6,'XS')]:
            for k,dx in enumerate([6,9]):door(f'CABIN_{offset+idx*2+k+1:02d}',f'C{offset+idx*2+k+1:02d}',prefix+str(idx+1),'V',x+dx,z,reverse=k==0)
        door('SECTOR_N_'+str(idx+1),['KOSZARY','LAB','MED'][idx],'XN'+str(idx+1),'H',x+6,north,reverse=True)
        door('SECTOR_S_'+str(idx+1),['CARGO','ENGINEERING','TECH'][idx],'XS'+str(idx+1),'H',x+6,6)
    for a,b,x in [('KOSZARY','LAB',15),('LAB','MED',30)]:door(a+'_'+b,a,b,'V',x,north+3)
    for a,b,x in [('CARGO','ENGINEERING',15),('ENGINEERING','TECH',30)]:door(a+'_'+b,a,b,'V',x,3)
    for zid,z in [('KOSZARY',north),('MAIN_W',main_s),('CARGO',3)]:door('BRIDGE_'+zid,'BRIDGE',zid,'V',0,z)
    for zid,z in [('MED',north),('MAIN_E',main_s),('TECH',3)]:door('STERN_'+zid,'STERN',zid,'V',45,z,reverse=True)
    for name,x,left,right in [('D1',12,'MAIN_W','MAIN_M'),('D2',27,'MAIN_M','MAIN_E')]:
        door(name+'_A',left,name,'V',x,main_s,name);door(name+'_B',name,right,'V',x+6,main_s,name)
    for name,zinner,zouter,pad in [('D3',bridge_top,height,'EXIT_N'),('D4',3,0,'EXIT_S')]:
        door(name+'_INNER','STERN',name,'H',45,zinner,name,reverse=name=='D3');door(name+'_OUTER',name,pad,'H',45,zouter,name,reverse=name=='D4')
    cells={}
    for z in zones:
        if z['id']=='BRIDGE':continue
        x0,x1,z0,z1=z['bounds']
        for x in range(x0,x1,3):
            for zz in range(z0,z1,3):
                if (x,zz) in cells:raise ValueError('Zones overlap')
                cells[x,zz]=z['id']
    for (x,z),zid in sorted(cells.items()):
        floor='F02_Floor_3m_Warning' if zmap[zid]['kind'] in ['airlock','exterior'] else 'F01_Floor_3m'
        place(f'F_{x}_{z}',floor,[x,0,z],0,'Floors',zid)
        if zmap[zid]['kind']!='exterior':place(f'C_{x}_{z}','C01_Ceiling_3m',[x,3,z],0,'Ceilings',zid)
    bridge_poly=[[0,3],[0,bridge_top],[-6,bridge_top],[-12,center],[-6,3]]
    for x in range(-12,0,3):
        for z in range(3,bridge_top,3):
            p=clip_rect(bridge_poly,x,x+3,z,z+3)
            if not p:continue
            if abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2-9)<1e-6:
                place(f'F_{x}_{z}','F01_Floor_3m',[x,0,z],0,'Floors','BRIDGE');place(f'C_{x}_{z}','C01_Ceiling_3m',[x,3,z],0,'Ceilings','BRIDGE')
            else:
                local=[[v[0]-x,v[1]-z] for v in p];suffix=hashlib.sha1(json.dumps(local).encode()).hexdigest()[:8]
                for prefix,role,y0,y1,py,cat in [('F','FLOOR',-.18,0,0,'Floors'),('C','ROOF',0,.18,3,'Ceilings')]:
                    mid=prefix+'_BowTile_'+suffix
                    if not any(m['id']==mid for m in mods):module(mid,[part(role,local,y0,y1)])
                    place(f'{prefix}_{x}_{z}',mid,[x,py,z],0,cat,'BRIDGE')
    # Build each grid boundary once. Bridge rear is a virtual neighbour.
    door_at={(d['axis'],d['x'],d['z']):d for d in doors};boundaries={}
    for (x,z),zid in cells.items():
        if zmap[zid]['kind']=='exterior':continue
        for key,other in [(('H',x,z),(x,z-3)),(('H',x,z+3),(x,z+3)),(('V',x,z),(x-3,z)),(('V',x+3,z),(x+3,z))]:
            if key in boundaries:continue
            nid=cells.get(other,'')
            if key[0]=='V' and key[1]==0 and 3<=key[2]<bridge_top:nid='BRIDGE'
            if nid==zid:continue
            if key not in door_at and nid and zmap[nid]['kind']=='corridor' and zmap[zid]['kind']=='corridor':
                openings.append(dict(axis=key[0],x=key[1],z=key[2],zones=[zid,nid]));boundaries[key]=None
            else:boundaries[key]=[zid,nid]
    nodes={};wallidx=0
    for key,pair in sorted(boundaries.items()):
        if pair is None:continue
        axis,x,z=key;d=door_at.get(key);wallidx+=1
        mid='W04_DoorWall_3m' if d else ['W01_Wall_3m','W02_Wall_3m_Variant','W05_Wall_3m_Service'][wallidx%3]
        pid=d['id'] if d else f'W_{axis}_{x}_{z}'
        place(pid,mid,[d['root_x'] if d else x,0,d['root_z'] if d else z],d['yaw'] if d else (0 if axis=='H' else -90),'Walls',next((v for v in pair if v),''))
        endpoints=[((x,z),(1,0)),((x+3,z),(-1,0))] if axis=='H' else [((x,z),(0,1)),((x,z+3),(0,-1))]
        for pos,direction in endpoints:nodes.setdefault(pos,[]).append(direction)
    for z in [3,bridge_top]:nodes.setdefault((0,z),[]).append((-1,0))
    for (x,z),dirs in sorted(nodes.items()):
        count=len(dirs);kind='END' if count==1 else 'CROSS' if count==4 else 'T' if count==3 else 'STRAIGHT' if dirs[0][0]+dirs[1][0]==0 and dirs[0][1]+dirs[1][1]==0 else 'CORNER'
        place(f'N_{x}_{z}','N_'+kind,[x,0,z],0,'Nodes')
    bow_path=[[-.15,3],[-6,3],[-12,center],[-6,bridge_top],[-.15,bridge_top]]
    for i,p in enumerate(strip_polygons(bow_path,.3)):
        anchor=p[0];local=[[v[0]-anchor[0],v[1]-anchor[1]] for v in p];mid=f'H_Bridge_Wall_{i}'
        module(mid,[part('HULL',local,0,1.05),part('GLASS',local,1.05,2.55),part('HULL',local,2.55,3)])
        place(mid,mid,[anchor[0],0,anchor[1]],0,'BowWalls','BRIDGE')
    armor_path=[[45,-.6],[0,-.6],[-6.8,1],[-13.5,center],[-6.8,height-1],[0,height+.6],[45,height+.6]]
    armor_panels=strip_polygons(armor_path,.6)
    for i,p in enumerate(armor_panels):prism(f'H_OuterArmor_{i}',p,-.18,3.18,'HULL','Armor')
    # Clip the cap at the actual miter intersection, rather than overlapping its corner.
    join=min([p for p in armor_panels[0] if abs(p[1]+.3)<1e-5],key=lambda p:p[0])
    diag=armor_panels[1];j=min(range(len(diag)),key=lambda i:math.dist(diag[i],join));far=max([diag[(j-1)%len(diag)],diag[(j+1)%len(diag)]],key=lambda p:p[1])
    z_at_zero=join[1]+(0-join[0])*(far[1]-join[1])/(far[0]-join[0])
    cap_polys=[[[0,0],[45,0],[45,-.3],join,[0,z_at_zero]],[[0,height],[0,height-z_at_zero],[join[0],height+.3],[45,height+.3],[45,height]]]
    for i,cap in enumerate(cap_polys):
        for prefix,y0,y1,cat in [('Lower',-.18,0,'Armor'),('Upper',3,3.18,'Ceilings')]:
            prism(f'H_Rim_{prefix}_{i}',cap,y0,y1,'HULL',cat)
    inner_joints=[]
    for a,b in zip(armor_panels,armor_panels[1:]):
        shared=[v for v in a if any(math.dist(v,w)<1e-5 for w in b)]
        inner_joints.append(min(shared,key=lambda p:math.dist(p,[0,center])))
    outer_lower=[inner_joints[1],inner_joints[2]]
    lower_technical=[[0,3],[-6,3],[-12,center],outer_lower[1],outer_lower[0],[0,z_at_zero]]
    for side,poly in [('Lower',lower_technical),('Upper',[[x,height-z] for x,z in lower_technical])]:
        for i,triangle in enumerate(triangulate(poly)):
            prism(f'H_BowRoof_{side}_{i}',triangle,3,3.18,'HULL','Ceilings')
            prism(f'H_BowBase_{side}_{i}',triangle,-.18,0,'HULL','Armor')
    # Missing fixtures are intentionally simple, separate editable solids.
    bed=[box('METAL',[0,.12,0],[2.1,.35,1]),box('METAL',[.15,0,.1],[.35,.12,.9]),box('METAL',[1.75,0,.1],[1.95,.12,.9]),box('BED',[.12,.35,.05],[2.05,.55,.95]),box('LIGHT',[.2,.55,.13],[.55,.68,.87]),box('METAL',[0,.35,0],[.1,.95,1]),box('ACCENT',[.75,.55,.05],[2.05,.58,.95])]
    module('P_Bed',bed);module('P_MedBed',[dict(p,role='LIGHT' if p['role']=='BED' else p['role']) for p in bed])
    def desk(width):return [box('METAL',[0,.75,0],[width,.85,.8]),box('METAL',[.12,0,.12],[.25,.75,.68]),box('METAL',[width-.25,0,.12],[width-.12,.75,.68]),box('DARK',[.3,.85,.64],[min(width-.15,1.2),1.4,.75]),box('SCREEN',[.34,1.05,.61],[min(width-.19,1.16),1.36,.64])]
    module('P_Desk',desk(2.4));compact=desk(1.2)
    for p in compact:p['outline']=[v*.65 if i%2 else v for i,v in enumerate(p['outline'])]
    module('P_CabinDesk',compact)
    module('P_Locker',[box('METAL',[0,0,0],[.65,2.2,.6]),box('SCREEN',[.12,1.2,-.02],[.2,1.5,0])])
    module('P_Crate',[box('CRATE',[0,0,0],[1.2,1.05,1.2]),box('METAL',[.1,1.05,.1],[1.1,1.12,1.1])])
    module('P_Chair',[box('METAL',[.1,0,.1],[.5,.45,.5]),box('BED',[0,.45,0],[.6,.58,.6]),box('BED',[0,.58,.5],[.6,1.2,.6])])
    module('P_Reactor',[box('METAL',[0,0,0],[2.4,.2,2.4]),box('DARK',[.2,.2,.2],[2.2,2.4,2.2]),box('SCREEN',[.65,2.4,.65],[1.75,2.6,1.75]),box('ACCENT',[.65,.5,.15],[1.75,1.9,.2])])
    module('P_Server',[box('DARK',[0,0,0],[1.3,2.4,.8])]+[box('SCREEN',[.12,y,-.025],[1.18,y+.04,0]) for y in [.3,.7,1.1,1.5,1.9]])
    engine=[box('METAL',[0,1,-.6],[1.35,2,.6]),part('ENGINE',[[1.35,-.85],[1.85,-1.2],[6.85,-1.2],[7.35,-.85],[7.35,.85],[6.85,1.2],[1.85,1.2],[1.35,.85]],.25,2.65),box('DARK',[7.35,.6,-.85],[8.7,2.3,.85]),box('THRUST',[8.7,.7,-.7],[8.85,2.2,.7])]
    for x in [2.2,3.0,3.8,4.6,5.4,6.2]:engine.append(box('DARK',[x,2.65,-.9],[x+.12,2.72,.9]))
    module('P_Engine',engine)
    for i in range(5):place(f'ENGINE_{i+1:02d}','P_Engine',[48.15,0,1.5+i*(height-3)/4],0,'Engines')
    def prop(pid,mid,x,z,yaw=0,zid=''):place(pid,mid,[x,0,z],yaw,'Props',zid)
    for zoneinfo in zones:
        if zoneinfo['kind']!='cabin':continue
        x0,x1,z0,z1=zoneinfo['bounds'];zid=zoneinfo['id']
        right=int(zid[1:])%2==0
        prop(zid+'_BED','P_Bed',x0+(2.4 if right else .5),z0+1.8,zid=zid);prop(zid+'_LOCKER','P_Locker',x1-1.0 if right else x0+.5,z0+.3,zid=zid);prop(zid+'_DESK','P_CabinDesk',x0+3.3,z0+.35,zid=zid)
        zoneinfo['waypoint'][2]=z0+branch_length/2
    for i,x in enumerate([.8,3.3,5.8,9.3,11.8]):prop('BARRACK_BED_'+str(i),'P_Bed',x,north+4.5,zid='KOSZARY')
    for i,(x,z) in enumerate([(16.5,north+.7),(25.2,north+.7),(21.2,north+4.8)]):prop('LAB_BENCH_'+str(i),'P_Desk',x,z,zid='LAB')
    for i,x in enumerate([32,34.5,40,42.5]):prop('MED_BED_'+str(i),'P_MedBed',x,north+4.4,zid='MED')
    for i,(x,z) in enumerate([(1,1),(2.5,1),(4,1),(10,1),(11.5,1),(13,1),(2.2,4.4),(3,3),(10,3),(12,3)]):prop('CARGO_BOX_'+str(i),'P_Crate',x,z,zid='CARGO')
    for i,x in enumerate([17.2,25.4]):prop('REACTOR_'+str(i),'P_Reactor',x,1.6,zid='ENGINEERING')
    for i,x in enumerate([31.3,33.3,40.3,42.3]):prop('TECH_RACK_'+str(i),'P_Server',x,1.0,zid='TECH')
    for i,(x,z,yaw) in enumerate([(-7,center-1.2,-90),(-4,4.4,0),(-4,bridge_top-2.2,0)]):prop('BRIDGE_CONSOLE_'+str(i),'P_Desk',x,z,yaw,'BRIDGE')
    prop('CAPTAIN_SEAT','P_Chair',-5.8,center-.3,-90,'BRIDGE')
    materials={
        'HULL':[.075,.11,.15,1],'METAL':[.32,.4,.47,1],'DARK':[.07,.12,.17,1],
        'BED':[.22,.34,.4,1],'LIGHT':[.69,.77,.77,1],'ACCENT':[.84,.48,.13,1],
        'SCREEN':[.08,.7,.84,1],'GLASS':[.2,.59,.72,.38],'CRATE':[.38,.31,.2,1],
        'ENGINE':[.21,.28,.34,1],'THRUST':[.9,.44,.12,1]}
    return dict(version='C01.SHIP.3.1',reference='Reference/ship_plan.png',body=[0,45,0,height],corridor_width=3,branch_length=branch_length,bridge_outline=[v for p in bridge_poly for v in p],
                zones=zones,doors=doors,openings=openings,modules=mods,placements=placements,
                materials=[dict(role=k,color=v) for k,v in materials.items()],airlocks=[dict(id=n,doors=[d['id'] for d in doors if d['airlock']==n]) for n in ['D1','D2','D3','D4']])

if __name__=='__main__':
    ship=build();OUT.write_text(json.dumps(ship,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'{len(ship["zones"])} zones, {len(ship["doors"])} doors, {len(ship["placements"])} placements, {len(ship["modules"])} new module definitions')
