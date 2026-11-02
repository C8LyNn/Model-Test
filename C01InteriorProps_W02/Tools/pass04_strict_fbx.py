#!/usr/bin/env python3
"""PASS04 actual Blender source vs imported binary FBX topology audit."""
import bpy, bmesh, collections, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
W02="C01InteriorProps_W02" in str(Path(__file__).resolve())
SRC=ROOT/("C01InteriorProps_W02" if W02 else "C01InteriorProps_Source")
MODEL=ROOT/("Assets/C01InteriorProps/W02/Models" if W02 else "Assets/C01InteriorProps/Models")
IDS=["P17-04","P17-05","P17-06","P17-07"] if W02 else ["P17-01","P17-02","P17-03"]
OUT=SRC/"QA"/"PASS04"; OUT.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def q(v): return tuple(round(float(x),5) for x in v)
def analyze(objs):
    parts=[];tri=[];verts=[];edges=[]
    for ob in objs:
        bm=bmesh.new();bm.from_mesh(ob.data)
        dup=sum(n-1 for n in collections.Counter(q(v.co) for v in bm.verts).values() if n>1)
        item=dict(name=ob.name,vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),
            triangles=sum(len(f.verts)-2 for f in bm.faces),duplicate_coordinate_vertices=dup,
            loose_vertices=sum(not v.link_edges for v in bm.verts),
            zero_edges=sum(e.calc_length()<1e-9 for e in bm.edges),
            boundary_edges=sum(e.is_boundary for e in bm.edges),
            nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
            degenerate_faces=sum(f.calc_area()<1e-10 for f in bm.faces),
            ngons=sum(len(f.verts)>3 for f in bm.faces),
            uv0=bool(ob.data.uv_layers),
            materials=[m.name for m in ob.data.materials if m])
        parts.append(item); bm.free()
        if not item["uv0"] or any(item[x] for x in ["loose_vertices","zero_edges","degenerate_faces"]):
            raise RuntimeError(ob.name+" invalid local mesh "+repr(item))
        mw=ob.matrix_world.copy()
        vv=[mw@v.co for v in ob.data.vertices]
        verts += [(ob.name,v) for v in vv]
        edges += [(ob.name,vv[e.vertices[0]],vv[e.vertices[1]]) for e in ob.data.edges]
        ob.data.calc_loop_triangles()
        uvdata=ob.data.uv_layers.active.data if ob.data.uv_layers else None
        for t in ob.data.loop_triangles:
            pts=[vv[k] for k in t.vertices]
            n=(pts[1]-pts[0]).cross(pts[2]-pts[0])
            if n.length<1e-10: raise RuntimeError("Degenerate triangle "+ob.name)
            tri.append(dict(owner=ob.name,points=pts,normal=n.normalized(),
                key=tuple(sorted(q(x) for x in pts)),uv=[tuple(uvdata[k].uv) for k in t.loops] if uvdata else None))
    return dict(parts=parts,tri=tri,verts=verts,edges=edges)
def tj_scan(data):
    out=[];count=0
    for mesh,v in data["verts"]:
        for owner,a,b in data["edges"]:
            if mesh!=owner:continue
            d=b-a;den=d.length_squared
            if den<1e-12:continue
            t=(v-a).dot(d)/den
            if t<1e-5 or t>1-1e-5:continue
            if (v-(a+d*t)).length < 1e-5:
                count+=1
                if len(out)<20:out.append(dict(mesh=mesh,vertex=q(v),edge_start=q(a),edge_end=q(b)))
    return dict(count=count,samples=out)
def polygon_area(p):
    return abs(sum(p[k][0]*p[(k+1)%len(p)][1]-p[(k+1)%len(p)][0]*p[k][1] for k in range(len(p))))*.5
def clip_area(a,b):
    sign=1 if sum(b[i][0]*b[(i+1)%3][1]-b[(i+1)%3][0]*b[i][1] for i in range(3))>=0 else -1
    poly=list(a)
    for i in range(3):
        s=b[i];e=b[(i+1)%3]
        def side(p):return sign*((e[0]-s[0])*(p[1]-s[1])-(e[1]-s[1])*(p[0]-s[0]))
        if not poly:break
        nxt=[];old=poly[-1];d0=side(old)
        for cur in poly:
            d1=side(cur)
            if (d1>=-1e-10)!=(d0>=-1e-10) and abs(d0-d1)>1e-20:
                t=d0/(d0-d1);nxt.append((old[0]+t*(cur[0]-old[0]),old[1]+t*(cur[1]-old[1])))
            if d1>=-1e-10:nxt.append(cur)
            old=cur;d0=d1
        poly=nxt
    return polygon_area(poly) if len(poly)>2 else 0
def overlap_scan(tris):
    count=0;sample=[]
    for i,t in enumerate(tris):
        for o in tris[i+1:]:
            if t["owner"]==o["owner"] or t["normal"].dot(o["normal"])<.999999:continue
            if any(abs(t["normal"].dot(x-t["points"][0]))>1e-5 for x in o["points"]):continue
            drop=max(range(3),key=lambda k:abs(t["normal"][k]))
            a=[tuple(p[j] for j in range(3) if j!=drop) for p in t["points"]]
            b=[tuple(p[j] for j in range(3) if j!=drop) for p in o["points"]]
            if min(max(p[0] for p in a),max(p[0] for p in b))-max(min(p[0] for p in a),min(p[0] for p in b))<1e-5:continue
            if min(max(p[1] for p in a),max(p[1] for p in b))-max(min(p[1] for p in a),min(p[1] for p in b))<1e-5:continue
            area=clip_area(a,b)
            if area>1e-9:
                count+=1
                if len(sample)<30:sample.append(dict(a=t["owner"],b=o["owner"],area_m2=round(area,9)))
    return dict(count=count,samples=sample,status="CANDIDATES require review; not automatic defects")
def compare(a,b):
    sa=collections.defaultdict(list);sb=collections.defaultdict(list)
    for t in a["tri"]:sa[t["key"]].append(t)
    for t in b["tri"]:sb[t["key"]].append(t)
    missing=sum(max(0,len(ts)-len(sb.get(k,[]))) for k,ts in sa.items())
    extra=sum(max(0,len(ts)-len(sa.get(k,[]))) for k,ts in sb.items())
    flip=sum(not any(x["normal"].dot(t["normal"])>.999 for x in sb.get(k,[])) for k,ts in sa.items() for t in ts)
    uvbad=sum(not any(x["uv"] is not None and len(x["uv"])==3 for x in sb.get(k,[])) for k,ts in sa.items() for t in ts)
    return dict(source_triangles=len(a["tri"]),fbx_triangles=len(b["tri"]),
        missing_triangle_positions=missing,extra_triangle_positions=extra,
        winding_mismatches=flip,uv0_missing_after_fbx=uvbad)
matrix=[]
for id in IDS:
    blend=SRC/"Blender"/(id+".blend");fbx=MODEL/(id+".fbx")
    if not blend.exists() or not fbx.exists():raise RuntimeError("Missing true native binary "+id)
    if not blend.read_bytes().startswith(b"BLENDER") or not fbx.read_bytes().startswith(b"Kaydara FBX Binary"):
        raise RuntimeError("Non-native or LFS pointer binary "+id)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    parents=[o.name for o in bpy.context.scene.objects if o.type=="EMPTY"]
    bpy.context.view_layer.update();src=analyze(objs)
    tj=tj_scan(src);over=overlap_scan(src["tri"])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx),axis_forward="-Z",axis_up="Y")
    new=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    bpy.context.view_layer.update();dst=analyze(new)
    diff=compare(src,dst)
    if len(objs)!=len(new) or any(diff[x] for x in ("missing_triangle_positions","extra_triangle_positions","winding_mismatches","uv0_missing_after_fbx")):
        raise RuntimeError("Real binary source-FBX triangle mismatch "+id+" "+str(diff))
    if tj["count"]:raise RuntimeError("Unexpected SAME-MESH T junction "+id+" "+repr(tj))
    # Root parent naming can differ on FBX import; preserve named functional pivots.
    required={"P17-03":["LeverPivot"],"P17-06":["CoverPivot","SwitchPivot"],"P17-07":["CartridgePivot"]}.get(id,[])
    empties=[o.name for o in bpy.context.scene.objects if o.type=="EMPTY"]
    if any(not any(p in n for n in empties) for p in required):raise RuntimeError("Lost movable pivot "+id)
    data=dict(id=id,blend_sha256=sha(blend),fbx_sha256=sha(fbx),
        before_source=src["parts"],after_fbx=dst["parts"],compare=diff,
        same_mesh_t_junction=tj,cross_part_same_facing_coplanar=over,
        moving_pivots_checked=required,unity="NOT RUN",independent_qa="PENDING",
        non_coplanar_self_intersections="NOT RUN",status="SOURCE_FBX_PASS_COPLANAR_REVIEW" if over["count"] else "SOURCE_FBX_PASS")
    (OUT/(id+"_strict_fbx.json")).write_text(json.dumps(data,indent=2)+"\n")
    matrix.append(dict(id=id,status=data["status"],source_meshes=len(objs),
        source_tris=diff["source_triangles"],fbx_tris=diff["fbx_triangles"],
        same_mesh_t_junctions=tj["count"],crosspart_coplanar_candidates=over["count"],
        blend_sha256=data["blend_sha256"],fbx_sha256=data["fbx_sha256"]))
    print("PASS04 real native FBX",id,matrix[-1],flush=True)
(OUT/"PASS04_MATRIX.json").write_text(json.dumps(dict(results=matrix,unity="NOT RUN",independent_qa="PENDING"),indent=2)+"\n")
print("PASS04 verified real native files",len(matrix),flush=True)
