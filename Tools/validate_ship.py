import json,math,sys
from pathlib import Path
from collections import Counter,defaultdict,deque
from ship_geometry import polygon_area,clip_rect,transform_poly,overlap_poly
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT/'UnityProject'
QA=ROOT/'C01Ship_QA' if PROJECT==ROOT else ROOT/'QA'
BASE=json.loads((PROJECT/'Assets/C01Modular/Data/kit.json').read_text())

def floor_polygons(ship):
    mods={m['id']:m for m in ship['modules']};out=[]
    for p in ship['placements']:
        if p['category']!='Floors':continue
        if p['module'].startswith(('F01_','F02_')):poly=[[0,0],[3,0],[3,3],[0,3]]
        else:
            values=mods[p['module']]['parts'][0]['outline'];poly=list(map(list,zip(values[::2],values[1::2])))
        out.append((p['id'],transform_poly(poly,[p['x'],p['y'],p['z']],p['yaw'])))
    return out

def validate(ship):
    errors=[];counts={};pmap={p['id']:p for p in ship['placements']};zmap={z['id']:z for z in ship['zones']}
    def check(ok,text):
        if not ok:errors.append(text)
    check(len(pmap)==len(ship['placements']),'Duplicate placement / shared node')
    check(ship['body']==[0,45,0,33],'Expanded body must be 45 x 33 m')
    check(len([z for z in ship['zones'] if z['kind']=='cabin'])==12,'Expected 12 cabins')
    check({z['id'] for z in ship['zones'] if z['kind']=='sector'}=={'KOSZARY','LAB','MED','CARGO','ENGINEERING','TECH'},'Sector family mismatch')
    check(sum(p['module']=='P_Engine' for p in ship['placements'])==5,'Expected 5 engines')
    check(len(ship['doors'])==36,'Reference has 36 separate doors')
    expected_links=set()
    for row,offset,side in [(18,0,'N'),(6,6,'S')]:
        for pair in range(3):
            for j in range(2):
                cabin=f'C{offset+2*pair+j+1:02d}';other=f'X{side}{pair+1}';expected_links.add(frozenset([cabin,other]))
                z=zmap.get(cabin,{});x=pair*15+(9 if j else 0)
                check(z.get('bounds')==[x,x+6,row,row+9],'Cabin bounds '+cabin)
                ds=[d for d in ship['doors'] if cabin in d['zones']];check(len(ds)==1 and other in ds[0]['zones'],'Cabin entry is not exclusively transverse '+cabin)
    for pair in range(3):
        expected_links.add(frozenset([['KOSZARY','LAB','MED'][pair],'XN'+str(pair+1)]));expected_links.add(frozenset([['CARGO','ENGINEERING','TECH'][pair],'XS'+str(pair+1)]))
        for side,row in [('N',18),('S',6)]:
            check(zmap.get(f'X{side}{pair+1}',{}).get('bounds')==[pair*15+6,pair*15+9,row,row+9],'Side corridor width/length')
    for zid in ['MAIN_W','MAIN_M','MAIN_E','D1','D2']:
        b=zmap[zid]['bounds'];check(b[2:]==[15,18],'Main corridor width/position '+zid)
    check(zmap['STERN']['bounds']==[45,48,3,30],'Stern corridor width/length')
    for a,b in [('KOSZARY','LAB'),('LAB','MED'),('CARGO','ENGINEERING'),('ENGINEERING','TECH'),('BRIDGE','KOSZARY'),('BRIDGE','MAIN_W'),('BRIDGE','CARGO'),('STERN','MED'),('STERN','MAIN_E'),('STERN','TECH'),('MAIN_W','D1'),('D1','MAIN_M'),('MAIN_M','D2'),('D2','MAIN_E'),('STERN','D3'),('D3','EXIT_N'),('STERN','D4'),('D4','EXIT_S')]:expected_links.add(frozenset([a,b]))
    check({frozenset(d['zones']) for d in ship['doors']}==expected_links,'Door adjacency differs from reference')
    for zid,b in [('D1',[12,18,15,18]),('D2',[27,33,15,18]),('D3',[45,48,30,33]),('D4',[45,48,0,3])]:check(zmap.get(zid,{}).get('bounds')==b,'Airlock position '+zid)
    for d in ship['doors']:
        p=pmap.get(d['id']);check(p is not None and p['module']=='W04_DoorWall_3m' and [p['x'],p['z'],p['yaw']]==[d.get('root_x',d['x']),d.get('root_z',d['z']),d['yaw']],'Missing or displaced physical door '+d['id'])
    # Independently derive every required body boundary from reference zone cells.
    cells={}
    for z in ship['zones']:
        if z['id']=='BRIDGE' or z['kind']=='exterior':continue
        x0,x1,z0,z1=z['bounds']
        for x in range(x0,x1,3):
            for zz in range(z0,z1,3):
                check((x,zz) not in cells,'Overlapping zone cells');cells[x,zz]=z['id']
    required={};allowed_open=set();dkeys={(d['axis'],d['x'],d['z']) for d in ship['doors']}
    for (x,z),zid in cells.items():
        for key,neighbor in [(('H',x,z),(x,z-3)),(('H',x,z+3),(x,z+3)),(('V',x,z),(x-3,z)),(('V',x+3,z),(x+3,z))]:
            nz=cells.get(neighbor,'')
            if key[0]=='V' and key[1]==0 and 3<=key[2]<30:nz='BRIDGE'
            if zid==nz:continue
            if key not in dkeys and nz and zmap[zid]['kind']=='corridor' and zmap[nz]['kind']=='corridor':allowed_open.add(key)
            else:required[key]=[zid,nz]
    from geometry import point
    def wall_key(p):
        end=point([3,0,0],[p['x'],p['y'],p['z']],p['yaw'])
        return ('H' if abs(end[2]-p['z'])<1e-5 else 'V',round(min(p['x'],end[0]),6),round(min(p['z'],end[2]),6))
    actual=Counter(wall_key(p) for p in ship['placements'] if p['category']=='Walls')
    check(set(actual)==set(required),'Missing/extra boundary wall');check(all(v==1 for v in actual.values()),'Duplicated wall')
    nodes=Counter((p['x'],p['z']) for p in ship['placements'] if p['category']=='Nodes');endpoints=set()
    for axis,x,z in required:endpoints|={(x,z),(x+3,z) if axis=='H' else (x,z+3)}
    check(set(nodes)==endpoints and all(v==1 for v in nodes.values()),'Missing/duplicate shared junction')
    expected_cells={(x,z) for x in range(0,48,3) for z in range(0,33,3)}|{(45,-3),(45,33)}
    canonical_bow=[[0,3],[0,30],[-6,30],[-12,16.5],[-6,3]]
    for x in range(-12,0,3):
        for z in range(3,30,3):
            if clip_rect(canonical_bow,x,x+3,z,z+3):expected_cells.add((x,z))
    floors=[p for p in ship['placements'] if p['category']=='Floors'];check({(p['x'],p['z']) for p in floors}==expected_cells and len(floors)==len(expected_cells),'Floor cells incomplete')
    polys=dict(floor_polygons(ship));area=0
    for p in floors:
        poly=polys[p['id']];a=polygon_area(poly);area+=a
        expected_area=polygon_area(clip_rect(canonical_bow,p['x'],p['x']+3,p['z'],p['z']+3)) if p['x']<0 else 9
        check(abs(a-expected_area)<1e-5,'Bow/floor coverage '+p['id']);check(p['y']==0 and p['yaw']==0,'Floor not level '+p['id'])
    check(abs(area-1845)<1e-5,'Incorrect total floor area')
    ceilings=[p for p in ship['placements'] if p['category']=='Ceilings' and p['zone']];check(len(ceilings)==len(expected_cells)-2,'Missing interior ceiling')
    check({(p['x'],p['z']) for p in ceilings}==expected_cells-{(45,-3),(45,33)},'Missing/duplicate ceiling cells')
    check(all(p['y']==3 and p['yaw']==0 for p in ceilings),'Ceiling not level')
    graph=defaultdict(set)
    for link in ship['doors']+ship['openings']:
        a,b=link['zones'];graph[a].add(b);graph[b].add(a)
    reached={'BRIDGE'};q=deque(reached)
    while q:
        for v in graph[q.popleft()]:
            if v not in reached:reached.add(v);q.append(v)
    check(set(zmap)<=reached,'Disconnected rooms: '+str(set(zmap)-reached))
    counts.update(zones=len(zmap),cabins=12,doors=len(ship['doors']),engines=sum(p['module']=='P_Engine' for p in ship['placements']),floor_tiles=len(floors),floor_area_m2=area,walls=sum(actual.values()),nodes=sum(nodes.values()),reachable_zones=len(reached))
    return dict(status='PASS' if not errors else 'FAIL',errors=errors,counts=counts)

def world_solids(ship,angle=0):
    base={m['id']:m for m in BASE['modules']};custom={m['id']:m for m in ship['modules']};solids=[]
    def add(mid,pos,yaw,owner,category):
        m=base.get(mid) or custom[mid]
        for i,p in enumerate(m['parts']):
            if 'lo' in p:
                poly=[[p['lo'][0],p['lo'][2]],[p['hi'][0],p['lo'][2]],[p['hi'][0],p['hi'][2]],[p['lo'][0],p['hi'][2]]];lo=p['lo'][1];hi=p['hi'][1]
            else:poly=[list(v) for v in zip(p['outline'][::2],p['outline'][1::2])];lo=p['y0'];hi=p['y1']
            poly=transform_poly(poly,pos,yaw);solids.append(dict(poly=poly,lo=lo+pos[1],hi=hi+pos[1],owner=owner,part=i,category=category,role=p['role'],moving=mid=='D02_Door_Hinged',xmin=min(v[0] for v in poly),xmax=max(v[0] for v in poly),zmin=min(v[1] for v in poly),zmax=max(v[1] for v in poly)))
        for c in m.get('children',[]):
            local=c['position'];pt=transform_poly([[local[0],local[2]]],pos,yaw)[0]
            add(c['module'],[pt[0],pos[1]+local[1],pt[1]],yaw+c.get('yaw',0)+(angle if c['module']=='D02_Door_Hinged' else 0),owner+'/'+c['socket'],category)
    for p in ship['placements']:add(p['module'],[p['x'],p['y'],p['z']],p['yaw'],p['id'],p['category'])
    return solids

def geometry_audit(ship):
    result={};errors=[]
    for pose in [0,90]:
        solids=sorted(world_solids(ship,pose),key=lambda p:p['xmin']);hits=[]
        for i,a in enumerate(solids):
            for b in solids[i+1:]:
                if b['xmin']>=a['xmax']-1e-5:break
                if min(a['hi'],b['hi'])-max(a['lo'],b['lo'])<=1e-5 or min(a['zmax'],b['zmax'])-max(a['zmin'],b['zmin'])<=1e-5:continue
                if overlap_poly(a['poly'],b['poly']):hits.append([a['owner'],a['part'],b['owner'],b['part']])
        result[str(pose)]=dict(solids=len(solids),penetrations=len(hits),examples=hits[:25]);errors.extend(hits[:25])
    return dict(status='PASS' if not errors else 'FAIL',poses=result)

def sweep_audit(ship):
    from geometry import point
    base_by_id={p['id']:p for p in ship['placements']};static=[s for s in world_solids(ship,0) if not s['moving']];failures=defaultdict(int);examples=[];poses={};tests=0
    def shape(poly,y0,y1,pos,yaw):
        p=transform_poly(poly,pos,yaw);return dict(poly=p,lo=y0+pos[1],hi=y1+pos[1],xmin=min(v[0] for v in p),xmax=max(v[0] for v in p),zmin=min(v[1] for v in p),zmax=max(v[1] for v in p))
    def hit(a,b):
        return min(a['hi'],b['hi'])-max(a['lo'],b['lo'])>1e-5 and min(a['xmax'],b['xmax'])-max(a['xmin'],b['xmin'])>1e-5 and min(a['zmax'],b['zmax'])-max(a['zmin'],b['zmin'])>1e-5 and overlap_poly(a['poly'],b['poly'])
    hinges={}
    for d in ship['doors']:
        p=base_by_id.get(d['id'])
        if p is None:continue
        hinge=point([.66,.02,0],[p['x'],p['y'],p['z']],p['yaw']);hinges[d['id']]=hinge
        nearby=[s for s in static if s['xmax']>hinge[0]-1.8 and s['xmin']<hinge[0]+1.8 and s['zmax']>hinge[2]-1.8 and s['zmin']<hinge[2]+1.8 and s['lo']<2.36 and s['hi']>.02]
        states=[]
        for angle in range(91):
            body=shape([[0,-.03],[1.68,-.03],[1.68,.03],[0,.03]],0,2.34,hinge,p['yaw']+angle)
            barrels=[shape([[-.035,-.025],[0,-.025],[0,.025],[-.035,.025]],y,y+.14,hinge,p['yaw']+angle) for y in [.3,1.9]]
            solids=[body]+barrels;states.append(solids)
            for s in nearby:
                if any(hit(a,s) for a in solids):
                    key=d['id']+' <> '+s['owner'];failures[key]+=1
                    if sum(e[0]==key for e in examples)<2:examples.append([key,angle,s['part']])
        poses[d['id']]=states
    pairs=0
    ids=list(poses)
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if math.dist([hinges[a][0],hinges[a][2]],[hinges[b][0],hinges[b][2]])>3.38:continue
            pairs+=1
            for aa,asolid in enumerate(poses[a]):
                for ba,bsolid in enumerate(poses[b]):
                    tests+=1
                    if any(hit(x,y) for x in asolid for y in bsolid):
                        key='PAIR '+a+' <> '+b;failures[key]+=1
                        if sum(e[0]==key for e in examples)<2:examples.append([key,aa,ba])
    return dict(status='PASS' if not failures else 'FAIL',individual_poses=len(poses)*91,nearby_door_pairs=pairs,independent_angle_combinations=tests,failures=dict(failures),examples=examples)

if __name__=='__main__':
    QA.mkdir(exist_ok=True)
    ship=json.loads((PROJECT/'Assets/C01ShipV3/Data/ship.json').read_text(encoding='utf-8'));r=validate(ship);(QA/'layout_qa.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
    if '--geometry' in sys.argv:
        g=geometry_audit(ship);(QA/'geometry_qa.json').write_text(json.dumps(g,indent=2));print(json.dumps(g,indent=2));r['status']='FAIL' if g['status']=='FAIL' else r['status']
    if '--sweeps' in sys.argv:
        sweep=sweep_audit(ship);(QA/'sweep_qa.json').write_text(json.dumps(sweep,indent=2));print(json.dumps(sweep,indent=2));r['status']='FAIL' if sweep['status']=='FAIL' else r['status']
    sys.exit(r['status']!='PASS')
