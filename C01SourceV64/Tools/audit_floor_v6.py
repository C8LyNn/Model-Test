"""Independent expected grid surfaces against actual model geometry."""
from collections import defaultdict
import math
import json
import grid_layout
import scene_data_v6
from validate_ship_v5 import solids, difference
from ship_geometry import polygon_area


def audit(data):
    plan=grid_layout.build()
    shafts=[[v*3 for v in (l["x0"],l["x1"],l["z0"],l["z1"])] for l in plan["lifts"]]
    samples=defaultdict(list)
    for s in solids(data):
        if s["category"] not in ("Floors","Walls","Nodes"):
            continue
        for deck,y in enumerate(plan["elevations"]):
            is_floor=s["category"]=="Floors" and abs(s["hi"]-y)<1e-6
            is_wall=s["category"] in ("Walls","Nodes") and s["lo"]<=y+1e-6 and s["hi"]>=y-1e-6
            if not (is_floor or is_wall):
                continue
            for x in range(math.floor(s["x0"]/3),math.floor(s["x1"]/3)+1):
                for z in range(math.floor(s["z0"]/3),math.floor(s["z1"]/3)+1):
                    samples[deck,x,z].append(s["poly"])
    expected=set()
    for z in plan["zones"]:
        if z["kind"]=="void" or z.get("parent"):
            continue
        for x in range(z["x0"],z["x1"]):
            for zz in range(z["z0"],z["z1"]):
                expected.add((z["deck"],x,zz))
    for deck in (0,1,2):
        for x in range(-16,0):
            inset=max(0,int((-x-1)*.85))
            for z in range(inset,30-inset):
                expected.add((deck,x,z))
        for x in range(42,50):
            for z in range(30):
                expected.add((deck,x,z))
    for deck,x0,x1,z0,z1 in ((1,44,46,30,32),(1,44,46,-2,0),(0,50,58,22,27)):
        for x in range(x0,x1):
            for z in range(z0,z1):
                expected.add((deck,x,z))
    gaps=[]
    for deck,x,z in sorted(expected):
        poly=[[x*3,z*3],[x*3+3,z*3],[x*3+3,z*3+3],[x*3,z*3+3]]
        remain=[poly]
        for x0,x1,z0,z1 in shafts:
            cut=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
            remain=[r for p in remain for r in difference(p,cut)]
        for cut in samples[deck,x,z]:
            remain=[r for p in remain for r in difference(p,cut)]
            if not remain:
                break
        area=sum(polygon_area(p) for p in remain)
        if area>1e-5:
            gaps.append(dict(deck=deck,x=x,z=z,area=area))
    return dict(status="PASS" if not gaps else "FAIL",regions=len(expected),
                gaps=len(gaps),missing_area=sum(g["area"] for g in gaps),examples=gaps[:20])


if __name__=="__main__":
    result=audit(scene_data_v6.build())
    with open("floor_coverage_v6.json","w",encoding="utf8") as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
