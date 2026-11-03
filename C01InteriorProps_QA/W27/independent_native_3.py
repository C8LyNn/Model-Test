#!/usr/bin/env python3
"""C01-02 W27: independent read-only signed BLEND/FBX Blender4 acceptance.
Original producer tests are NOT imported. This file never saves or exports any asset.
Use: blender -b -t 2 --python independent_native_3.py -- $GITHUB_WORKSPACE/producers
"""
import bpy, sys, math, json, hashlib, pathlib, collections, importlib.util, traceback
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/"C01InteriorProps_QA"/"W27"/"runtime-results"
OUT.mkdir(parents=True,exist_ok=True)
SPECS={
 "P15-03": ("p15","Assets/C01InteriorProps/P15/Sources/Blender/P15-03.blend",
            "Assets/C01InteriorProps/P15/Models/FBX/P15-03.fbx",
            "e787a9455baa08d5e6b198b4c47d236376b240e08781792020b93be899ca38de",
            "ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149",34,672),
 "P18-03": ("p18","Assets/C01InteriorProps/C01-18/Sources/P18-03.blend",
            "Assets/C01InteriorProps/C01-18/Models/P18-03.fbx",
            "1c8086b048ac1c62a6791bea5df22a22168b5aea4bc17008a2ce233d86ede41e",
            "f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f",63,1780),
 "P19-03": ("p19","Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.blend",
            "Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.fbx",
            "ce43931f9116fe3aef6f795c98e505665c921e6c1080c7d61c5cd518e7f7f5b8",
            "4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967",5,128)
}
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def hash_verified(p,sha,magic):
    require(p.is_file(),f"missing actual native bytes: {p}")
    raw=p.read_bytes()
    measured=hashlib.sha256(raw).hexdigest()
    require(measured==sha,f"{p.name} actual SHA {measured} != {sha}")
    require(raw.startswith(magic),f"{p.name} incorrect native file magic")
    return {"full_sha256":measured,"bytes":len(raw)}
def meshes():return {o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
def world_vertices(o):return [o.matrix_world @ v.co for v in o.data.vertices]
def box(o):
    vertices=world_vertices(o)
    return [[min(v[k] for v in vertices),max(v[k] for v in vertices)] for k in range(3)]
def snapshot(asset):
    objs=meshes(); total=0; verts=0; bad_uv=0; tiny=0; n_gons=0; matrices={}
    triangles=collections.Counter(); normals=0; materials=0
    bbmin=[math.inf]*3;bbmax=[-math.inf]*3
    for name,o in objs.items():
        m=o.data
        m.calc_loop_triangles()
        tris=len(m.loop_triangles);total+=tris;verts+=len(m.vertices)
        n_gons+=sum(len(p.vertices)>4 for p in m.polygons)
        require(m.uv_layers.active is not None,f"{asset}: {name} missing UV0")
        materials+=int(bool(m.materials))
        require(bool(m.polygons),f"{asset}: {name} empty mesh")
        uv=m.uv_layers.active.data
        points=world_vertices(o)
        for v in points:
            for k in range(3):bbmin[k]=min(bbmin[k],v[k]);bbmax[k]=max(bbmax[k],v[k])
        for tri in m.loop_triangles:
            a,b,c=[points[i] for i in tri.vertices]
            area=(b-a).cross(c-a).length*.5
            if area <1e-12: tiny+=1
            # quantized world-space triangle identity (tolerant to FBX precision)
            sig=tuple(sorted(tuple(round(z*10000) for z in xyz) for xyz in (a,b,c)))
            triangles[(name,sig)]+=1
            u0,u1,u2=[uv[i].uv for i in tri.loops]
            uvarea=abs((u1-u0).cross(u2-u0))*.5
            if not math.isfinite(uvarea) or uvarea<1e-11:bad_uv+=1
            poly=m.polygons[tri.polygon_index]
            if poly.normal.length<.99:normals+=1
        matrices[name]=[list(row) for row in o.matrix_world]
    require(materials==len(objs),f"{asset}: mesh without material slots")
    require(tiny==0,f"{asset}: {tiny} degenerate 3D triangles")
    require(bad_uv==0,f"{asset}: {bad_uv} zero-UV-area triangulated polygons")
    require(normals==0,f"{asset}: {normals} invalid geometric normals")
    return {"meshes":len(objs),"vertices":verts,"triangles":total,"ngons":n_gons,
            "zero_uv_triangles":bad_uv,"degenerate_triangles":tiny,
            "aabb_min":bbmin,"aabb_max":bbmax,
            "triangle_signatures":triangles,"world_matrices":matrices}
def bvh(o):
    m=o.data;m.calc_loop_triangles()
    verts=world_vertices(o)
    faces=[tuple(t.vertices) for t in m.loop_triangles]
    return BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0),box(o)
def bvh_overlap(a,b):
    # Correct closed AABB overlap. Older producer had this predicate INVERTED.
    if any(a[1][i]>b[2][i] or b[1][i]>a[2][i] for i in range(3)):
        return []
    return a[0].overlap(b[0])
def negative_control():
    a=BVHTree.FromPolygons([(-1,-1,0),(1,-1,0),(0,1,0)],[(0,1,2)],all_triangles=True)
    b=BVHTree.FromPolygons([(0,-.2,-1),(0,-.2,1),(0,.7,0)],[(0,1,2)],all_triangles=True)
    require(len(a.overlap(b))>0,"BVH negative control failed to detect real crossing")
def check_p15():
    obj=meshes();door=bpy.data.objects.get("P15-03_Door_ROOT")
    body=bpy.data.objects.get("P15-03_Body_ROOT")
    require(door and body and door!=body,"missing independent cabin body / internal hinge roots")
    fixed={n:bvh(o) for n,o in obj.items() if o.parent==body}
    moving={n:o for n,o in obj.items() if o.parent==door}
    require(len(moving)>0 and len(fixed)>0 and len(moving)+len(fixed)==34,
            "missing/incorrect original cabinet moving hierarchy")
    require(max(abs(a-b) for a,b in zip(door.matrix_world.translation,(-.352,-.138,0)))<1e-4,
            "hinge root pivot moved")
    negative_control()
    old=tuple(door.rotation_euler)
    counts={"critical_samples":0,"full_samples":0,"critical_pairs":0,"full_pairs":0}
    critical={"DoorSkin","Hinge_Lower_Sleeve","Hinge_Upper_Sleeve"}
    fixed_critical={"Hinge_Lower_Mount","Hinge_Upper_Mount","Hinge_Lower_LowerEar",
                    "Hinge_Lower_UpperEar","Hinge_Upper_LowerEar","Hinge_Upper_UpperEar",
                    "Hinge_Lower_AxlePin","Hinge_Upper_AxlePin"}
    try:
        for subset,angles,tag in [
            (critical,[x*.25 for x in range(361)],"critical"),
            (None,list(range(0,91,2)),"full")
        ]:
            for angle in angles:
                door.rotation_euler[2]=-math.radians(angle)
                bpy.context.view_layer.update()
                for name,o in moving.items():
                    if subset and name not in subset:continue
                    mesh=bvh(o)
                    for fn,static in fixed.items():
                        if subset and fn not in fixed_critical:continue
                        hits=bvh_overlap(mesh,static)
                        if hits:raise AssertionError(
                          f"P15-03 {tag}: angle={angle} {name} x {fn} BVH triangle witnesses={hits[:3]}")
                counts[tag+"_samples"]+=1
    finally:
        door.rotation_euler=old;bpy.context.view_layer.update()
    require(counts["critical_samples"]==361 and counts["full_samples"]==46,"incomplete motion sweep")
    return counts
def check_p18():
    obj=meshes();witness={};total_samples=0
    for wheel in ("Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF"):
        require(wheel in obj,f"{wheel} missing original rubber wheel")
        bbox=box(obj[wheel]); require(abs(bbox[1][0])<.001,f"{wheel} wheel no ground contact")
        require(abs((bbox[1][1]-bbox[1][0])-.210)<.0002,f"{wheel} wheel radius changed")
        center=Vector([(v[0]+v[1])*.5 for v in bbox])
        side=wheel.split("_")[1][0]
        for suffix in ("In","Out"):
            fork=("Outer" if suffix=="In" else "Inner") if side=="L" else ("Inner" if suffix=="In" else "Outer")
            hub=obj.get(wheel+"_Hub_"+suffix); fixed=obj.get(wheel+"_Fork"+fork)
            require(hub is not None and fixed is not None,f"{wheel} missing hub/fork")
            fixedbv=bvh(fixed)
            orig=hub.matrix_world.copy()
            min_gap=math.inf
            try:
                for angle in range(0,361,5):
                    rot=Matrix.Translation(center) @ Matrix.Rotation(math.radians(angle),4,"X") @ Matrix.Translation(-center)
                    hub.matrix_world=rot@orig;bpy.context.view_layer.update()
                    box_h=box(hub)[0];box_f=fixedbv[1][0]
                    gap=max(box_h[0]-box_f[1],box_f[0]-box_h[1])
                    min_gap=min(min_gap,gap)
                    hits=bvh_overlap(bvh(hub),fixedbv)
                    if hits:raise AssertionError(f"P18-03 {wheel} hub-{suffix}/fork-{fork} angle={angle} hits={hits[:3]}")
                    total_samples+=1
            finally:
                hub.matrix_world=orig;bpy.context.view_layer.update()
            require(.0018<=min_gap<=.0022,f"P18-03 {wheel} {suffix} axial gap {min_gap}")
            witness[wheel+"_"+suffix+"/"+fork]=round(min_gap,8)
    require(total_samples==584,"incomplete 8*73 swept wheel verification")
    return {"samples":total_samples,"minimum_gap_m":min(witness.values()),"eight_interfaces_m":witness,
            "collider_policy":"source-only, NOT Unity PhysX"}
def compact(s):
    return {k:v for k,v in s.items() if k not in ("triangle_signatures","world_matrices")}
def run_one(asset, base, binary_parser):
    ref,bl,fb,sha_bl,sha_fb,mcount,tcount=SPECS[asset]
    root=base/ref;bp=root/bl;fp=root/fb
    receipt={"id":asset,"producer_revision":ref,"status":"HOLD","unity":"NOT_RUN",
             "evidence_kind":"independent real Blender4 BLEND open + original binary FBX import"}
    try:
        receipt["native_blend"]=hash_verified(bp,sha_bl,b"BLENDER")
        receipt["native_fbx"]=hash_verified(fp,sha_fb,b"Kaydara FBX Binary")
        raw=binary_parser.analyze(fp.read_bytes())
        receipt["independent_raw_fbx"]={k:v for k,v in raw.items() if k!="parts"}
        require(raw["meshes"]==mcount,f"{asset}: raw FBX parts {raw['meshes']}")
        require(raw["zero_area_UV_polygons_with_positive_3D_area"]==0,
                f"{asset}: raw original FBX has collapsed UV0")
        require(raw["opposite_polygon_corner_normals"]==0,
                f"{asset}: raw original FBX has inverted corner normals")
        bpy.ops.wm.open_mainfile(filepath=str(bp))
        blend=snapshot(asset);require(blend["meshes"]==mcount and blend["triangles"]==tcount,
                                      f"{asset} native BLEND count change")
        if asset=="P15-03":receipt["blend_motion"]=check_p15()
        if asset=="P18-03":receipt["blend_wheel_motion"]=check_p18()
        if asset=="P19-03":require(blend["ngons"]==0 and blend["vertices"]==72,"P19-03 real native mesh not triangulated")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(fp))
        imp=snapshot(asset);require(imp["meshes"]==mcount and imp["triangles"]==tcount,
                                    f"{asset} FBX reimport count change")
        require(max(abs(a-b) for a,b in zip(blend["aabb_min"]+blend["aabb_max"],
                                              imp["aabb_min"]+imp["aabb_max"]))<.0001,
                f"{asset} source to FBX world AABB changed")
        if asset=="P15-03":receipt["fbx_motion"]=check_p15()
        if asset=="P18-03":receipt["fbx_wheel_motion"]=check_p18()
        if asset=="P19-03":
            require(imp["ngons"]==0 and imp["vertices"]==72,"P19-03 FBX n-gons/vertices not stable")
            require(blend["triangle_signatures"]==imp["triangle_signatures"],
                    "P19-03 exact world triangle sets mismatch after FBX import")
            receipt["triangle_equivalence"]="world triangle signatures 128/128 equal at 0.1mm grid"
        receipt["blend"]=compact(blend);receipt["imported_fbx"]=compact(imp)
        receipt["status"]="INDEPENDENT_NEW_SHA_STATIC_AND_MOTION_PASS__UNITY_HOLD" if asset!="P19-03" else "INDEPENDENT_NEW_SHA_STATIC_PASS__UNITY_HOLD"
    except Exception as e:
        receipt["status"]="INDEPENDENT_NEW_SHA_FAIL_OR_NOT_RUN__HOLD"
        receipt["failure"]=str(e);receipt["traceback"]=traceback.format_exc(limit=4)
    (OUT/(asset+"_W27_INDEPENDENT.json")).write_text(json.dumps(receipt,indent=2)+"\n")
    print("C01_W27_INDEPENDENT",asset,receipt["status"],receipt.get("failure",""),flush=True)
    return receipt
def main():
    require(bpy.app.version[0]==4,"Real Blender 4 required")
    i=sys.argv.index("--"); base=pathlib.Path(sys.argv[i+1]).resolve()
    src=ROOT/"C01InteriorProps_QA"/"GLOBAL_MESH_W26"/"W26_FBX_POLYGON_QA.py"
    mod=importlib.util.module_from_spec(importlib.util.spec_from_file_location("c01_w26_fbx",src))
    mod.__spec__.loader.exec_module(mod)
    results=[run_one(a,base,mod) for a in SPECS]
    summary={"scope":"C01-02 independent, no Claude doors/no exported assets/no Unity",
             "blender":bpy.app.version_string,"per_model":[{"id":x["id"],"status":x["status"],"failure":x.get("failure")} for x in results],
             "unity":"OWNER_ACTION_REQUIRED","release":"HOLD"}
    (OUT/"W27_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
    if not all("PASS" in x["status"] for x in results):sys.exit(1)
main()
