"""Compare actual slab underside polygons against independent ceiling regions."""
from collections import defaultdict
import json
import math
import grid_layout
import scene_data_v6
from validate_ship_v5 import solids, difference
from ship_geometry import polygon_area

def audit(data):
    plan=grid_layout.build()
    shafts=[[v*3 for v in (l["x0"],l["x1"],l["z0"],l["z1"])] for l in plan["lifts"]]
    cells={d:{} for d in (0,1,2)}
    for zone in plan["zones"]:
        if zone["kind"]=="void" or zone.get("parent"):
            continue
        for x in range(zone["x0"],zone["x1"]):
            for z in range(zone["z0"],zone["z1"]):
                cells[zone["deck"]][x,z]=zone["kind"]
    # Ordinary rooms have three-metre clear heights. Core atria share one roof
    # four modules above the lower deck and deliberately contain partial decks.
    planes=defaultdict(list)
    for deck,grid in cells.items():
        for (x,z),kind in grid.items():
            planes[6.0 if deck==1 and kind=="sector" else (-.4,3.0,6.4)[deck]].append((deck,x,z,True))
    for x in range(-16,0):
        inset=max(0,int((-x-1)*.5))
        for z in range(5+inset,24-inset): planes[8.6].append((2,x,z,False))
    for x in range(42,50):
        for z in range(5,24): planes[8.6].append((2,x,z,False))
    buckets=defaultdict(list)
    for s in solids(data):
        for plane in planes:
            face=s["category"] in ("Floors","Ceilings") and abs(s["lo"]-plane)<1e-5
            occupied=s["category"] in ("Walls","Nodes") and s["lo"]<=plane+1e-5 and s["hi"]>=plane-1e-5
            if face or occupied:
                for x in range(math.floor(s["x0"]/3),math.floor(s["x1"]/3)+1):
                    for z in range(math.floor(s["z0"]/3),math.floor(s["z1"]/3)+1):
                        buckets[plane,x,z].append(s["poly"])
    missing=[]
    for plane,regions in planes.items():
        for deck,x,z,holes in regions:
            remain=[[[x*3,z*3],[x*3+3,z*3],[x*3+3,z*3+3],[x*3,z*3+3]]]
            if holes:
                for x0,x1,z0,z1 in shafts:
                    cut=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
                    remain=[r for p in remain for r in difference(p,cut)]
            for cut in buckets[plane,x,z]:
                remain=[r for p in remain for r in difference(p,cut)]
                if not remain:
                    break
            area=sum(polygon_area(p) for p in remain)
            if area>1e-5:
                missing.append(dict(deck=deck,x=x,z=z,plane=plane,area=area))
    return dict(status="PASS" if not missing else "FAIL",regions=sum(map(len,planes.values())),
                gaps=len(missing),missing_area=sum(g["area"] for g in missing),examples=missing[:20])

if __name__=="__main__":
    result=audit(scene_data_v6.build())
    with open("ceiling_coverage_v6.json","w",encoding="utf8") as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
