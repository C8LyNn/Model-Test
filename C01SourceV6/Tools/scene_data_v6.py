"""Draft v6 assembly derived from the V5 module catalog and a grid topology.

This builder is intentionally kept in the work area until all components and
physical checks pass. Coordinates in grid_layout are squares of 3 m.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import json
import hashlib
import math
import sys

import grid_layout

HERE = Path(__file__).resolve().parent
PROJECT = HERE/"UnityProject" if (HERE/"UnityProject/Assets").is_dir() else HERE.parent.parent
V5_TOOLS = HERE/"v5_dependencies"
V5_DATA = PROJECT/"Assets/C01ShipV5/Data/ship_v5.json"
sys.path.insert(0, str(V5_TOOLS))
from build_ship_v5 import join_deck_intervals, vertical_modules, cut_intervals, subtract_all, clean
from models_v5 import part, box
from ship_geometry import clip_rect, transform_poly
from ceiling_work.vertical_partition import vertical_modules as roof_partition


def build():
    plan = grid_layout.build()
    old = json.loads(V5_DATA.read_text(encoding="utf8"))
    models = {m["id"]: deepcopy(m) for m in old["models"]}
    old_models = models.copy()
    old_zones = {z["id"]: z for z in old["zones"]}
    old_placements = old["placements"]
    zones, placements, gates, links, coverage, lifts, airlocks = [], [], [], [], [], [], []
    lookup = {}
    cells = {0: {}, 1: {}, 2: {}}
    walls = defaultdict(list)
    cuts = defaultdict(list)
    node_cuts = defaultdict(list)
    floors = plan["elevations"]

    def place(ident, model, x, y, z, yaw=0, category="Props", zone="", deck=-1, **extra):
        p = dict(id=ident, model=model, category=category, zone=zone, deck=deck,
                 x=round(x, 7), y=round(y, 7), z=round(z, 7), yaw=yaw, parent="",
                 gate="", buttonGate="", buttonLift="", buttonFloor=0, travel=[0, 0, 0])
        p.update(extra)
        placements.append(p)
        return p

    def zone(spec):
        d = spec["deck"]
        kind = spec["kind"]
        height = 12 if kind == "sector" or (d == 0 and (kind == "core" or spec["id"] == "L0_DOCK")) else 6
        b = [spec[k] * 3 for k in ("x0", "x1", "z0", "z1")]
        y = floors[d]
        z = dict(id=spec["id"], label=spec["id"].replace("_", " "),
                 kind=kind, deck=d, floor=y, height=height, bounds=b,
                 parent=spec.get("parent", ""),
                 waypoint=[(b[0]+b[1])/2, y, (b[2]+b[3])/2])
        zones.append(z)
        lookup[z["id"]] = z
        if kind != "void":
            for x in range(spec["x0"], spec["x1"]):
                for zz in range(spec["z0"], spec["z1"]):
                    if z["id"].endswith("_BRIDGE"):
                        inset=max(0, int((-x-1)*.85))
                        if zz < inset or zz >= 30-inset:
                            continue
                    cells[d][x, zz] = z["id"]

    for spec in plan["zones"]:
        if spec["kind"] != "bathroom":
            zone(spec)
    for spec in plan["zones"]:
        if spec["kind"] == "bathroom":
            zone(spec)
    for deck in (0, 1, 2):
        zone(dict(id=f"L{deck}_BRIDGE", kind="core", deck=deck, x0=-16, x1=0, z0=0, z1=30))
        zone(dict(id=f"L{deck}_STERN", kind="core", deck=deck, x0=42, x1=50, z0=0, z1=30))
    zone(dict(id="L1_D3",kind="airlock",deck=1,x0=42,x1=50,z0=29,z1=30,parent="L1_STERN"))
    zone(dict(id="L1_D4",kind="airlock",deck=1,x0=42,x1=50,z0=0,z1=1,parent="L1_STERN"))
    zone(dict(id="L0_DOCK",kind="airlock",deck=0,x0=42,x1=50,z0=22,z1=27,parent="L0_STERN"))
    for ident,deck,b in (("L1_EXIT_N",1,[44,46,30,32]),("L1_EXIT_S",1,[44,46,-2,0]),
                         ("L0_EXIT",0,[50,58,22,27])):
        world=[v*3 for v in b]
        z=dict(id=ident,label=ident,kind="exterior",deck=deck,floor=floors[deck],height=6,
               bounds=world,parent="",waypoint=[(world[0]+world[1])/2,floors[deck],(world[2]+world[3])/2])
        zones.append(z);lookup[ident]=z

    # Pick an existing V5 gate as a rigid kit: rotations preserve model dimensions.
    def rotate(x, z, yaw):
        a = math.radians(yaw)
        return math.cos(a)*x + math.sin(a)*z, -math.sin(a)*x + math.cos(a)*z

    def gate(ident, deck, a, b, axis, gx, gz, width=3):
        template = next(g for g in old["gates"] if g["id"] == ("L0_EVAC_INNER" if width==9 else "L1_C01_GATE"))
        pieces = [p for p in old_placements if p["id"].startswith(template["id"]+"_")]
        x, z, y = gx*3, gz*3, floors[deck]
        yaw = 0 if axis == "H" else -90
        mapping = {}
        for src in pieces:
            p = deepcopy(src)
            p["id"] = ident + src["id"][len(template["id"]):]
            lx, lz = rotate(src["x"]-template["x"], src["z"]-template["z"], -template["yaw"])
            dx, dz = rotate(lx, lz, yaw)
            p.update(x=round(x+dx, 7), y=round(y+src["y"]-template["y"], 7),
                     z=round(z+dz, 7), yaw=(src["yaw"]-template["yaw"]+yaw),
                     zone=a, deck=deck)
            tx, tz = rotate(src["travel"][0], src["travel"][2], -template["yaw"])
            tx, tz = rotate(tx, tz, yaw)
            p["travel"] = [tx, src["travel"][1], tz]
            if p["gate"]:
                p["gate"] = ident
            if p["buttonGate"]:
                p["buttonGate"] = ident
            placements.append(p)
            mapping[src["id"]] = p["id"]
        height=template["height"]
        g = dict(id=ident, deck=deck, x=x, y=y, z=z, yaw=yaw, width=width, height=height,
                 zones=[a, b], leaves=[mapping[i] for i in template["leaves"]],
                 buttons=[mapping[i] for i in template["buttons"]], airlock="", lift="", floor=-1)
        gates.append(g)
        for offset in range(0,width,3):
            cuts[axis, x+offset if axis=="H" else x, z if axis=="H" else z+offset].append([y,y+height])
        for offset in range(3,width,3):
            node_cuts[x+offset if axis=="H" else x,z if axis=="H" else z+offset].append([y,y+height])
        links.append(dict(a=a, b=b, kind="gate", gate=ident))
        return g

    wanted = {frozenset(p) for p in plan["links"]}
    for deck in (0, 1, 2):
        wanted.add(frozenset((f"L{deck}_MAIN", f"L{deck}_BRIDGE")))
        wanted.add(frozenset((f"L{deck}_MAIN", f"L{deck}_STERN")))
    candidates = defaultdict(list)
    all_edges = {}
    for deck, grid in cells.items():
        edges = {}
        for (x, z), owner in grid.items():
            for edge in (("H", x, z), ("H", x, z+1), ("V", x, z), ("V", x+1, z)):
                edges.setdefault(edge, []).append(owner)
        all_edges[deck] = edges
        for edge, owners in edges.items():
            if len(owners) == 2 and owners[0] != owners[1] and frozenset(owners) in wanted:
                candidates[deck, frozenset(owners)].append(edge)
    door_edges = {}
    for (deck, pair), edges in candidates.items():
        a, b = sorted(pair)
        if "airlock" in (lookup[a]["kind"],lookup[b]["kind"]):
            continue
        if lookup[a]["kind"] == lookup[b]["kind"] == "corridor":
            links.append(dict(a=a, b=b, kind="opening", gate=""))
            continue
        ordered = sorted(edges)
        safe = [e for e in ordered if not (e[0]=="H" and e[2] in (14,15) and
                                            (12 <= e[1] <= 15 or 26 <= e[1] <= 29))]
        edge = (safe or ordered)[len(safe or ordered)//2]
        door_edges[deck, edge] = (a, b)
        gate("G_"+a+"_"+b, deck, a, b, *edge)

    for deck in (0,1,2):
        for name,x in (("D1",13),("D2",27)):
            ident=f"L{deck}_{name}"
            inner=gate(ident+"_A",deck,f"L{deck}_MAIN",ident,"V",x,14)
            outer=gate(ident+"_B",deck,ident,f"L{deck}_MAIN","V",x+2,14)
            inner["airlock"]=outer["airlock"]=ident
            airlocks.append(dict(id=ident,gates=[inner["id"],outer["id"]]))
    for name,inside,outside,pad in (("D3",29,30,"L1_EXIT_N"),("D4",1,0,"L1_EXIT_S")):
        ident="L1_"+name
        inner=gate(ident+"_INNER",1,"L1_STERN",ident,"H",44,inside)
        outer=gate(ident+"_OUTER",1,ident,pad,"H",44,outside)
        inner["airlock"]=outer["airlock"]=ident
        airlocks.append(dict(id=ident,gates=[inner["id"],outer["id"]]))
    inner=gate("L0_EVAC_INNER",0,"L0_EVAC_HANGAR","L0_DOCK","V",42,23,width=9)
    outer=gate("L0_EVAC_OUTER",0,"L0_DOCK","L0_EXIT","V",50,23,width=9)
    inner["airlock"]=outer["airlock"]="L0_EVAC_LOCK"
    airlocks.append(dict(id="L0_EVAC_LOCK",gates=[inner["id"],outer["id"]]))
    gate("L0_DOCK_ACCESS",0,"L0_STERN","L0_DOCK","H",43,22)

    # Collect each wall edge once; leave openings between adjacent corridors.
    for deck, edges in all_edges.items():
        for edge, owners in edges.items():
            if len(owners) == 2 and owners[0] == owners[1]:
                continue
            if len(owners) == 1:
                h = lookup[next(iter(owners))]["height"]
            else:
                a, b = sorted(owners)
                if (frozenset(owners) in wanted and lookup[a]["kind"] == lookup[b]["kind"] == "corridor"):
                    continue
                h = max(lookup[a]["height"], lookup[b]["height"])
            axis, gx, gz = edge
            walls[axis, gx*3, gz*3].append([floors[deck], floors[deck]+h])

    # Four lift shafts, off the central corridor. Perimeter walls and all
    # landings use the same 3 m wall and gate sockets as the rest of the ship.
    shaft_rects = []
    for lift in plan["lifts"]:
        x0,x1,z0,z1 = (lift[k]*3 for k in ("x0","x1","z0","z1"))
        shaft_rects.append([x0,x1,z0,z1])
        ident = lift["id"]
        core = "BRIDGE" if ident.startswith("BRIDGE") else "STERN"
        for x in range(x0,x1,3):
            for z in (z0,z1):
                walls["H",x,z].append([-12.4,12.4])
        for z in range(z0,z1,3):
            for x in (x0,x1):
                walls["V",x,z].append([-12.4,12.4])
        landings, waypoints = [], []
        for deck in (0,1,2):
            gid = ident+"_LANDING_"+str(deck)
            core_id = f"L{deck}_{core}"
            g = gate(gid,deck,core_id,core_id,"V",x0//3,z0//3)
            g["lift"],g["floor"] = ident,deck
            for p in placements:
                if p["id"] in g["buttons"]:
                    p["buttonLift"],p["buttonFloor"] = ident,deck
            landings.append(gid)
            waypoints.append(dict(position=[x0-.9,floors[deck],z0+1.5]))
        cx,cz=(x0+x1)/2,(z0+z1)/2
        car=ident+"_CAR"
        if lift["kind"] == "passenger":
            place(ident+"_PLATFORM","P_LiftCar_W",cx,0,cz,category="LiftCars",parent=car)
            bounds=[cx-1.29,cx+1.29,cz-1.29,cz+1.29]
        else:
            for x in range(x0,x1,3):
                for z in range(z0,z1,3):
                    inset_x=.15 if x==x0 else 0
                    inset_z=.15 if z==z0 else 0
                    width_x=2.85
                    width_z=2.85
                    mid="P_CargoLiftTile"
                    if mid not in models:
                        models[mid]=dict(id=mid,family="prop",nominal=[3,.2,3],sockets=[],
                                         parts=[box("METAL",[0,-.2,0],[width_x,0,width_z])])
                    place(f"{ident}_PLATFORM_{x}_{z}",mid,x+inset_x,0,z+inset_z,category="LiftCars",parent=car)
            bounds=[x0+.15,x1-.15,z0+.15,z1-.15]
        for floor in (0,1,2):
            place(ident+"_SELECT_"+str(floor),"P_Button",x0+.5+floor*.4,1.3,z1-.15,
                  yaw=180,category="Buttons",parent=car,buttonLift=ident,buttonFloor=floor)
        lifts.append(dict(id=ident,car=car,x=cx,z=cz,bounds=bounds,startFloor=1,
                          floors=[0,1,2],elevations=floors,landings=landings,waypoints=waypoints))
        for deck in (0,1):
            links.append(dict(a=f"L{deck}_{core}",b=f"L{deck+1}_{core}",kind="lift",gate=""))

    nodes = defaultdict(list)
    obstacles = []
    for (axis, x, z), spans in walls.items():
        for a, b in join_deck_intervals(spans):
            for point in ((x, z), (x+3, z) if axis == "H" else (x, z+3)):
                nodes[point].append([a, b])
        for a, b, style in roof_partition(cut_intervals(join_deck_intervals(spans), cuts[axis, x, z]),[-.4,12,12.4]):
            h = round(b-a, 7)
            mid = f"W3_H{round(h*1000)}" + ("_FASCIA" if style=="trim" else "")
            if mid not in models:
                parts = ([box("PANEL",[.15,0,-.15],[2.85,h,.15])] if style=="trim" else
                         [box("METAL", [.15, 0, -.15], [2.85, min(.12,h), .15]),
                          box("METAL", [.15, max(.12,h-.12), -.15], [2.85,h,.15])])
                if style!="trim" and h > .32:
                    parts += [box("WALL", [.15,.12,-.1], [2.85,h-.12,.1]),
                              box("PANEL", [.15,.12,-.15], [2.85,h-.12,-.1]),
                              box("PANEL", [.15,.12,.1], [2.85,h-.12,.15])]
                models[mid] = dict(id=mid, family="wall", nominal=[3,h,.3], sockets=[], parts=parts)
            place(f"W_{axis}_{x}_{z}_{a}", mid, x, a, z, 0 if axis=="H" else -90, "Walls")
            rect = [x+.15,x+2.85,z-.15,z+.15] if axis=="H" else [x-.15,x+.15,z+.15,z+2.85]
            obstacles.append((a,b,rect))
    for (x,z), spans in nodes.items():
        for a,b,style in roof_partition(cut_intervals(join_deck_intervals(spans),node_cuts[x,z]),[-.4,12,12.4]):
            h=round(b-a,7)
            mid=f"N_H{round(h*1000)}"+("_FASCIA" if style=="trim" else "")
            if mid not in models:
                models[mid]=dict(id=mid,family="node",nominal=[.3,h,.3],sockets=[],
                                 parts=[box("PANEL" if style=="trim" else "METAL",[-.15,0,-.15],[.15,h,.15])])
            place(f"N_{x}_{z}_{a}",mid,x,a,z,category="Nodes")
            obstacles.append((a,b,[x-.15,x+.15,z-.15,z+.15]))

    # Protect open deck-2 galleries while leaving shaft entrances unobstructed.
    def shaft_cell(x,z):
        return any(l["x0"]<=x<l["x1"] and l["z0"]<=z<l["z1"] for l in plan["lifts"])
    def core_floor(x,z,owner):
        bridge_passage=(x in (-5,-4) and z==7) or (x==-5 and z==8)
        if owner.endswith("_BRIDGE") and x < -3 and 3<=z<27 and not bridge_passage:
            return False
        if owner.endswith("_STERN") and 44<=x<48 and 6<=z<24 and not (19<=z<=21):
            return False
        return True
    rail_edges=set()
    grid2=cells[2]
    for (x,z),owner in grid2.items():
        if lookup[owner]["kind"]!="core" or not core_floor(x,z,owner) or shaft_cell(x,z):
            continue
        for dx,dz,edge in ((-1,0,("V",x,z)),(1,0,("V",x+1,z)),
                           (0,-1,("H",x,z)),(0,1,("H",x,z+1))):
            near=(x+dx,z+dz)
            if grid2.get(near)!=owner or shaft_cell(*near) or core_floor(*near,owner):
                continue
            axis,gx,gz=edge;key=(axis,gx*3,gz*3)
            # A structural wall already guards this boundary.
            if any(a<=6.4+1e-6 and b>=7.6-1e-6 for a,b in walls.get(key,())):
                continue
            rail_edges.add(edge)
    rail_nodes=set()
    for axis,x,z in sorted(rail_edges):
        x,z=x*3,z*3
        place(f"R_{axis}_{x}_{z}","P_Rail3",x,6.4,z,0 if axis=="H" else -90,
              "Railings",deck=2)
        rail_nodes.add((x,z))
        rail_nodes.add((x+3,z) if axis=="H" else (x,z+3))
    for x,z in sorted(rail_nodes):
        # Existing full-height junctions own their footprint.
        if any(a<=6.4+1e-6 and b>=7.6-1e-6 for a,b in nodes.get((x,z),())):
            continue
        place(f"RP_{x}_{z}","P_RailPost",x,6.4,z,category="Railings",deck=2)

    # Cut slab tiles against real shaft and wall solids rather than allowing
    # overlapping floors through continuous walls. Pieces remain separate
    # prefabs with no transform scaling.
    example = next(p for p in old_placements if p["id"] == "F_L0_0_24")
    floor_model = old_models[example["model"]]
    obstacle_bins=defaultdict(list)
    for item in obstacles:
        a,b,r=item
        for gx in range(math.floor(r[0]/3),math.floor(r[1]/3)+1):
            for gz in range(math.floor(r[2]/3),math.floor(r[3]/3)+1):
                obstacle_bins[gx,gz].append(item)

    def slab(ident, deck, gx, gz, top, thickness, zid, ceiling=False, holes=True):
        x,z=gx*3,gz*3
        poly=[[x,z],[x+3,z],[x+3,z+3],[x,z+3]]
        rects=list(shaft_rects) if holes else []
        for a,b,r in obstacle_bins[gx,gz]:
            if top > a+1e-6 and top-thickness < b-1e-6:
                if x+3>r[0] and x<r[1] and z+3>r[2] and z<r[3]:
                    rects.append(r)
        polys=subtract_all(poly,rects)
        if not polys:
            return
        parts=[]
        for p in polys:
            local=[[a-x,b-z] for a,b in p]
            if ceiling:
                parts.append(part("HULL",local,-thickness,0))
            else:
                bounds=[min(v[0] for v in p),max(v[0] for v in p),
                        min(v[1] for v in p),max(v[1] for v in p)]
                for t in floor_model["parts"]:
                    points=[[t["outline"][i]+x,t["outline"][i+1]+z] for i in range(0,len(t["outline"]),2)]
                    q=clip_rect(points,*bounds)
                    if q:
                        parts.append(part(t["role"],[[a-x,b-z] for a,b in clean(q)],t["y0"],t["y1"]))
            coverage.append(dict(id=ident+"_"+str(len(coverage)),deck=deck,
                                 plane=top-thickness if ceiling else top,
                                 normal="down" if ceiling else "up",
                                 poly=[v for point in p for v in point]))
        if not parts:
            return
        digest=hashlib.sha1(json.dumps(parts,sort_keys=True).encode()).hexdigest()[:12]
        mid=("C_" if ceiling else "F_")+digest
        if mid not in models:
            models[mid]=dict(id=mid,family="ceiling" if ceiling else "floor",
                             nominal=[3,thickness,3],sockets=[],parts=parts)
        place(ident,mid,x,top,z,category="Ceilings" if ceiling else "Floors",zone=zid,deck=deck)

    for deck, grid in cells.items():
        for (x,z), zid in grid.items():
            # Deck 2 retains a gallery through each core rather than capping
            # the entire bridge and stern atria.
            if deck==2 and lookup[zid]["kind"]=="core" and not core_floor(x,z,zid):
                continue
            slab(f"F_{deck}_{x}_{z}",deck,x,z,floors[deck],.4,zid)
    for ident in ("L1_EXIT_N","L1_EXIT_S","L0_EXIT"):
        zn=lookup[ident];x0,x1,z0,z1=(int(v/3) for v in zn["bounds"])
        for x in range(x0,x1):
            for z in range(z0,z1):
                slab(f"F_{ident}_{x}_{z}",zn["deck"],x,z,zn["floor"],.4,ident)

    for (x,z),zid in cells[0].items():
        if lookup[zid]["kind"] in ("corridor","airlock") and zid != "L0_DOCK":
            slab(f"C0_{x}_{z}",0,x,z,floors[0]+6.2,.2,zid,ceiling=True)
    for deck in (1,2):
        for (x,z),zid in cells[deck].items():
            zn=lookup[zid]
            if deck==1 and zn["kind"] != "sector":
                continue
            top=floors[deck]+zn["height"]+.2
            slab(f"C{deck}_{x}_{z}",deck,x,z,top,.2,zid,ceiling=True,
                 holes=zn["kind"]!="core")

    # Keep the original room-scale fixtures and vertical facilities. They are
    # translated as whole prefabs, never scaled with the enlarged ship.
    for zn in zones:
        if zn["kind"] == "cabin":
            tokens=zn["id"].split("_")
            side=tokens[1]
            n=int(tokens[-1])
            pair=(n-1)//4
            number=pair*2+(n-1)%2+1+(6 if side=="S" else 0)
            old_id=f'L{zn["deck"]}_C{number:02}'
        elif zn["kind"] == "sector":
            old_id=zn["id"]
        elif zn["id"] == "L1_BRIDGE":
            old_id="L1_BRIDGE"
        else:
            continue
        if old_id not in old_zones:
            continue
        source=old_zones[old_id]
        dx=zn["bounds"][0]-source["bounds"][0]
        dz=zn["bounds"][2]-source["bounds"][2]
        if old_id=="L1_BRIDGE":
            # Place consoles near the central gallery of the new tapered bow,
            # not at the bounding-box corner outside its stepped outline.
            dx,dz=0,22.5
        for p in old_placements:
            if p["category"] not in ("Props","Structures","Ventilation"):
                continue
            if p["zone"] not in (old_id,old_id+"_BATH"):
                continue
            q=deepcopy(p)
            suffix=p["id"]
            if suffix.startswith(old_id):
                suffix=suffix[len(old_id):]
            else:
                suffix="_"+suffix
            q.update(id=zn["id"]+suffix,x=round(p["x"]+dx,7),
                     z=round(p["z"]+dz,7),y=round(p["y"]+zn["floor"]-source["floor"],7),
                     zone=zn["id"]+("_BATH" if p["zone"].endswith("_BATH") else ""),
                     deck=zn["deck"])
            placements.append(q)
    for zn in zones:
        if zn["kind"] == "support":
            b=zn["bounds"]
            place(zn["id"]+"_DESK","P_Desk",b[0]+.6,zn["floor"],b[2]+.6,
                  category="Props",zone=zn["id"],deck=zn["deck"])
    for platform in [p for p in placements if p["model"]=="P_Mezzanine_3m"]:
        x,y,z=platform["x"],platform["y"],platform["z"]
        prefix=platform["id"]+"_GUARD"
        place(prefix+"_S","P_Rail3",x,y,z,category="Railings",zone=platform["zone"],deck=platform["deck"])
        place(prefix+"_E","P_Rail3",x+3,y,z,-90,category="Railings",zone=platform["zone"],deck=platform["deck"])
        for i,(px,pz) in enumerate(((x,z),(x+3,z),(x+3,z+3))):
            place(prefix+"_POST_"+str(i),"P_RailPost",px,y,pz,
                  category="Railings",zone=platform["zone"],deck=platform["deck"])
    for i,z in enumerate((3,24,45,66,87)):
        for j in (0,1):
            place(f"ENGINE_{i}_{j}","P_Engine",150.15+j*9,0,z,
                  category="Engines")

    return dict(version="C01.SHIP.6.0", unit=3, body=[0,126,0,90],
                shipBounds=[-48,174,-6,96], decks=[dict(id=i,y=floors[i]) for i in (0,1,2)],
                materials=old["materials"], models=list(models.values()),
                placements=placements, zones=zones, gates=gates, airlocks=airlocks, lifts=lifts,
                links=links, coverage=coverage)

if __name__=="__main__":
    data=build()
    out=PROJECT/"Assets/C01ShipV6/Data/ship_v6.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({key:len(data[key]) for key in ("placements","models","zones","gates","lifts")}))
