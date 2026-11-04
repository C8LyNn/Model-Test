"""Plan sector roof variants flush with the upper corridor without moving ceilings."""
from collections import defaultdict
from pathlib import Path
import hashlib,json,math,sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV68/Tools/v5_dependencies'))
from validate_ship_v5 import solids,difference
from ship_geometry import overlap_poly,polygon_area

def build(data):
    parts=solids(data)
    low=[s for s in parts if s['category']=='Ceilings' and abs(s['hi']-6.2)<1e-6]
    owners=defaultdict(list)
    for s in low:owners[s['owner']].append(s)
    high=[s for s in parts if not(s['category']=='Ceilings' and abs(s['hi']-6.2)<1e-6)
          and s['hi']>6.2+1e-6 and s['lo']<6.6-1e-6]
    buckets=defaultdict(list)
    for s in high:
        for x in range(math.floor(s['x0']/3),math.floor(s['x1']/3)+1):
            for z in range(math.floor(s['z0']/3),math.floor(s['z1']/3)+1):buckets[(x,z)].append(s)
    roofs=[];bad_tiles=0;uncovered=0;cap_hits=set();raised_hits=set()
    for p in data['placements']:
        if p['category']!='Ceilings' or abs(p['y']-6.2)>1e-6:continue
        x,z=p['x'],p['z'];tile=[[x,z],[x+3,z],[x+3,z+3],[x,z+3]]
        local_parts=owners[p['id']]
        nearby={id(s):s for s in buckets[(math.floor(x/3),math.floor(z/3))]}.values()
        blockers=[s for s in nearby if s['hi']>6.4+1e-6 and s['lo']<6.6-1e-6]
        for a in local_parts:
            for b in nearby:
                if min(a['x1'],b['x1'])-max(a['x0'],b['x0'])>1e-5 and min(a['z1'],b['z1'])-max(a['z0'],b['z0'])>1e-5 and overlap_poly(a['poly'],b['poly']):
                    raised_hits.add((p['id'],b['owner'],b['part']))
        remaining=[tile]
        for s in local_parts:
            remaining=[r for poly in remaining for r in difference(poly,s['poly'])]
        for s in blockers:
            remaining=[r for poly in remaining for r in difference(poly,s['poly'])]
        caps=[poly for poly in remaining if polygon_area(poly)>1e-6]
        for cap in caps:
            for b in blockers:
                if overlap_poly(cap,b['poly']):cap_hits.add((p['id'],b['owner'],b['part']))
        # Recompute top coverage independently of the cap construction loop.
        check=[tile]
        for cut in [s['poly'] for s in local_parts]+caps+[s['poly'] for s in blockers]:
            check=[r for poly in check for r in difference(poly,cut)]
            if not check:break
        area=sum(polygon_area(poly) for poly in check)
        if area>1e-5:bad_tiles+=1;uncovered+=area
        outlines=[dict(outline=[round(v,6) for q in poly for v in (q[0]-x,q[1]-z)]) for poly in caps]
        key=json.dumps([p['model'],outlines],sort_keys=True,separators=(',',':'))
        variant='C_V70_'+hashlib.sha1(key.encode()).hexdigest()[:12]
        roofs.append(dict(id=p['id'],model=p['model'],variant=variant,bottom=6.0,top=6.6,caps=outlines))
    return dict(version='C01.SHIP.7.0',roofs=roofs,audit=dict(uncoveredTiles=bad_tiles,
                uncoveredArea=round(uncovered,7),capPenetrations=len(cap_hits),raisedRoofPenetrations=len(raised_hits),
                capPolygons=sum(len(r['caps']) for r in roofs),raisedExamples=sorted(raised_hits)[:10],capExamples=sorted(cap_hits)[:10]))

if __name__=='__main__':
    data=json.loads((ROOT/'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
    result=build(data);out=ROOT/'Assets/C01ShipV70/Data/roof_repair.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result['audit'],indent=2))
