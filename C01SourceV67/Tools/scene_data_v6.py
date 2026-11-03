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
        height = (12 - (floors[d] - floors[0])) if kind == "core" else 3
        b = [spec[k] * 3 for k in ("x0", "x1", "z0", "z1")]
        y = floors[d]
        z = dict(id=spec["id"], label=spec.get("label") or spec["id"].replace("_", " "),
                 kind=kind, deck=d, floor=y, height=height, bounds=b,
                 parent=spec.get("parent", ""),
                 waypoint=[(b[0]+b[1])/2, y, (b[2]+b[3])/2])
        zones.append(z)
        lookup[z["id"]] = z
        if kind != "void":
            for x in range(spec["x0"], spec["x1"]):
                for zz in range(spec["z0"], spec["z1"]):
                    if z["id"].endswith("_BRIDGE"):
                        inset=max(0, int((-x-1)*.5))
                        if zz < 5+inset or zz >= 24-inset:
                            continue
                    cells[d][x, zz] = z["id"]

    for spec in plan["zones"]:
        if spec["kind"] != "bathroom":
            zone(spec)
    for spec in plan["zones"]:
        if spec["kind"] == "bathroom":
            zone(spec)
    for deck in (0, 1, 2):
        zone(dict(id=f"L{deck}_BRIDGE", kind="core", deck=deck, x0=-16, x1=0, z0=5, z1=24))
        zone(dict(id=f"L{deck}_STERN", kind="core", deck=deck, x0=42, x1=50, z0=5, z1=24))
    zone(dict(id="L1_D3",kind="airlock",deck=1,x0=42,x1=50,z0=23,z1=24,parent="L1_STERN"))
    zone(dict(id="L1_D4",kind="airlock",deck=1,x0=42,x1=50,z0=5,z1=6,parent="L1_STERN"))
    zone(dict(id="L0_DOCK",kind="airlock",deck=0,x0=42,x1=50,z0=19,z1=24,parent="L0_STERN"))
    zone(dict(id="L0_FREIGHT_DOCK",kind="airlock",deck=0,x0=42,x1=50,z0=5,z1=10,parent="L0_STERN"))
    for ident,deck,b in (("L1_EXIT_N",1,[44,46,24,26]),("L1_EXIT_S",1,[44,46,3,5]),
                         ("L0_EXIT",0,[50,58,19,24]),("L0_FREIGHT_EXIT",0,[50,58,5,10]),
                         ("L2_ESCAPE_EXIT",2,[44,46,24,26])):
        world=[v*3 for v in b]
        z=dict(id=ident,label=ident,kind="exterior",deck=deck,floor=floors[deck],height=3,
               bounds=world,parent="",waypoint=[(world[0]+world[1])/2,floors[deck],(world[2]+world[3])/2])
        zones.append(z);lookup[ident]=z

    # Pick an existing V5 gate as a rigid kit: rotations preserve model dimensions.
    def rotate(x, z, yaw):
        a = math.radians(yaw)
        return math.cos(a)*x + math.sin(a)*z, -math.sin(a)*x + math.cos(a)*z

    def gate(ident, deck, a, b, axis, gx, gz, width=3):
        height=3
        x,z,y=gx*3,gz*3,floors[deck]
        yaw=0 if axis=="H" else -90
        pocket=width/6; step=(width-2*pocket)/8; panel_width=step+.01
        def world(px,py,pz):
            dx,dz=rotate(px,pz,yaw);return [x+dx,y+py,z+dz]
        def register(mid,parts):
            if mid not in models:
                models[mid]=dict(id=mid,family="gate",nominal=[3,3,.3],sockets=[],parts=parts)
            return mid
        frame=([box('METAL',[.15,0,-.15],[.23,height,.15]),
                box('METAL',[width-.23,0,-.15],[width-.15,height,.15]),
                box('METAL',[.23,height-.2,-.15],[width-.23,height,.15])]+
               [box('DARK',[u,0,v],[w,height-.2,t]) for u,w in [(.23,pocket),(width-pocket,width-.23)] for v,t in [(-.15,-.09),(.09,.15)]])
        for i,p in enumerate(frame):
            xs=p['outline'][::2];zs=p['outline'][1::2]
            for xi,(x0,x1) in enumerate(vertical_modules([(min(xs),max(xs))])):
                for yi,(y0,y1) in enumerate(vertical_modules([(p['y0'],p['y1'])])):
                    size=[round(x1-x0,7),round(y1-y0,7),round(max(zs)-min(zs),7)]
                    parts=[box(p['role'],[0,0,0],size)]
                    mid=register('G_Piece_'+hashlib.sha1(json.dumps(parts,sort_keys=True).encode()).hexdigest()[:12],parts)
                    place(f'{ident}_FRAME_{i}_{xi}_{yi}',mid,*world(x0,y0,min(zs)),yaw,'GateFrames',a,deck)
        leaves=[]
        for side in (0,1):
            for i in range(4):
                px=pocket+i*step-.005 if side==0 else width/2+i*step-.005
                target=pocket-panel_width if side==0 else width-pocket
                tx,tz=rotate(target-px,0,yaw);pz=-.06+i*.04
                for yi,(y0,y1) in enumerate(vertical_modules([(0,height-.23)])):
                    h=round(y1-y0,7)
                    parts=[box('ACCENT',[0,0,-.011],[.018,h,.011]),box('PANEL',[.018,0,-.011],[panel_width-.018,h,.011]),box('ACCENT',[panel_width-.018,0,-.011],[panel_width,h,.011])]
                    if y0<=.9 and y1>=1:parts.append(box('SCREEN',[.04,.9-y0,-.015],[panel_width-.04,1-y0,-.011]))
                    mid=register(f'G_Leaf_W{round(panel_width*1000)}_H{round(h*1000)}_S{int(y0<=.9 and y1>=1)}',parts)
                    pid=f'{ident}_LEAF_{side}_{i}_{yi}';leaves.append(pid)
                    place(pid,mid,*world(px,.02+y0,pz),yaw,'GateLeaves',a,deck,gate=ident,travel=[tx,0,tz])
        buttons=[]
        for side in (0,1):
            pid=ident+'_BUTTON_'+str(side);buttons.append(pid)
            place(pid,'P_Button',*world(pocket-.28 if side==0 else pocket-.06,1.1,.15 if side==0 else -.15),yaw+180*side,'Buttons',a,deck,buttonGate=ident,buttonFloor=deck)
        g=dict(id=ident,deck=deck,x=x,y=y,z=z,yaw=yaw,width=width,height=height,zones=[a,b],leaves=leaves,buttons=buttons,airlock='',lift='',floor=-1)
        chase_open = deck == 2 and (a.endswith("_MAIN") or b.endswith("_MAIN") or ident == "L2_ESCAPE_GATE")
        if chase_open:
            # Preserve the structural frame and exact cut, but never close the pursuit route.
            removed = set(leaves + buttons)
            placements[:] = [p for p in placements if p["id"] not in removed]
        else:
            gates.append(g)
        for offset in range(0,width,3):cuts[axis,x+offset if axis=='H' else x,z if axis=='H' else z+offset].append([y,y+height])
        for offset in range(3,width,3):
            node_cuts[x+offset if axis=='H' else x,z if axis=='H' else z+offset].append([y,y+height])
        links.append(dict(a=a,b=b,kind='opening' if chase_open else 'gate',gate='' if chase_open else ident));return g


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
        options=safe or ordered
        north_vertical=options[0][0]=="V" and all(e[2]>=15 for e in options)
        edge=options[(len(options)-1)//2 if north_vertical else len(options)//2]
        door_edges[deck, edge] = (a, b)
        gate("G_"+a+"_"+b, deck, a, b, *edge)

    for deck in (0,1,2):
        for name,x in (("D1",13),("D2",27)):
            ident=f"L{deck}_{name}"
            inner=gate(ident+"_A",deck,f"L{deck}_MAIN",ident,"V",x,14)
            outer=gate(ident+"_B",deck,ident,f"L{deck}_MAIN","V",x+2,14)
            if deck != 2:
                inner["airlock"]=outer["airlock"]=ident
                airlocks.append(dict(id=ident,gates=[inner["id"],outer["id"]]))
    for name,inside,outside,pad in (("D3",23,24,"L1_EXIT_N"),("D4",6,5,"L1_EXIT_S")):
        ident="L1_"+name
        inner=gate(ident+"_INNER",1,"L1_STERN",ident,"H",44,inside)
        outer=gate(ident+"_OUTER",1,ident,pad,"H",44,outside)
        inner["airlock"]=outer["airlock"]=ident
        airlocks.append(dict(id=ident,gates=[inner["id"],outer["id"]]))
    inner=gate("L0_EVAC_INNER",0,"L0_EVAC_HANGAR","L0_DOCK","V",42,20,width=9)
    outer=gate("L0_EVAC_OUTER",0,"L0_DOCK","L0_EXIT","V",50,20,width=9)
    inner["airlock"]=outer["airlock"]="L0_EVAC_LOCK"
    airlocks.append(dict(id="L0_EVAC_LOCK",gates=[inner["id"],outer["id"]]))
    gate("L0_DOCK_ACCESS",0,"L0_STERN","L0_DOCK","H",43,19)
    inner=gate("L0_FREIGHT_INNER",0,"L0_FOOD_RESERVE","L0_FREIGHT_DOCK","V",42,6,width=9)
    outer=gate("L0_FREIGHT_OUTER",0,"L0_FREIGHT_DOCK","L0_FREIGHT_EXIT","V",50,6,width=9)
    inner["airlock"]=outer["airlock"]="L0_FREIGHT_LOCK"
    airlocks.append(dict(id="L0_FREIGHT_LOCK",gates=[inner["id"],outer["id"]]))
    gate("L0_FREIGHT_ACCESS",0,"L0_STERN","L0_FREIGHT_DOCK","H",43,10)
    gate("L2_ESCAPE_GATE",2,"L2_STERN","L2_ESCAPE_EXIT","H",44,24)

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
                h = min(lookup[a]["height"], lookup[b]["height"])
            axis, gx, gz = edge
            walls[axis, gx*3, gz*3].append([floors[deck], floors[deck]+h])
            # A taller atrium meets the body above the upper-deck ceiling.
            if deck == 2 and axis == "V" and gx in (0,42) and len(owners)==2:
                high=max(lookup[q]["height"] for q in owners)
                if high > h: walls[axis,gx*3,gz*3].append([floors[deck]+h,floors[deck]+high])

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
                walls["H",x,z].append([floors[0],floors[2]+3])
        for z in range(z0,z1,3):
            for x in (x0,x1):
                walls["V",x,z].append([floors[0],floors[2]+3])
        landings, waypoints = [], []
        for deck in (0,1,2):
            gid = ident+"_LANDING_"+str(deck)
            core_id = f"L{deck}_{core}"
            entrance_z = z1-3 if lift["id"]=="STERN_CARGO_N" else z0
            g = gate(gid,deck,core_id,core_id,"V",x0//3,entrance_z//3)
            g["lift"],g["floor"] = ident,deck
            for p in placements:
                if p["id"] in g["buttons"]:
                    p["buttonLift"],p["buttonFloor"] = ident,deck
            landings.append(gid)
            waypoints.append(dict(position=[x0-.9,floors[deck],entrance_z+1.5]))
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
        for a, b, style in roof_partition(cut_intervals(join_deck_intervals(spans), cuts[axis, x, z]),[3,6.4,8.6]):
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
        for a,b,style in roof_partition(cut_intervals(join_deck_intervals(spans),node_cuts[x,z]),[3,6.4,8.6]):
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
        # Two narrow galleries and lift approaches leave the core open vertically.
        if z == 14: return True
        if owner.endswith("BRIDGE"):
            return (x == -5 and 10 <= z <= 18) or (-8 <= x <= -5 and 12 <= z <= 16)
        return (x in (42,44,45) and 5 <= z <= 23) or (42 <= x <= 46 and (z in (7,20) or 12 <= z <= 16))
    for gallery_deck in (1,2):
        rail_edges=set()
        grid=cells[gallery_deck]
        for (x,z),owner in grid.items():
            if lookup[owner]["kind"]!="core" or not core_floor(x,z,owner) or shaft_cell(x,z):
                continue
            for dx,dz,edge in ((-1,0,("V",x,z)),(1,0,("V",x+1,z)),
                               (0,-1,("H",x,z)),(0,1,("H",x,z+1))):
                near=(x+dx,z+dz)
                if grid.get(near)!=owner or shaft_cell(*near) or core_floor(*near,owner):
                    continue
                # The half-storey bridge stairs need an opening in the gallery rail.
                if gallery_deck==1 and edge in (("V",-5,10),("V",-5,18),("V",44,10),("V",44,18)):
                    continue
                axis,gx,gz=edge;key=(axis,gx*3,gz*3)
                if any(a<=floors[gallery_deck]+1e-6 and b>=floors[gallery_deck]+1.2-1e-6 for a,b in walls.get(key,())):
                    continue
                rail_edges.add(edge)
        rail_nodes=set()
        for axis,x,z in sorted(rail_edges):
            x,z=x*3,z*3
            place(f"R{gallery_deck}_{axis}_{x}_{z}","P_Rail3",x,floors[gallery_deck],z,0 if axis=="H" else -90,
                  "Railings",deck=gallery_deck)
            rail_nodes.add((x,z));rail_nodes.add((x+3,z) if axis=="H" else (x,z+3))
        for x,z in sorted(rail_nodes):
            if gallery_deck==1 and (x,z) in ((-15,30),(-15,33),(-15,54),(-15,57),(132,30),(132,33),(132,54),(132,57)):
                continue
            if any(a<=floors[gallery_deck]+1e-6 and b>=floors[gallery_deck]+1.2-1e-6 for a,b in nodes.get((x,z),())):
                continue
            place(f"RP{gallery_deck}_{x}_{z}","P_RailPost",x,floors[gallery_deck],z,category="Railings",deck=gallery_deck)

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
            if deck>0 and lookup[zid]["kind"]=="core" and not core_floor(x,z,zid):
                continue
            slab(f"F_{deck}_{x}_{z}",deck,x,z,floors[deck],.4,zid)
    for ident in ("L1_EXIT_N","L1_EXIT_S","L0_EXIT","L0_FREIGHT_EXIT","L2_ESCAPE_EXIT"):
        zn=lookup[ident];x0,x1,z0,z1=(int(v/3) for v in zn["bounds"])
        for x in range(x0,x1):
            for z in range(z0,z1):
                slab(f"F_{ident}_{x}_{z}",zn["deck"],x,z,zn["floor"],.4,ident)

    for deck in (1,2):
        for (x,z),zid in cells[deck].items():
            zn=lookup[zid]
            if deck==1:
                continue
            top=floors[deck]+zn["height"]+.2
            slab(f"C{deck}_{x}_{z}",deck,x,z,top,.2,zid,ceiling=True,
                 holes=zn["kind"]!="core")

    # Reflect north cabin fixtures as independent mesh variants, without
    # negative transform scales or non-mirrored bathroom furniture.
    def mirror_model(mid):
        mirrored=mid+"_MIRRORZ"
        if mirrored not in models:
            model=deepcopy(models[mid]);model["id"]=mirrored
            for part in model["parts"]:
                pts=list(zip(part["outline"][::2],part["outline"][1::2]))
                part["outline"]=[v for x,z in reversed(pts) for v in (x,-z)]
            for socket in model.get("sockets",[]):
                socket["position"][2]*=-1;socket["normal"][2]*=-1
            models[mirrored]=model
        return mirrored

    # Rebuild only over-height equipment as shorter models; keep unit scale.
    for source_id in ("P_Pullup", "P_ExamScanner", "P_Purifier", "P_Shuttle"):
        model = deepcopy(models[source_id]); model["id"] = source_id + "_ROOM3"
        for component in model["parts"]:
            if source_id in ("P_Pullup", "P_ExamScanner") and component["y0"] >= 2.8:
                component["y0"], component["y1"] = 2.65, 2.8
        model["parts"] = [p for p in model["parts"] if p["y0"] < 2.8]
        for component in model["parts"]: component["y1"] = min(component["y1"], 2.8)
        model["nominal"][1] = min(model["nominal"][1], 2.8)
        models[model["id"]] = model

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
            continue  # Bridge command stations are built by the final-scene manifest.
        else:
            continue
        if old_id == "L0_FOOD_RESERVE":
            old_id = "L0_CARGO"
        if old_id not in old_zones:
            continue
        source=old_zones[old_id]
        dx=zn["bounds"][0]-source["bounds"][0]
        dz=zn["bounds"][2]-source["bounds"][2]
        if old_id=="L1_BRIDGE":
            # Place consoles near the central gallery of the new tapered bow,
            # not at the bounding-box corner outside its stepped outline.
            dx,dz=0,21
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
            if zn["kind"] == "cabin" and "_N_CABIN_" in zn["id"]:
                q["z"] = round(zn["bounds"][2]+zn["bounds"][3]-q["z"],7)
                q["yaw"] = (-q["yaw"]) % 360
                q["model"] = mirror_model(q["model"])
            # The old sector fit-out was designed for a 12 m volume. Reuse
            # its 3 m stair and ladder modules to reach a 3 m mezzanine inside
            # the new 6 m room; never squash the prefab transforms.
            if zn["kind"] == "sector":
                # Old sector stairs, mezzanines and ducts were designed for taller rooms.
                if p["model"] in ("P_Stair_3m", "P_Ladder_3m", "P_Mezzanine_3m") or p["category"] == "Ventilation":
                    continue
                if p["model"] == "P_Stair_3m" and p["y"] - source["floor"] >= 3:
                    continue
                if p["model"] == "P_Ladder_3m" and p["y"] - source["floor"] >= 3:
                    continue
                if p["model"] == "P_Mezzanine_3m":
                    q["y"] = zn["floor"] + 3
                    q["x"] -= 6  # land exactly on the shortened flight
                if p["model"] == "P_Ladder_3m":
                    q["x"] -= 6
                if p["category"] == "Ventilation":
                    q["y"] = zn["floor"] + 3
                    q["x"] += 3
                    if p["model"] == "P_VentCap":
                        q["x"] += 6
                        q["z"] += 1.5
                        q["yaw"] = (q["yaw"] + 180) % 360
                if p["model"] == "P_ReactorLarge":
                    q["model"] = "P_Reactor"
            if q["model"] in ("P_Pullup", "P_ExamScanner", "P_Purifier", "P_Shuttle"):
                original = q["model"]
                q["model"] += "_ROOM3"
                if original == "P_Purifier":
                    q["z"] = min(q["z"], zn["bounds"][3] - 3.2)
            placements.append(q)
    # Small independent functional assets for long-duration crew services.
    service_models={
        "P_GalleyCounter":[box("METAL",[0,0,0],[2.4,.85,.75]),box("PANEL",[0,.85,0],[2.4,1,.75]),box("SCREEN",[.35,1,0],[1.05,1.04,.55])],
        "P_MessTable":[box("METAL",[.12,0,.12],[.24,.78,.24]),box("METAL",[1.96,0,.12],[2.08,.78,.24]),box("METAL",[.12,0,.96],[.24,.78,1.08]),box("METAL",[1.96,0,.96],[2.08,.78,1.08]),box("PANEL",[0,.78,0],[2.2,.9,1.2])],
        "P_ServiceRack":[box("DARK",[0,0,0],[2.2,2.15,.6]),box("METAL",[0,0,-.025],[2.2,.12,0]),box("METAL",[0,1.02,-.025],[2.2,1.14,0]),box("METAL",[0,2.03,-.025],[2.2,2.15,0])],
        "P_LaundryUnit":[box("PANEL",[0,0,0],[.9,1.15,.8]),box("DARK",[.15,.15,-.025],[.75,.8,0]),box("SCREEN",[.25,.85,-.025],[.65,1.05,0])],
        "P_LoungeBench":[box("METAL",[.1,0,.1],[1.9,.4,.7]),box("BED",[0,.4,0],[2,.58,.8]),box("PANEL",[0,.58,.65],[2,1.05,.8])],
        "P_LifeSupportPanel":[box("DARK",[0,0,0],[1.5,2.2,.55]),box("SCREEN",[.15,.9,-.025],[1.35,1.65,0]),box("METAL",[.15,.25,-.025],[1.35,.35,0])]}
    for mid,parts in service_models.items():
        models[mid]=dict(id=mid,family="prop",nominal=[3,3,3],sockets=[],parts=parts)
    role_by_id={s["id"]:s.get("role","") for s in plan["zones"]}
    for zn in zones:
        if zn["kind"] != "support": continue
        b=zn["bounds"];role=role_by_id.get(zn["id"],"")
        if role=="GALLEY": pair=("P_GalleyCounter","P_ServiceRack")
        elif role=="MESS": pair=("P_MessTable","P_MessTable")
        elif role=="LAUNDRY": pair=("P_LaundryUnit","P_LaundryUnit")
        elif role in ("CREW_LOUNGE","RECREATION","QUIET_ROOM"): pair=("P_LoungeBench","P_MessTable")
        elif role in ("WATER_CONTROL","POWER_CONTROL","ENGINE_MONITORING","COMMUNICATIONS","TELEMEDICINE"): pair=("P_Desk","P_LifeSupportPanel")
        elif role in ("MEDICAL_RECEPTION","RESEARCH_PREP"): pair=("P_Desk","P_Analyser")
        else: pair=("P_Desk","P_ServiceRack")
        for i,mid in enumerate(pair):
            place(zn["id"]+"_SERVICE_"+str(i),mid,b[0]+.6+i*3.8,zn["floor"],b[2]+.6,
                  category="Props",zone=zn["id"],deck=zn["deck"])
        if role=="MESS":
            # Four tables and four benches leave a clear central approach.
            for i in range(2):
                x=b[0]+.6+i*3.8
                place(zn["id"]+"_TABLE_BACK_"+str(i),"P_MessTable",x,zn["floor"],b[2]+6.5,category="Props",zone=zn["id"],deck=zn["deck"])
                place(zn["id"]+"_BENCH_FRONT_"+str(i),"P_LoungeBench",x,zn["floor"],b[2]+1.85,category="Props",zone=zn["id"],deck=zn["deck"])
                place(zn["id"]+"_BENCH_BACK_"+str(i),"P_LoungeBench",x,zn["floor"],b[2]+5.65,category="Props",zone=zn["id"],deck=zn["deck"])
        elif role=="GALLEY":
            place(zn["id"]+"_COUNTER_BACK","P_GalleyCounter",b[0]+.6,zn["floor"],b[2]+6.5,category="Props",zone=zn["id"],deck=zn["deck"])
        elif role=="LAUNDRY":
            for i,x in enumerate((2.5,6.3)):
                place(zn["id"]+"_WASHER_"+str(i),"P_LaundryUnit",b[0]+x,zn["floor"],b[2]+.6,category="Props",zone=zn["id"],deck=zn["deck"])
    for platform in [p for p in placements if p["model"]=="P_Mezzanine_3m"]:
        x,y,z=platform["x"],platform["y"],platform["z"]
        prefix=platform["id"]+"_GUARD"
        place(prefix+"_S","P_Rail3",x,y,z,category="Railings",zone=platform["zone"],deck=platform["deck"])
        # The remaining east edge is protected up to the duct entrance.
        if "P_RailVent" not in models:
            models["P_RailVent"]=dict(id="P_RailVent",family="prop",nominal=[1.4,1.2,.08],sockets=[],
                parts=[box("METAL",[.15,0,-.04],[.21,1.2,.04]),
                       box("METAL",[.21,1.08,-.04],[1.4,1.2,.04])])
        place(prefix+"_E","P_RailVent",x+3,y,z,-90,category="Railings",zone=platform["zone"],deck=platform["deck"])
        # The duct side wall replaces the far east corner post.
        for i,(px,pz) in enumerate(((x,z),(x+3,z))):
            place(prefix+"_POST_"+str(i),"P_RailPost",px,y,pz,
                  category="Railings",zone=platform["zone"],deck=platform["deck"])
    # Half-storey overlook platforms in both atria, each reached by a
    # 1.5 m rising, unit-scale staircase from the main-deck lift gallery.
    for core, anchor in (("BRIDGE", -15), ("STERN", 135)):
        for side, z in (("S", 30), ("N", 54)):
            tag = f"L1_{core}_HALF_{side}"
            place(tag+"_STAIRS", "P_Stair_3m", anchor, floors[1], z+1.2, 180,
                  category="Structures", zone="L1_"+core, deck=1)
            place(tag+"_PLATFORM", "P_Mezzanine_3m", anchor-6, floors[1]+1.5, z,
                  category="Mezzanines", zone="L1_"+core, deck=1)
            for suffix,zz in (("S",z),("N",z+3)):
                place(tag+"_RAIL_"+suffix,"P_Rail3",anchor-6,floors[1]+1.5,zz,
                      category="Railings",zone="L1_"+core,deck=1)
            place(tag+"_RAIL_W","P_Rail3",anchor-6,floors[1]+1.5,z,-90,
                  category="Railings",zone="L1_"+core,deck=1)
    # Alternating partial-width barriers leave an explicit capsule route.
    for mid, height in (("P_ChaseCrate", .6), ("P_ChaseBarrier", 1.5)):
        models[mid] = dict(id=mid, family="prop", nominal=[.55,height,1.15], sockets=[],
            parts=[box("DARK",[0,0,0],[.55,height,1.15]),
                   box("ACCENT",[.02,height-.1,-.02],[.53,height,0])])
    for i,x in enumerate((9,21,33,51,63,75,93,105,117)):
        z = 42.2 if i % 2 == 0 else 43.65
        place(f"L2_CHASE_OBSTACLE_{i:02}", "P_ChaseCrate" if i%3==0 else "P_ChaseBarrier",
              x, floors[2], z, category="ChaseObstacles", zone="L2_MAIN", deck=2)
    for i,z in enumerate((19.5,31.5,43.5,55.5,67.5)):
        for j in (0,1):
            place(f"ENGINE_{i}_{j}","P_Engine",150.15+j*9,0,z,
                  category="Engines")

    return dict(version="C01.SHIP.6.7", unit=3, body=[0,126,15,72],
                shipBounds=[-48,174,9,78], decks=[dict(id=i,y=floors[i]) for i in (0,1,2)],
                materials=old["materials"], models=list(models.values()),
                placements=placements, zones=zones, gates=gates, airlocks=airlocks, lifts=lifts,
                links=links, coverage=coverage)

if __name__=="__main__":
    data=build()
    out=PROJECT/"Assets/C01ShipV67/Data/ship_v67.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({key:len(data[key]) for key in ("placements","models","zones","gates","lifts")}))
