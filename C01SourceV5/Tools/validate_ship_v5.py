"""Independent v5 plan/content/solid audits, including source details and missing surfaces."""
import json,math,collections,sys
from pathlib import Path
from ship_geometry import transform_poly,overlap_poly,polygon_area
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT.parent if (ROOT.parent/'Assets/C01ShipV5').is_dir() else ROOT/'UnityProject';QA=ROOT/'C01ShipV5_QA' if PROJECT==ROOT else ROOT/'QA'

def halfplane(poly,a,b,inside):
    def cross(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        cp,cq=cross(p),cross(q);ip=cp>=-1e-9 if inside else cp<=1e-9;iq=cq>=-1e-9 if inside else cq<=1e-9
        if ip:out.append(p)
        if ip!=iq and abs(cp-cq)>1e-12:
            t=cp/(cp-cq);out.append([p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])])
    clean=[]
    for p in out:
        if not clean or math.dist(clean[-1],p)>1e-8:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-8:clean.pop()
    return clean if len(clean)>=3 and polygon_area(clean)>1e-9 else []

def difference(poly,cut):
    if not poly:return []
    xs=[p[0] for p in poly];zs=[p[1] for p in poly];cx=[p[0] for p in cut];cz=[p[1] for p in cut]
    if max(xs)<=min(cx)+1e-9 or min(xs)>=max(cx)-1e-9 or max(zs)<=min(cz)+1e-9 or min(zs)>=max(cz)-1e-9:return [poly]
    remain=poly;pieces=[]
    for a,b in zip(cut,cut[1:]+cut[:1]):
        outside=halfplane(remain,a,b,False)
        if outside:pieces.append(outside)
        remain=halfplane(remain,a,b,True)
        if not remain:break
    return pieces

def reference_surfaces():
    """Literal accepted plan surfaces; independent of manifest coverage and model IDs."""
    from ship_geometry import clip_rect
    bow=[[0,3],[0,42],[-12,42],[-24,22.5],[-12,3]];ys={0:-12.4,1:0.,2:6.4};out=[]
    def add(kind,deck,x,z,plane,poly=None,shaft_cut=True):
        p=poly or [[x,z],[x+3,z],[x+3,z+3],[x,z+3]];polys=[p]
        if shaft_cut:
            for x0,x1,z0,z1 in [[-6,-3,21,24],[66,69,21,24]]:
                cut=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]];polys=[r for p in polys for r in difference(p,cut)]
        for i,p in enumerate(polys):out.append((f'{kind}_L{deck}_{x}_{z}_{i}',kind,plane,p))
    for deck in [0,1,2]:
        for x in range(0,63,3):
            for z in range(0 if deck<2 else 12,45 if deck<2 else 33,3):
                add('floor',deck,x,z,ys[deck]);ceiling=(-6.4 if z==21 else -.4) if deck==0 else (6 if 12<=z<33 else 12) if deck==1 else 12.4
                add('ceiling',deck,x,z,ceiling)
        for x in range(-24,0,3):
            for z in range(3,42,3):
                p=clip_rect(bow,x,x+3,z,z+3)
                if not p or deck==2 and x!=-3:continue
                add('floor',deck,x,z,ys[deck],p);add('ceiling',deck,x,z,-.4 if deck==0 else 6 if deck==1 and x==-3 else 12.4,p)
        for x in range(63,75,3):
            for z in range(0,45,3):
                central=66<=x<72 and 3<=z<42
                if deck==2 and central:continue
                add('floor',deck,x,z,ys[deck]);add('ceiling',deck,x,z,-.4 if deck==0 else 12.4 if deck==2 or central else 6)
    for deck,x0,x1,z0,z1 in [(0,75,87,33,42),(1,66,72,45,48),(1,66,72,-3,0)]:
        for x in range(x0,x1,3):
            for z in range(z0,z1,3):add('floor',deck,x,z,ys[deck])
    for x in [-6,66]:add('ceiling',2,x,21,12.4,shaft_cut=False)
    return out

def surface_audit(data):
    bodies=solids(data);targets=reference_surfaces();planes={ (kind,plane) for _,kind,plane,_ in targets};tables={}
    structure={'Walls','Nodes','Hull','GateFrames'}
    for kind,plane in planes:
        buckets=collections.defaultdict(list)
        for s in bodies:
            face=s['category'] in (['Floors'] if kind=='floor' else ['Floors','Ceilings']) and abs((s['hi'] if kind=='floor' else s['lo'])-plane)<1e-5
            occupied=s['category'] in structure and s['lo']<=plane+1e-5 and s['hi']>=plane-1e-5
            if not(face or occupied):continue
            for x in range(math.floor(s['x0']/3),math.floor(s['x1']/3)+1):
                for z in range(math.floor(s['z0']/3),math.floor(s['z1']/3)+1):buckets[x,z].append(s['poly'])
        tables[kind,plane]=buckets
    gaps=[];area=0
    for name,kind,plane,poly in targets:
        x=math.floor(min(p[0] for p in poly)/3+1e-7);z=math.floor(min(p[1] for p in poly)/3+1e-7);remaining=[poly]
        for cut in tables[kind,plane].get((x,z),[]):
            remaining=[p for r in remaining for p in difference(r,cut)]
            if not remaining:break
        missing=sum(polygon_area(p) for p in remaining)
        if missing>1e-5:area+=missing;gaps.append(dict(id=name,plane=plane,area=missing))
    return dict(status='PASS' if not gaps else 'FAIL',regions=len(targets),gaps=len(gaps),missing_area=area,examples=gaps[:20])

def validate(data):
    errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    ps=data['placements'];byid={p['id']:p for p in ps};models={m['id']:m for m in data['models']};zs={z['id']:z for z in data['zones']}
    check(len(byid)==len(ps),'Duplicate placement ID');check(data['body']==[0,63,0,45],'Body dimensions');check(data['unit']==3,'Construction unit')
    for deck in [1,2]:
        for side,z,offset in [('N',24,0),('S',12,6)]:
            for block in range(3):
                branch=zs.get(f'L{deck}_X{side}{block+1}',{});check(branch.get('bounds')==[block*21+9,block*21+12,z,z+9],'Branch grid')
                for j,rx in enumerate([block*21,block*21+12]):
                    zid=f'L{deck}_C{offset+block*2+j+1:02d}';room=zs.get(zid,{})
                    check(room.get('bounds')==[rx,rx+9,z,z+9] and room.get('height')==6,'Cabin dimensions '+zid)
                    bath=zs.get(zid+'_BATH',{});check(bath.get('bounds')==[rx,rx+6,z+6,z+9] and bath.get('parent')==zid,'Bathroom dimensions '+zid)
    # Required floor ownership is derived from the fixed room plan, not placement counts.
    required=set()
    for deck,z0,z1 in [(0,0,45),(1,0,45),(2,12,33)]:
        for x in range(0,63,3):
            for z in range(z0,z1,3):required.add(f'F_L{deck}_{x}_{z}')
    for deck in [0,1,2]:
        for x in range(63,75,3):
            for z in range(0,45,3):
                if deck==2 and 66<=x<72 and 3<=z<42:continue
                if x==66 and z==21:continue # actual 3m elevator shaft, not a missing floor
                required.add(f'F_L{deck}_{x}_{z}')
    check(required<=set(byid),'Missing required floor fragments: '+','.join(sorted(required-set(byid))[:15]))
    ceilings={f'C_L0_{x}_21' for x in range(0,63,3)}
    ceilings|={f'C_L1_{x}_{z}' for x in range(0,63,3) for z in list(range(0,12,3))+list(range(33,45,3))}
    ceilings|={f'C_L2_{x}_{z}' for x in range(0,63,3) for z in range(12,33,3)}
    check(ceilings<=set(byid),'Missing required ceiling fragments: '+','.join(sorted(ceilings-set(byid))[:15]))
    for deck in [1,2]:
        for i in range(1,13):
            zid=f'L{deck}_C{i:02d}';local=[p for p in ps if p['zone']==zid]
            check(sum(p['model']=='P_Bed' for p in local)==4,'Missing cabin beds '+zid);check(sum(p['model']=='P_Locker' for p in local)==8,'Missing cabin lockers '+zid)
    for gid,g in enumerate(data['gates']):
        check(len(g['leaves'])>=8 and len(g['leaves'])%8==0 and all(v in byid for v in g['leaves']),'Missing gate leaf '+g['id'])
        check(len(g['buttons'])==2 and all(v in byid and byid[v]['buttonGate']==g['id'] for v in g['buttons']),'Missing gate button '+g['id'])
        for pid in g['leaves']:
            if pid in byid:check(byid[pid]['gate']==g['id'] and len(byid[pid]['travel'])==3,'Gate motion ownership '+pid)
    check(len(data['lifts'])==2,'Expected two vertical cores')
    for lift in data['lifts']:
        check(lift['floors']==[0,1,2] and lift['elevations']==[-12.4,0,6.4],'Lift stops '+lift['id'])
        check(len(lift['landings'])==3 and all(any(g['id']==gid and g['lift']==lift['id'] for g in data['gates']) for gid in lift['landings']),'Lift landing gates '+lift['id'])
    graph=collections.defaultdict(set)
    for l in data['links']:graph[l['a']].add(l['b']);graph[l['b']].add(l['a'])
    reached={'L1_BRIDGE'};queue=collections.deque(reached)
    while queue:
        for z in graph[queue.popleft()]:
            if z not in reached:reached.add(z);queue.append(z)
    check(set(zs)<=reached,'Disconnected zones: '+','.join(sorted(set(zs)-reached)))
    for p in ps:check(p['model'] in models,'Missing source model '+p['id'])
    used={p['model'] for p in ps}
    for m in data['models']:check(m['id'] not in used or bool(m['parts']),'Empty used source model '+m['id'])
    check(bool(data.get('coverage')),'Surface ray coverage targets missing')
    coverage=surface_audit(data);check(coverage['status']=='PASS','Independent surface gaps: '+json.dumps(coverage['examples']))
    return dict(status='PASS' if not errors else 'FAIL',errors=errors,surfaces=coverage,counts=dict(placements=len(ps),zones=len(zs),reachable_zones=len(reached),gates=len(data['gates']),lifts=len(data['lifts']),beds=sum(p['model']=='P_Bed' for p in ps),lockers=sum(p['model']=='P_Locker' for p in ps)))

def solids(data,openness=0):
    models={m['id']:m for m in data['models']};out=[]
    for p in data['placements']:
        pos=[p['x']+p['travel'][0]*openness,p['y']+p['travel'][1]*openness,p['z']+p['travel'][2]*openness]
        for i,part in enumerate(models[p['model']]['parts']):
            poly=transform_poly(list(zip(part['outline'][::2],part['outline'][1::2])),pos,p['yaw']);xs=[q[0] for q in poly];zs=[q[1] for q in poly]
            out.append(dict(owner=p['id'],model=p['model'],part=i,category=p['category'],poly=poly,lo=pos[1]+part['y0'],hi=pos[1]+part['y1'],x0=min(xs),x1=max(xs),z0=min(zs),z1=max(zs),gate=p['gate']))
    return out

def collision_audit(data,openness=0):
    bodies=solids(data,openness);buckets=collections.defaultdict(list);seen=set();hits=[];tests=0
    for i,s in enumerate(bodies):
        for x in range(math.floor(s['x0']/3),math.floor(s['x1']/3)+1):
            for y in range(math.floor(s['lo']/6),math.floor(s['hi']/6)+1):
                for z in range(math.floor(s['z0']/3),math.floor(s['z1']/3)+1):buckets[x,y,z].append(i)
    for group in buckets.values():
        for ai,aindex in enumerate(group):
            a=bodies[aindex]
            for bindex in group[ai+1:]:
                key=(min(aindex,bindex),max(aindex,bindex))
                if key in seen:continue
                seen.add(key);b=bodies[bindex]
                if min(a['hi'],b['hi'])-max(a['lo'],b['lo'])<1e-5 or min(a['x1'],b['x1'])-max(a['x0'],b['x0'])<1e-5 or min(a['z1'],b['z1'])-max(a['z0'],b['z0'])<1e-5:continue
                tests+=1
                if overlap_poly(a['poly'],b['poly']):
                    hits.append([a['owner'],a['part'],b['owner'],b['part']])
    groups=collections.Counter((a.split('_')[0],b.split('_')[0]) for a,_,b,_ in hits)
    return dict(status='PASS' if not hits else 'FAIL',solids=len(bodies),poses=openness,penetrations=len(hits),tests=tests,groups={str(k):v for k,v in groups.items()},examples=hits[:80])

if __name__=='__main__':
    QA.mkdir(exist_ok=True);data=json.loads((PROJECT/'Assets/C01ShipV5/Data/ship_v5.json').read_text(encoding='utf-8'));r=validate(data);(QA/'layout_v5.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
    if '--geometry' in sys.argv:
        for pose in [0,1]:
            g=collision_audit(data,pose);(QA/f'geometry_v5_{pose}.json').write_text(json.dumps(g,indent=2));print(json.dumps(g,indent=2));r['status']='FAIL' if g['status']=='FAIL' else r['status']
    sys.exit(r['status']!='PASS')
