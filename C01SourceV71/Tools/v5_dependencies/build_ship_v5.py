"""Three-deck C01. World coordinates come from one assembly graph, never render offsets."""
import json,math,hashlib,collections
from pathlib import Path
from ship_geometry import ccw,clip_rect,strip_polygons,polygon_area,transform_poly
from models_v5 import make_models,part,box,PALETTE
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT.parent if (ROOT.parent/'Assets/C01ShipV5').is_dir() else ROOT/'UnityProject'
OUT=PROJECT/'Assets/C01ShipV5/Data/ship_v5.json'
Y={0:-12.4,1:0.,2:6.4};BOW=[[0,3],[0,42],[-12,42],[-24,22.5],[-12,3]]
SHAFTS=[[-6,-3,21,24],[66,69,21,24]]

def intervals(values):
    out=[]
    for a,b in sorted(values):
        if b-a<1e-6:continue
        if out and a<=out[-1][1]+1e-6:out[-1][1]=max(out[-1][1],b)
        else:out.append([a,b])
    return out

def vertical_modules(values):
    """Partition an occupied span into repeated 3 m panels plus an exact remainder."""
    for a,b in values:
        while b-a>1e-7:
            end=min(b,round(a+3,7))
            yield a,end
            a=end

def join_deck_intervals(values):
    """Wall ownership crosses the slab where two wall stories meet."""
    spans=intervals(values)
    for lower,upper in zip(spans,spans[1:]):
        if any(abs(lower[1]-a)<1e-6 and abs(upper[0]-b)<1e-6 for a,b in [(-.4,0),(3,3.4)]):
            lower[1]=upper[0]
    return intervals(spans)

def clip_along(poly, origin, axis, value, keep_above):
    def distance(p):return (p[0]-origin[0])*axis[0]+(p[1]-origin[1])*axis[1]-value
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da,db=distance(a),distance(b);ia=da>=-1e-9 if keep_above else da<=1e-9;ib=db>=-1e-9 if keep_above else db<=1e-9
        if ia:result.append(a)
        if ia!=ib:
            t=da/(da-db);result.append([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t])
    return clean(result) if len(result)>=3 else []
def cut_intervals(values,cuts):
    for lo,hi in cuts:
        out=[]
        for a,b in values:
            if hi<=a+1e-6 or lo>=b-1e-6:out.append([a,b]);continue
            if lo>a+1e-6:out.append([a,lo])
            if hi<b-1e-6:out.append([hi,b])
        values=out
    return values
def clean(poly):
    poly=ccw(poly)
    changed=True
    while changed and len(poly)>3:
        changed=False
        for i,b in enumerate(poly):
            a=poly[i-1];c=poly[(i+1)%len(poly)]
            if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<1e-7:
                poly.pop(i);changed=True;break
    return poly
def subtract(poly,rect):
    x0,x1,z0,z1=rect;M=10000
    pieces=[clip_rect(poly,-M,x0,-M,M),clip_rect(poly,x1,M,-M,M),clip_rect(poly,x0,x1,-M,z0),clip_rect(poly,x0,x1,z1,M)]
    return [clean(p) for p in pieces if p and polygon_area(p)>1e-7]
def subtract_all(poly,rects):
    polys=[poly]
    for r in rects:
        nxt=[]
        for p in polys:
            xs=[v[0] for v in p];zs=[v[1] for v in p]
            if max(xs)<=r[0]+1e-7 or min(xs)>=r[1]-1e-7 or max(zs)<=r[2]+1e-7 or min(zs)>=r[3]-1e-7:nxt.append(p)
            else:nxt.extend(subtract(p,r))
        polys=nxt
    return polys

def build():
    models=make_models();placements=[];zones=[];gates=[];locks=[];lifts=[];links=[];coverage=[]
    zone_map={};cells={0:{},1:{},2:{}};wall_ranges=collections.defaultdict(list);gate_cuts=collections.defaultdict(list);node_cuts=collections.defaultdict(list)
    def model(mid,parts):
        if mid not in models:models[mid]=dict(id=mid,parts=parts)
        return mid
    def place(pid,mid,x,y,z,yaw=0,category='Props',zone='',deck=-1,**extra):
        p=dict(id=pid,model=mid,category=category,zone=zone,deck=deck,x=round(x,7),y=round(y,7),z=round(z,7),yaw=yaw,parent='',gate='',buttonGate='',buttonLift='',buttonFloor=0,travel=[0,0,0]);p.update(extra);placements.append(p);return p
    def zone(zid,label,kind,deck,b,height,parent='',waypoint=None):
        labels={'GYM':'KOSZARY / TRENING','LAB':'LABORATORIUM','MED':'SEKTOR MEDYCZNY','CARGO':'MAGAZYN','ENGINE CONTROL':'MASZYNOWNIA / STEROWANIE','TECH':'SEKTOR TECHNICZNY','ENGINE ROOM':'MASZYNOWNIA GŁÓWNA','PURIFICATION':'OCZYSZCZALNIA','EVAC HANGAR':'HANGAR EWAKUACYJNY','HYDROPONICS':'UPRAWY ROŚLIN','MAIN_W':'KORYTARZ GŁÓWNY','MAIN_M':'KORYTARZ GŁÓWNY','MAIN_E':'KORYTARZ GŁÓWNY'}
        label=labels.get(label,label)
        z=dict(id=zid,label=label,kind=kind,deck=deck,floor=Y[deck],height=height,bounds=b,parent=parent,waypoint=waypoint or [(b[0]+b[1])/2,Y[deck],(b[2]+b[3])/2]);zones.append(z);zone_map[zid]=z
        return z
    def fill(z):
        b=z['bounds']
        for x in range(int(b[0]),int(b[1]),3):
            for zz in range(int(b[2]),int(b[3]),3):
                key=(x,zz)
                if key in cells[z['deck']] and not z['parent']:raise ValueError('Overlapping non-nested zone '+z['id'])
                cells[z['deck']][key]=z['id']
    def link(a,b,kind='opening',gate=''):
        if not any({l['a'],l['b']}=={a,b} and l['kind']==kind for l in links):links.append(dict(a=a,b=b,kind=kind,gate=gate))
    def gate(gid,a,b,axis,x,z,deck,width=3,height=6,airlock='',lift='',floor=-1):
        fy=Y[deck];yaw=0 if axis=='H' else -90;pocket=width/6;clear=width-2*pocket;step=clear/8;panel_width=step+.01
        frame_parts=([
            box('METAL',[.15,0,-.15],[.23,height,.15]),box('METAL',[width-.23,0,-.15],[width-.15,height,.15]),
            box('METAL',[.23,height-.2,-.15],[width-.23,height,.15])]+
            [box('DARK',[u,0,v],[w,height-.2,t]) for u,w in [(.23,pocket),(width-pocket,width-.23)] for v,t in [(-.15,-.09),(.09,.15)]])
        root_pos=[x,fy,z]
        def world(px,py,pz):
            p=transform_poly([[px,pz]],root_pos,yaw)[0];return [p[0],fy+py,p[1]]
        for index,p in enumerate(frame_parts):
            xs=p['outline'][::2];zs=p['outline'][1::2]
            for xi,(x0,x1) in enumerate(vertical_modules([(min(xs),max(xs))])):
                for yi,(y0,y1) in enumerate(vertical_modules([(p['y0'],p['y1'])])):
                    size=[round(x1-x0,7),round(y1-y0,7),round(max(zs)-min(zs),7)]
                    parts=[box(p['role'],[0,0,0],size)];key=hashlib.sha1(json.dumps(parts,sort_keys=True).encode()).hexdigest()[:12]
                    mid=model('G_Piece_'+key,parts);place(f'{gid}_FRAME_{index}_{xi}_{yi}',mid,*world(x0,y0,min(zs)),yaw,'GateFrames',a,deck)
        leaf_ids=[]
        for side in [0,1]:
            for i in range(4):
                px=pocket+i*step-.005 if side==0 else width/2+i*step-.005
                target=pocket-panel_width if side==0 else width-pocket
                pz=-.06+i*.04;travel=transform_poly([[target-px,0]],[0,0,0],yaw)[0]
                for yi,(y0,y1) in enumerate(vertical_modules([(0,height-.23)])):
                    h=round(y1-y0,7);parts=[box('ACCENT',[0,0,-.011],[.018,h,.011]),box('PANEL',[.018,0,-.011],[panel_width-.018,h,.011]),box('ACCENT',[panel_width-.018,0,-.011],[panel_width,h,.011])]
                    if y0<=.9 and y1>=1:parts.append(box('SCREEN',[.04,.9-y0,-.015],[panel_width-.04,1.0-y0,-.011]))
                    leaf=model(f'G_Leaf_W{round(panel_width*1000)}_H{round(h*1000)}_S{int(y0<=.9 and y1>=1)}',parts)
                    pid=f'{gid}_LEAF_{side}_{i}_{yi}';leaf_ids.append(pid);place(pid,leaf,*world(px,.02+y0,pz),yaw,'GateLeaves',a,deck,gate=gid,travel=[travel[0],0,travel[1]])
        button_ids=[]
        for side in [0,1]:
            wp=world(pocket-.28 if side==0 else pocket-.06,1.1,.15 if side==0 else -.15)
            pid=gid+'_BUTTON_'+str(side);button_ids.append(pid);place(pid,'P_Button',*wp,yaw+180*side,'Buttons',a,deck,buttonGate=gid,buttonLift=lift,buttonFloor=floor if floor>=0 else deck)
        g=dict(id=gid,deck=deck,x=x,y=fy,z=z,yaw=yaw,width=width,height=height,zones=[a,b],leaves=leaf_ids,buttons=button_ids,airlock=airlock,lift=lift,floor=floor);gates.append(g);link(a,b,'gate',gid)
        for offset in range(0,width,3):gate_cuts[(axis,x+offset if axis=='H' else x,z if axis=='H' else z+offset)].append([fy,fy+height])
        for offset in range(3,width,3):node_cuts[(x+offset if axis=='H' else x,z if axis=='H' else z+offset)].append([fy,fy+height])
        return gid

    # Residential decks, with nested bathrooms owning their own two floor squares.
    for deck in [1,2]:
        for i in range(3):
            x=i*21
            for side,z0,offset in [('N',24,0),('S',12,6)]:
                branch=zone(f'L{deck}_X{side}{i+1}','KORYTARZ BOCZNY','corridor',deck,[x+9,x+12,z0,z0+9],6);fill(branch)
                for j,rx in enumerate([x,x+12]):
                    number=offset+i*2+j+1;cid=f'L{deck}_C{number:02d}'
                    fill(zone(cid,f'KAJUTA {deck}{number:02d}','cabin',deck,[rx,rx+9,z0,z0+9],6,waypoint=[rx+4.5,Y[deck],z0+4.5]))
                    bid=cid+'_BATH';fill(zone(bid,'ŁAZIENKA','bathroom',deck,[rx,rx+6,z0+6,z0+9],6,parent=cid,waypoint=[rx+4.5,Y[deck],z0+7.5]))
                    gate(cid+'_GATE',cid,branch['id'],'V',rx+9 if j==0 else rx,z0+3,deck)
                    gate(cid+'_BATH_GATE',cid,bid,'H',rx+3,z0+6,deck)
        if deck==1:
            for i,(north,south) in enumerate([('GYM','CARGO'),('LAB','ENGINE_CONTROL'),('MED','TECH')]):
                x=i*21
                for name,b,wp in [(north,[x,x+21,33,45],[x+10.5,Y[deck],37.5]),(south,[x,x+21,0,12],[x+10.5,Y[deck],7.5])]:fill(zone('L1_'+name,name.replace('_',' '),'sector',1,b,12,waypoint=wp))
                gate('L1_SECTOR_N_'+str(i+1),'L1_'+north,f'L1_XN{i+1}','H',x+9,33,1)
                gate('L1_SECTOR_S_'+str(i+1),'L1_'+south,f'L1_XS{i+1}','H',x+9,12,1)
    # Lower deck service rooms, separated from the same 3m main spine.
    for name,b,wp in [('ENGINE_ROOM',[0,21,24,45],[10.5,-12.4,28.5]),('PURIFICATION',[21,42,24,45],[31.5,-12.4,28.5]),('EVAC_HANGAR',[42,63,24,45],[52.5,-12.4,28.5]),('CARGO',[0,21,0,21],[10.5,-12.4,16.5]),('HYDROPONICS',[21,63,0,21],[31.5,-12.4,16.5])]:fill(zone('L0_'+name,name.replace('_',' '),'sector',0,b,12,waypoint=wp))
    for i,name in enumerate(['ENGINE_ROOM','PURIFICATION','EVAC_HANGAR']):gate('L0_SERVICE_N_'+str(i),'L0_'+name,'L0_MAIN_W' if i==0 else 'L0_MAIN_M' if i==1 else 'L0_MAIN_E','H',i*21+9,24,0)
    for name,x,main in [('CARGO',9,'L0_MAIN_W'),('HYDROPONICS',30,'L0_MAIN_M')]:gate('L0_SERVICE_S_'+name,'L0_'+name,main,'H',x,21,0)
    for deck in [0,1,2]:
        for suffix,b in [('MAIN_W',[0,18,21,24]),('D1',[18,24,21,24]),('MAIN_M',[24,39,21,24]),('D2',[39,45,21,24]),('MAIN_E',[45,63,21,24])]:fill(zone(f'L{deck}_{suffix}',suffix,'airlock' if suffix.startswith('D') else 'corridor',deck,b,6))
        for name,x,left,right in [('D1',18,'MAIN_W','MAIN_M'),('D2',39,'MAIN_M','MAIN_E')]:
            lid=f'L{deck}_{name}';a=gate(lid+'_A',f'L{deck}_{left}',lid,'V',x,21,deck,airlock=lid);b=gate(lid+'_B',lid,f'L{deck}_{right}','V',x+6,21,deck,airlock=lid);locks.append(dict(id=lid,gates=[a,b]))
        zone(f'L{deck}_BRIDGE','MOSTEK / PION','core',deck,[-24,0,3,42],12 if deck==0 else 6,waypoint=[-1.5,Y[deck],22.5])
        zone(f'L{deck}_STERN','RUFA / PION ŚLUZ','core',deck,[63,75,0,45],12 if deck==0 else 6,waypoint=[64.5,Y[deck],22.5])
        gate(f'L{deck}_BRIDGE_MAIN',f'L{deck}_BRIDGE',f'L{deck}_MAIN_W','V',0,21,deck)
        gate(f'L{deck}_STERN_MAIN',f'L{deck}_STERN',f'L{deck}_MAIN_E','V',63,21,deck)
    # Sector chain connections and bridge/rear entrances.
    for deck,row,names in [(1,36,['GYM','LAB','MED']),(1,6,['CARGO','ENGINE_CONTROL','TECH']),(0,36,['ENGINE_ROOM','PURIFICATION','EVAC_HANGAR'])]:
        for i in [0,1]:gate(f'L{deck}_CHAIN_{row}_{i}',f'L{deck}_{names[i]}',f'L{deck}_{names[i+1]}','V',(i+1)*21,row,deck,height=12)
        for x,name,core in [(0,names[0],'BRIDGE'),(63,names[-1],'STERN')]:gate(f'L{deck}_{core}_SECTOR_{row}',f'L{deck}_{name}',f'L{deck}_{core}','V',x,row,deck)
    gate('L0_CARGO_GREEN','L0_CARGO','L0_HYDROPONICS','V',21,9,0,height=12)
    for deck in [0,1]:
        for x,name,core in [(0,'CARGO','BRIDGE'),(63,'HYDROPONICS' if deck==0 else 'TECH','STERN')]:
            if deck==0:gate(f'L{deck}_{core}_SOUTH',f'L{deck}_{name}',f'L{deck}_{core}','V',x,6,deck)
    # Nominal core outer walls. Body rear walls provide the shared x=0/63 boundary.
    for z in [0,45]:
        for x in range(63,75,3):wall_ranges[('H',x,z)].append([-12.4,12.4])
    for z in range(0,45,3):wall_ranges[('V',75,z)].append([-12.4,12.4])
    for name,inner,outer,pad in [('D3',42,45,'EXIT_N'),('D4',3,0,'EXIT_S')]:
        zid='L1_'+name;zone(zid,name,'airlock',1,[63,75,42,45] if name=='D3' else [63,75,0,3],6,parent='L1_STERN')
        zone('L1_'+pad,pad,'exterior',1,[66,72,45,48] if name=='D3' else [66,72,-3,0],6)
        for x in range(63,75,3):wall_ranges[('H',x,inner)].append([0,6])
        a=gate(zid+'_INNER','L1_STERN',zid,'H',66,inner,1,width=6,airlock=zid);b=gate(zid+'_OUTER',zid,'L1_'+pad,'H',66,outer,1,width=6,airlock=zid);locks.append(dict(id=zid,gates=[a,b]))
    zone('L0_DOCK','ŚLUZA EWAKUACYJNA','airlock',0,[63,75,33,42],12,parent='L0_STERN',waypoint=[64.5,-12.4,37.5])
    zone('L0_EXIT','PODEST EWAKUACYJNY','exterior',0,[75,87,33,42],12)
    for z in [33,42]:
        for x in range(63,75,3):wall_ranges[('H',x,z)].append([-12.4,-.4])
    gate('L0_DOCK_ACCESS','L0_STERN','L0_DOCK','H',63,33,0)
    # Replace the lower hangar->stern narrow portal with one wide actual craft portal.
    for gid in ['L0_STERN_SECTOR_36']:
        old_gate=next(g for g in gates if g['id']==gid);remove=set(old_gate['leaves']+old_gate['buttons']);placements[:]=[p for p in placements if p['id'] not in remove and not p['id'].startswith(gid+'_FRAME_')];gates.remove(old_gate);links[:]=[l for l in links if l['gate']!=gid]
        gate_cuts[('V',63,36)]=[v for v in gate_cuts[('V',63,36)] if v!=[-12.4,-6.4]]
    a=gate('L0_EVAC_INNER','L0_EVAC_HANGAR','L0_DOCK','V',63,33,0,width=9,height=12,airlock='L0_EVAC_LOCK');b=gate('L0_EVAC_OUTER','L0_DOCK','L0_EXIT','V',75,33,0,width=9,height=12,airlock='L0_EVAC_LOCK');locks.append(dict(id='L0_EVAC_LOCK',gates=[a,b]))

    # Build every required body boundary once per plane, then merge its vertical ownership.
    for deck,grid in cells.items():
        required={}
        for (x,z),zid in grid.items():
            for key,near in [(('H',x,z),(x,z-3)),(('H',x,z+3),(x,z+3)),(('V',x,z),(x-3,z)),(('V',x+3,z),(x+3,z))]:
                if key in required:continue
                other=grid.get(near,'')
                if key[0]=='V' and key[1]==0 and 3<=key[2]<42:other=f'L{deck}_BRIDGE'
                if key[0]=='V' and key[1]==63:other=f'L{deck}_STERN'
                if other==zid:continue
                za=zone_map[zid];zb=zone_map.get(other)
                if zb and za['kind']=='corridor' and zb['kind']=='corridor':link(zid,other);required[key]=None;continue
                h=max(za['height'],zb['height'] if zb and zb['kind'] not in ['core'] else za['height']);required[key]=(Y[deck],Y[deck]+h)
        for key,value in required.items():
            if value:wall_ranges[key].append(value)
    # Shaft walls have their own wall intervals; open face holds a gate at every landing.
    for lid,bounds,face in [('LIFT_BRIDGE',SHAFTS[0],'E'),('LIFT_STERN',SHAFTS[1],'W')]:
        x0,x1,z0,z1=bounds;cx=(x0+x1)/2;cz=(z0+z1)/2;landings=[];wps=[]
        for z in [z0,z1]:wall_ranges[('H',x0,z)].append([-12.4,12.4])
        for x in [x0,x1]:wall_ranges[('V',x,z0)].append([-12.4,12.4])
        for deck in [0,1,2]:
            core=f'L{deck}_'+('BRIDGE' if face=='E' else 'STERN');gid=lid+'_LANDING_'+str(deck)
            landings.append(gate(gid,core,core,'V',x1 if face=='E' else x0,z0,deck,lift=lid,floor=deck))
            wps.append(dict(position=[x1+.9 if face=='E' else x0-.9,Y[deck],cz]))
        car=lid+'_CAR';rail_x0,rail_x1=(-1.29,1.09) if face=='E' else (-1.09,1.29)
        car_model=model('P_LiftCar_'+face,[box('METAL',[-1.29,-.2,-1.29],[1.29,0,1.29]),box('DARK',[rail_x0,0,-1.29],[rail_x1,1.2,-1.23]),box('DARK',[rail_x0,0,1.23],[rail_x1,1.2,1.29])]+([box('DARK',[-1.29,0,-1.23],[-1.23,1.2,1.23])] if face=='E' else [box('DARK',[1.23,0,-1.23],[1.29,1.2,1.23])]))
        place(lid+'_PLATFORM',car_model,cx,0,cz,category='LiftCars',parent=car)
        for floor in [0,1,2]:place(lid+'_SELECT_'+str(floor),'P_Button',cx-.9+floor*.4,1.3,cz-1.23,category='Buttons',parent=car,buttonLift=lid,buttonFloor=floor)
        lifts.append(dict(id=lid,car=car,x=cx,z=cz,bounds=[cx-1.29,cx+1.29,cz-1.29,cz+1.29],startFloor=1,floors=[0,1,2],elevations=[-12.4,0,6.4],landings=landings,waypoints=wps))
        for deck in [0,1]:link(f'L{deck}_'+('BRIDGE' if face=='E' else 'STERN'),f'L{deck+1}_'+('BRIDGE' if face=='E' else 'STERN'),'lift')

    obstacles=[];node_ranges=collections.defaultdict(list)
    for (axis,x,z),values in wall_ranges.items():
        for a,b in join_deck_intervals(values):
            for node in [(x,z),(x+3,z) if axis=='H' else (x,z+3)]:node_ranges[node].append([a,b])
        for a,b in vertical_modules(cut_intervals(join_deck_intervals(values),gate_cuts[(axis,x,z)])):
            h=round(b-a,7);mid=f'W3_H{round(h*1000)}'
            model(mid,[box('METAL',[.15,0,-.15],[2.85,min(.12,h),.15]),box('METAL',[.15,max(.12,h-.12),-.15],[2.85,h,.15])]+([box('WALL',[.15,.12,-.10],[2.85,h-.12,.10]),box('PANEL',[.15,.12,-.15],[2.85,h-.12,-.10]),box('PANEL',[.15,.12,.10],[2.85,h-.12,.15])] if h>.32 else []))
            place(f'W_{axis}_{x}_{z}_{a}',mid,x,a,z,0 if axis=='H' else -90,'Walls',deck=-1)
            obstacles.append((a,b,[x+.15,x+2.85,z-.15,z+.15] if axis=='H' else [x-.15,x+.15,z+.15,z+2.85]))
    # The 12.4m bridge shell meets 12m sector walls at two rear corner nodes.
    # Their extensions close the roof-step junction and participate in slab clipping.
    for z in [3,42]:node_ranges[(0,z)].append([12,12.4])
    for (x,z),values in node_ranges.items():
        for a,b in vertical_modules(cut_intervals(intervals(values),node_cuts[(x,z)])):
            h=b-a;mid=model('N_H'+str(round(h*1000)),[box('METAL',[-.15,0,-.15],[.15,h,.15])]);place(f'N_{x}_{z}_{a}',mid,x,a,z,category='Nodes')
            obstacles.append((a,b,[x-.15,x+.15,z-.15,z+.15]))
    # Single continuous shell around the bow; rear wall is owned by the body graph.
    path=[[-.15,3],[-12,3],[-24,22.5],[-12,42],[-.15,42]]
    bow_strips=strip_polygons(path,.3)
    for i,poly in enumerate(bow_strips):
        bands=[(-12.4,-11.3,'HULL'),(-11.3,-9.4,'GLASS'),(-9.4,1.1,'HULL'),(1.1,3,'GLASS'),(3,7.5,'HULL'),(7.5,9.4,'GLASS'),(9.4,12.4,'HULL')]
        origin=path[i];dx=path[i+1][0]-origin[0];dz=path[i+1][1]-origin[1];length=math.hypot(dx,dz);axis=[dx/length,dz/length]
        distances=[(p[0]-origin[0])*axis[0]+(p[1]-origin[1])*axis[1] for p in poly]
        for xi,(a,b) in enumerate(vertical_modules([(min(distances),max(distances))])):
            clipped=clip_along(clip_along(poly,origin,axis,a,True),origin,axis,b,False)
            if not clipped:continue
            anchor=[origin[0]+axis[0]*a,origin[1]+axis[1]*a];local=[[round(x-anchor[0],7),round(z-anchor[1],7)] for x,z in clipped]
            for yi,(y0,y1) in enumerate(vertical_modules([(-12.4,12.4)])):
                parts=[part(role,local,round(max(ba,y0)-y0,7),round(min(bb,y1)-y0,7)) for ba,bb,role in bands if min(bb,y1)-max(ba,y0)>1e-7]
                key=hashlib.sha1(json.dumps(parts,sort_keys=True).encode()).hexdigest()[:12];mid=model('H_BOW_'+key,parts)
                place(f'H_BOW_{i}_{xi}_{yi}',mid,anchor[0],y0,anchor[1],category='Hull')
        # Exact convex footprints are retained for clipping outside the body tile grid.
        obstacles.append((-12.4,12.4,[min(x for x,z in poly),max(x for x,z in poly),min(z for x,z in poly),max(z for x,z in poly)],poly))

    # Horizontal slabs: body ownership plus core/exit footprints, minus actual crossing solids.
    kit=json.loads((ROOT/'Reference/kit_v3.json').read_text(encoding='utf-8'));tile=next(m for m in kit['modules'] if m['id']=='F01_Floor_3m')['parts']
    floor_regions=[]
    for deck,grid in cells.items():
        for (x,z),zid in grid.items():floor_regions.append((deck,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],zid))
    for deck in [0,1,2]:
        for x in range(-24,0,3):
            for z in range(3,42,3):
                p=clip_rect(BOW,x,x+3,z,z+3)
                if p and (deck!=2 or x==-3):floor_regions.append((deck,x,z,p,f'L{deck}_BRIDGE'))
        for x in range(63,75,3):
            for z in range(0,45,3):
                if deck==2 and 66<=x<72 and 3<=z<42:continue
                floor_regions.append((deck,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],f'L{deck}_STERN'))
    for zid in ['L0_EXIT','L1_EXIT_N','L1_EXIT_S']:
        b=zone_map[zid]['bounds'];deck=zone_map[zid]['deck']
        for x in range(b[0],b[1],3):
            for z in range(b[2],b[3],3):floor_regions.append((deck,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],zid))
    def floor_role(zid):
        z=zone_map[zid];k=z['kind']
        if k=='cabin':return 'F_CABIN'
        if k=='bathroom':return 'F_BATH'
        return next((role for suffix,role in [('GYM','F_GYM'),('LAB','F_LAB'),('MED','F_MED'),('CARGO','F_CARGO'),('ENGINE_CONTROL','F_CONTROL'),('TECH','F_TECH'),('ENGINE_ROOM','F_ENGINE'),('PURIFICATION','F_PURIFY'),('EVAC_HANGAR','F_HANGAR'),('HYDROPONICS','F_HYDRO')] if zid.endswith(suffix)),'FLOOR')
    # Convex hull-strip subtraction uses half-plane rectangles only for axis-aligned walls;
    # bow floor polygons terminate at their inner face using the parallel smaller polygon.
    inner_joints=[]
    for a,b in zip(bow_strips,bow_strips[1:]):
        common=[p for p in a if any(math.dist(p,q)<1e-6 for q in b)]
        inner_joints.append(min(common,key=lambda p:math.dist(p,[0,22.5])))
    inner_bow=[[0,3.15]]+inner_joints+[[0,41.85]]
    def slab(pid,deck,x,z,poly,top,thickness,role,category,zid,holes=True):
        rects=[]
        if holes:rects.extend(SHAFTS)
        for obstacle in obstacles:
            a,b,r,*extra=obstacle
            if top<=a+1e-6 or top-thickness>=b-1e-6:continue
            if extra:continue
            if max(v[0] for v in poly)<=r[0] or min(v[0] for v in poly)>=r[1] or max(v[1] for v in poly)<=r[2] or min(v[1] for v in poly)>=r[3]:continue
            rects.append(r)
        polys=subtract_all(poly,rects)
        if not polys:return
        parts=[]
        for p in polys:
            local=[[a-x,b-z] for a,b in p]
            parts.append(part('METAL' if category=='Floors' else 'HULL',local,-thickness,-.02 if category=='Floors' else 0))
            if category=='Floors':
                for t in tile[1:]:
                    lo=t['lo'];hi=t['hi'];q=clip_rect(p,x+lo[0],x+hi[0],z+lo[2],z+hi[2])
                    if q:parts.append(part('TRIM' if t['role']=='TRIM' else role,[[a-x,b-z] for a,b in clean(q)],-.02,0))
            coverage.append(dict(id=pid+'_'+str(len(coverage)),deck=deck,plane=top if category=='Floors' else top-thickness,normal='up' if category=='Floors' else 'down',poly=[v for pt in p for v in pt]))
            if category=='Floors' and deck>0:coverage.append(dict(id=pid+'_underside_'+str(len(coverage)),deck=deck-1,plane=top-thickness,normal='down',poly=[v for pt in p for v in pt]))
        key=hashlib.sha1(json.dumps(parts,sort_keys=True).encode()).hexdigest()[:12];mid=model(('F_' if category=='Floors' else 'C_')+key,parts);place(pid,mid,x,top,z,category=category,zone=zid,deck=deck)
    for deck,x,z,poly,zid in floor_regions:
        # Crossed bow walls need exact intersection with the inner offset polygon at upper slabs.
        if x<0 and deck>0:
            clipped=clip_rect(inner_bow,x,x+3,z,z+3)
            if not clipped:continue
            poly=clipped
        slab(f'F_L{deck}_{x}_{z}',deck,x,z,poly,Y[deck],.4,floor_role(zid),'Floors',zid)
    # Fixed, clipped landing sills bridge the platform clearance without entering its swept volume.
    for lift in lifts:
        bridge=lift['id']=='LIFT_BRIDGE';face=-3 if bridge else 66;edge=lift['bounds'][1] if bridge else lift['bounds'][0]
        rect=[edge,face,21.2,23.8] if bridge else [face,edge,21.2,23.8]
        for deck in [0,1,2]:
            top=Y[deck];poly=[[rect[0],rect[2]],[rect[1],rect[2]],[rect[1],rect[3]],[rect[0],rect[3]]]
            cuts=[o[2] for o in obstacles if len(o)==3 and top>o[0]+1e-6 and top-.2<o[1]-1e-6]
            pieces=subtract_all(poly,cuts);parts=[part('METAL',[[x-face,z-21.2] for x,z in p],-.2,0) for p in pieces]
            if parts:
                mid=model('SILL_'+lift['id']+'_'+str(deck),parts);pid='SILL_'+lift['id']+'_'+str(deck);place(pid,mid,face,top,21.2,category='Floors',zone=f'L{deck}_'+('BRIDGE' if bridge else 'STERN'),deck=deck)
                for p in pieces:coverage.append(dict(id=pid,deck=deck,plane=top,normal='up',poly=[v for pt in p for v in pt]))
    # Lower corridor roof is below the 12m service-room overhead volume.
    for (x,z),zid in cells[0].items():
        if zone_map[zid]['kind'] in ['corridor','airlock']:slab(f'C_L0_{x}_{z}',0,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],Y[0]+6+.2,.2,'HULL','Ceilings',zid)
    # Sectors have 12m clear roofs; upper cabins/corridors 6m. Roofs also cover core atria.
    for deck in [1,2]:
        for (x,z),zid in cells[deck].items():
            if deck==1 and zone_map[zid]['kind']!='sector':continue
            top=Y[deck]+zone_map[zid]['height']+.2
            slab(f'C_L{deck}_{x}_{z}',deck,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],top,.2,'HULL','Ceilings',zid)
    for x in range(-24,0,3):
        for z in range(3,42,3):
            poly=clip_rect(inner_bow,x,x+3,z,z+3)
            if poly:slab(f'C_CORE_B_{x}_{z}',2,x,z,poly,12.6,.2,'HULL','Ceilings','L2_BRIDGE',holes=False)
    for x in range(63,75,3):
        for z in range(0,45,3):slab(f'C_CORE_S_{x}_{z}',2,x,z,[[x,z],[x+3,z],[x+3,z+3],[x,z+3]],12.6,.2,'HULL','Ceilings','L2_STERN',holes=False)
    # Upper galleries have solid guard panels along their void edges, never invisible fall barriers.
    rail=model('P_Rail3',[box('METAL',[.15,.10,-.04],[2.85,1.2,.04])]);rail_nodes=set()
    def rail_at(pid,x,z,yaw,zid):
        place(pid,rail,x,6.4,z,yaw,'Railings',zid,2);end=transform_poly([[3,0]],[x,0,z],yaw)[0];rail_nodes.update([(x,z),(round(end[0],6),round(end[1],6))])
    for z in range(3,42,3):
        if z!=21:rail_at('RAIL_B_'+str(z),-3,z,-90,'L2_BRIDGE');rail_at('RAIL_S_W_'+str(z),66,z,-90,'L2_STERN')
        rail_at('RAIL_S_E_'+str(z),72,z,-90,'L2_STERN')
    for z in [3,42]:
        for x in [66,69]:rail_at(f'RAIL_S_{x}_{z}',x,z,0,'L2_STERN')
    post=model('P_RailPost',[box('METAL',[-.15,0,-.15],[.15,1.2,.15])])
    for x,z in sorted(rail_nodes):
        if (x,z) in {(-3,3),(-3,42),(-3,21),(-3,24),(66,21),(66,24)}:continue
        place(f'RP_{x}_{z}',post,x,6.4,z,category='Railings',zone='L2_BRIDGE' if x<0 else 'L2_STERN',deck=2)
    # Fixtures are not stretched when rooms enlarge.
    def prop(pid,mid,x,z,zid,yaw=0):return place(pid,mid,x,zone_map[zid]['floor'],z,yaw,'Props',zid,zone_map[zid]['deck'])
    # Vertical sector galleries, independent 3 m modules and accessible service ducts.
    for zid in ['L1_GYM','L1_LAB','L1_MED','L1_CARGO','L1_ENGINE_CONTROL','L1_TECH','L0_ENGINE_ROOM','L0_PURIFICATION','L0_EVAC_HANGAR','L0_CARGO','L0_HYDROPONICS']:
        x0,x1,z0,z1=zone_map[zid]['bounds']
        deck=zone_map[zid]['deck'];floor=zone_map[zid]['floor'];offset=14 if zid=='L0_HYDROPONICS' else 5
        if deck==1:zone_map[zid]['waypoint']=[x0+10.5,floor,z0+1.5]
        if zid=='L0_HYDROPONICS':zone_map[zid]['waypoint']=[x0+12,floor,z0+19.5]
        for i in range(4):place(zid+'_STAIR_'+str(i),'P_Stair_3m',x0+3+i*3,floor+i*1.5,z0+offset,category='Structures',zone=zid,deck=deck)
        place(zid+'_MEZZANINE','P_Mezzanine_3m',x0+15,floor+6,z0+offset,category='Structures',zone=zid,deck=deck)
        for i in range(2):place(zid+'_LADDER_'+str(i),'P_Ladder_3m',x0+17,floor+3*i,z0+offset+3,category='Structures',zone=zid,deck=deck)
        for i in range(2):place(zid+'_VENT_'+str(i),'P_Vent_3m',x0+9+3*i,floor+6,z0+offset+1.4,category='Ventilation',zone=zid,deck=deck)
        place(zid+'_VENT_END','P_VentCap',x0+9,floor+6,z0+offset+1.4,category='Ventilation',zone=zid,deck=deck)
    for zn in [z for z in zones if z['kind']=='cabin']:
        x0,x1,z0,z1=zn['bounds'];zid=zn['id']
        for i,(x,z) in enumerate([(.6,.6),(.6,2.5),(5.8,.6),(5.8,2.5)]):prop(zid+'_BED_'+str(i),'P_Bed',x0+x,z0+z,zid)
        for i,(x,z) in enumerate([(x,z) for x in [6.25,8.15] for z in [5.8,6.6,7.4,8.2]]):prop(zid+'_LOCKER_'+str(i),'P_Locker',x0+x,z0+z,zid)
        for mid,x,z in [('P_Shower',.5,6.4),('P_Toilet',.8,7.85),('P_Sink',2.1,8.0)]:prop(zid+'_'+mid,mid,x0+x,z0+z,zid+'_BATH')
    for i,(mid,x,z) in enumerate([('P_Treadmill',2,35),('P_Treadmill',6,35),('P_Rowing',13,35),('P_Rowing',16,39),('P_Pullup',2,41),('P_Weights',7,41)]):prop('GYM_'+str(i),mid,x,z,'L1_GYM')
    for i,(mid,x,z) in enumerate([('P_ExamScanner',44,40),('P_Analyser',49,40),('P_Analyser',55,40),('P_ExamChair',57,35),('P_MedBed',44,35),('P_MedBed',48,35)]):prop('MED_'+str(i),mid,x,z,'L1_MED')
    for zid in ['L1_LAB','L1_ENGINE_CONTROL']:
        b=zone_map[zid]['bounds']
        for i,(x,z) in enumerate([(b[0]+2,b[2]+2),(b[0]+14,b[2]+2),(b[0]+2,b[2]+8),(b[0]+14,b[2]+8)]):prop(zid+'_CONSOLE_'+str(i),'P_Desk',x,z,zid)
    for i,(x,z) in enumerate([(2,33),(13,33)]):prop('CORE_REACTOR_'+str(i),'P_ReactorLarge',x,z,'L0_ENGINE_ROOM')
    for i,(x,z) in enumerate([(23,35),(32,35),(23,40),(32,40)]):prop('PURIFIER_'+str(i),'P_Purifier',x,z,'L0_PURIFICATION')
    for i,(x,z) in enumerate([(x,z) for x in [24,27,30,36,39,42,48,51,54,60] for z in [2,5,8,11]]):prop('PLANT_'+str(i),'P_Plant',x,z,'L0_HYDROPONICS')
    prop('EVAC_SHUTTLE','P_Shuttle',48,34.5,'L0_EVAC_HANGAR')
    for zid in ['L1_CARGO','L0_CARGO']:
        b=zone_map[zid]['bounds']
        for i,(x,z) in enumerate([(b[0]+2,b[2]+2),(b[0]+5,b[2]+2),(b[0]+14,b[2]+2),(b[0]+17,b[2]+5)]):prop(zid+'_CRATE_'+str(i),'P_Crate',x,z,zid)
    for i,x in enumerate([44,48,55,59]):prop('TECH_SERVER_'+str(i),'P_Server',x,3,'L1_TECH')
    for i,(x,z) in enumerate([(-12,16),(-12,27),(-7,8)]):prop('BRIDGE_CONSOLE_'+str(i),'P_Desk',x,z,'L1_BRIDGE')
    for i,z in enumerate([1.5,12,22.5,33,43.5]):place('ENGINE_'+str(i+1),'P_Engine',75.15,0,z,category='Engines')
    # Formal assembly sockets are nominal construction contacts, not mesh bounding-box offsets.
    import re
    for mid,m in models.items():
        xs=[v for p in m['parts'] for v in p['outline'][::2]];zs=[v for p in m['parts'] for v in p['outline'][1::2]];ys=[v for p in m['parts'] for v in [p['y0'],p['y1']]]
        family='wall' if mid.startswith('W3_') else 'gate_frame' if mid.startswith('G_Frame') else 'floor' if mid.startswith('F_') else 'ceiling' if mid.startswith('C_') else 'node' if mid.startswith('N_') else 'hull' if mid.startswith('H_') else 'prop'
        m['family']=family;m['nominal']=[max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs)]
        m['sockets']=[dict(name='Socket_Origin',kind=family,position=[0,0,0],normal=[0,1,0])]
        if family in ['wall','gate_frame']:
            width=int(re.search(r'W(\d+)',mid).group(1)) if family=='gate_frame' else 3;m['nominal'][0]=width
            m['sockets'] += [dict(name='Socket_Start',kind='wall_edge',position=[0,0,0],normal=[-1,0,0]),dict(name='Socket_End',kind='wall_edge',position=[width,0,0],normal=[1,0,0])]
        elif family in ['floor','ceiling']:
            m['nominal']=[3,.4 if family=='floor' else .2,3]
            m['sockets'] += [dict(name='Socket_EndX',kind='tile_edge',position=[3,0,0],normal=[1,0,0]),dict(name='Socket_EndZ',kind='tile_edge',position=[0,0,3],normal=[0,0,1]),dict(name='Socket_Bottom',kind='deck_plane',position=[0,-m['nominal'][1],0],normal=[0,-1,0])]
    return dict(version='C01.SHIP.5.0',unit=3,body=[0,63,0,45],decks=[dict(id=i,y=Y[i]) for i in [0,1,2]],materials=[dict(role=k,color=v) for k,v in PALETTE.items()],models=list(models.values()),placements=placements,zones=zones,gates=gates,airlocks=locks,lifts=lifts,links=links,coverage=coverage)

if __name__=='__main__':
    data=build();OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:len(data[k]) for k in ['models','placements','zones','gates','lifts','coverage']}))
