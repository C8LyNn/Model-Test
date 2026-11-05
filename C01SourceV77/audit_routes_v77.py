"""Conservative 2D walkability check from the source solids (not a Unity play test)."""
from collections import defaultdict, deque
import math
import json
import scene_data_v6
from validate_ship_v5 import solids


def audit(data):
    bodies=solids(data,1)
    reports=[]
    step=.5
    for deck, floor in enumerate([-3.4,0,3.4]):
        if deck == 0: continue
        ground=defaultdict(list); block=defaultdict(list)
        for s in bodies:
            is_ground=s["category"]=="Floors" and abs(s["hi"]-floor)<1e-6
            is_block=(s["category"] not in ("Floors","Ceilings","Engines") and
                      s["hi"]>floor+.08 and s["lo"]<floor+1.8)
            if not(is_ground or is_block):
                continue
            table=ground if is_ground else block
            extra=.28 if is_block else 0
            for x in range(math.floor((s["x0"]-extra)/3),math.floor((s["x1"]+extra)/3)+1):
                for z in range(math.floor((s["z0"]-extra)/3),math.floor((s["z1"]+extra)/3)+1):
                    table[x,z].append(s)
        valid_cache={}
        def valid(i,j):
            if (i,j) in valid_cache:
                return valid_cache[i,j]
            x,z=(i+.5)*step,(j+.5)*step
            bucket=(math.floor(x/3),math.floor(z/3))
            supported=any(s["x0"]+1e-5<x<s["x1"]-1e-5 and s["z0"]+1e-5<z<s["z1"]-1e-5 for s in ground[bucket])
            blocked=any(s["x0"]-.28<x<s["x1"]+.28 and s["z0"]-.28<z<s["z1"]+.28 for s in block[bucket])
            valid_cache[i,j]=supported and not blocked
            return valid_cache[i,j]
        start=(21,87) # 10.75 m, 43.75 m, in the main corridor.
        visited=set()
        if valid(*start):
            visited.add(start);queue=deque([start])
            while queue:
                i,j=queue.popleft()
                for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
                    n=(i+dx,j+dz)
                    if n not in visited and valid(*n):
                        visited.add(n);queue.append(n)
        missing=[]
        for zn in data["zones"]:
            if zn["deck"]!=deck or zn["kind"]=="void":
                continue
            x0,x1,z0,z1=zn["bounds"]
            if not any(x0<(i+.5)*step<x1 and z0<(j+.5)*step<z1 for i,j in visited):
                missing.append(zn["id"])
        for lift in data["lifts"]:
            x,y,z=lift["waypoints"][deck-1]["position"]
            if not any(abs((i+.5)*step-x)<1.0 and abs((j+.5)*step-z)<1.0 for i,j in visited):
                missing.append(lift["id"]+"_LANDING_"+str(deck))
        reports.append(dict(deck=deck,reachable_samples=len(visited),missing=missing))
    return reports


if __name__=="__main__":
    result=audit(scene_data_v6.build())
    with open("routes_v6_draft.json","w",encoding="utf8") as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
