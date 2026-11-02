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
    for deck in (0,1,2):
        for x in range(-16,0):
            inset=max(0,int((-x-1)*.85))
            for z in range(inset,30-inset):
                cells[deck][x,z]="bridge"
        for x in range(42,50):
            for z in range(30):
                cells[deck][x,z]="stern"
    planes=defaultdict(list)
    def deck2_floor(x,z,kind):
        passage=(x in (-5,-4) and z==7) or (x==-5 and z==8)
        if kind=="bridge" and x < -3 and 3<=z<27 and not passage:
            return False
        if kind=="stern" and 44<=x<48 and 6<=z<24 and not (19<=z<=21):
            return False
        return (x,z) in cells[2]
    for deck,grid in cells.items():
        for (x,z),kind in grid.items():
            if deck==0:
                plane=-6.4 if kind=="corridor" else -.4
            elif deck==1:
                plane=6.0 if deck2_floor(x,z,kind) else (12.4 if kind in ("bridge","stern") else 12.0)
            else:
                plane=12.4
            planes[plane].append((deck,x,z,plane!=12.4))
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
