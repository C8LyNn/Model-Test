"""Sample actual pre-existing full structural solids against the new segmented union."""
import collections,json,math,sys
from pathlib import Path
from validate_ship_v5 import PROJECT,solids
ROOT=Path(__file__).resolve().parents[1]
old=json.loads((ROOT/'Reference/ship_v4.json').read_text(encoding='utf-8'))
new=json.loads((PROJECT/'Assets/C01ShipV5/Data/ship_v5.json').read_text(encoding='utf-8'))
negative='--remove-wall' in sys.argv
if negative:
    victim=next(p for p in new['placements'] if p['category']=='Walls' and p['model']=='W3_H3000')
    new['placements'].remove(victim)
categories={'Walls','Nodes','Hull','GateFrames','GateLeaves'}
def inside(point,poly):
    signs=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):signs.append((b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]))
    return min(signs)>=-1e-7 or max(signs)<=1e-7
results=[]
for pose in (0,1):
    buckets=collections.defaultdict(list)
    for s in solids(new,pose):
        if s['category'] not in categories:continue
        for x in range(math.floor(s['x0']/3),math.floor(s['x1']/3)+1):
            for z in range(math.floor(s['z0']/3),math.floor(s['z1']/3)+1):buckets[s['category'],x,z].append(s)
    missing=[];samples=0
    for s in solids(old,pose):
        if s['category'] not in categories:continue
        poly=s['poly'];cx=sum(p[0] for p in poly)/len(poly);cz=sum(p[1] for p in poly)/len(poly)
        points=[[cx,cz]]+[[p[0]*.95+cx*.05,p[1]*.95+cz*.05] for p in poly]
        h=s['hi']-s['lo'];steps=max(1,math.ceil(h/.5));ys=[s['lo']+h*(i+.5)/steps for i in range(steps)]
        for point in points:
            candidates=buckets.get((s['category'],math.floor(point[0]/3),math.floor(point[1]/3)),[])
            for y in ys:
                samples+=1
                if not any(q['lo']-1e-7<=y<=q['hi']+1e-7 and inside(point,q['poly']) for q in candidates):
                    missing.append({'owner':s['owner'],'part':s['part'],'point':[round(point[0],5),round(y,5),round(point[1],5)]});break
            if missing and missing[-1]['owner']==s['owner'] and missing[-1]['part']==s['part']:break
    results.append(dict(pose=pose,status='PASS' if not missing else 'FAIL',samples=samples,missing=len(missing),examples=missing[:20]))
out=ROOT/('QA/structure_negative.json' if negative else 'QA/structure_v4_to_v5.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps(results,indent=2));sys.exit(not all(r['missing'] for r in results) if negative else any(r['missing'] for r in results))
