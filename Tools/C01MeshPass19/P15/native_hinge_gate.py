"""C01-15 PASS19: inspect exact existing Blender 4.x / FBX native P15-03 bytes.
Read only: never edits source, generated binaries, or user scenes.
HOLD on collision; diagnostics are independent of earlier offline 2-D calculations.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "Assets/C01InteriorProps/P15"
OUT = ROOT / "C01_PASS19_P15_NATIVE_QA"
OUT.mkdir(parents=True, exist_ok=True)
BINS = {
    "Sources/Blender/P15-03.blend": "1deb3df36a1c87be8fe6ebec7529233b1d9eececa38230f4d9f693bf40fceb9a",
    "Models/FBX/P15-03.fbx": "7be76765763308deb8c0fa9d4c11cec8c74b60777e0199a160ebab088c59189d",
    "Models/FBX/P15-03_Body.fbx": "e03f774da5977f0aeb8dcb7eadf8e09aaf2cd4f16fa184c7ad92c672ee8cc112",
    "Models/FBX/P15-03_Door.fbx": "96f2d542fc0bdb2376642f1ed082ca77c9b03aed28d7bffb0ef6c111a7cca03d",
}
SPEC_SHA = "9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3"
REPORT = {
    "gate": "C01-15_PASS19_REAL_NATIVE_P15-03_HINGE_SWEEP",
    "scope": "existing signed source + hydrated genuine .blend and 3 Blender FBX, no new model export",
    "model": "P15-03", "blender_version": bpy.app.version_string,
    "files": {}, "stages": [], "result": "HOLD",
    "unity_6_urp": "NOT_RUN", "independent_C01_02": "PENDING",
}
def receipt(name, ok, extra=None):
    REPORT["stages"].append({"check": name, "result": "PASS" if ok else "HOLD", "details": extra or {}})
    if not ok:
        raise RuntimeError("FAIL-CLOSED: " + name + ": " + repr(extra))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def corners_and_triangles(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    xyz = [tuple(obj.matrix_world @ v.co) for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    return xyz, tris
def bvh_object(obj):
    xyz, tri = corners_and_triangles(obj)
    if not tri:
        raise RuntimeError("No triangles: " + obj.name)
    low = [min(v[i] for v in xyz) for i in range(3)]
    high = [max(v[i] for v in xyz) for i in range(3)]
    return BVHTree.FromPolygons(xyz, tri, all_triangles=True, epsilon=0.0), low, high
def aabb_intersect(a,b):
    return all(a[1][i] >= b[2][i] and b[1][i] >= a[2][i] for i in range(3))
def triangle_hits(a,b):
    if not aabb_intersect(a,b):
        return []
    return a[0].overlap(b[0])
def check_scene(label, source):
    expected = {p["name"]: p["component"] for p in source["parts"] if p["asset"] == "P15-03"}
    objs = {o.name: o for o in bpy.data.objects if o.type == "MESH"}
    receipt(label + "_exact_34_names", set(objs) == set(expected) and len(objs)==34,
            {"missing": sorted(set(expected)-set(objs)), "extra": sorted(set(objs)-set(expected))})
    body = bpy.data.objects.get("P15-03_Body_ROOT")
    door = bpy.data.objects.get("P15-03_Door_ROOT")
    receipt(label + "_two_separate_roots", body is not None and door is not None and door != body)
    receipt(label + "_parent_hierarchy", all(objs[k].parent == (door if v=="Door" else body)
                for k,v in expected.items()))
    receipt(label + "_uv_normals_triangle_area", all(o.data.uv_layers.active is not None
                and len(o.data.polygons)>0 and all(p.area > 1e-12 for p in o.data.polygons)
                for o in objs.values()))
    receipt(label + "_native_hinge_world_position",
            max(abs(door.matrix_world.translation[i]-v) for i,v in
                enumerate((-0.352,-0.138,0.0))) < 1e-5,
            {"hinge_blender_xyz": list(door.matrix_world.translation)})
    old_rot = tuple(door.rotation_euler)
    fixed = {n:bvh_object(o) for n,o in objs.items() if expected[n] == "Body"}
    moving_names = [n for n in objs if expected[n] == "Door"]
    def sample(degrees, full):
        door.rotation_euler[2] = -math.radians(degrees)
        bpy.context.view_layer.update()
        critical = {"DoorSkin", "Hinge_Lower_Sleeve", "Hinge_Upper_Sleeve"}
        critical_body = {"Hinge_Lower_Mount","Hinge_Upper_Mount",
            "Hinge_Lower_LowerEar","Hinge_Lower_UpperEar",
            "Hinge_Upper_LowerEar","Hinge_Upper_UpperEar",
            "Hinge_Lower_AxlePin","Hinge_Upper_AxlePin"}
        moving = moving_names if full else [n for n in moving_names if n in critical]
        collisions=[]
        for n in moving:
            a = bvh_object(objs[n])
            for name,b in fixed.items():
                if not full and name not in critical_body:
                    continue
                hits = triangle_hits(a,b)
                if hits:
                    collisions.append({"angle_deg": degrees,"moving":n,
                        "fixed":name,"triangle_pairs":len(hits)})
                    if len(collisions)>=8:
                        return collisions
        return collisions
    try:
        # Explicit 0..90 sweep, including extreme and mid positions; 0.25 degrees
        # in hinge-critical region and 2 degrees for every moving-vs-fixed pair.
        critical_clashes=[]
        full_clashes=[]
        for step in range(361):
            critical_clashes += sample(step*.25, False)
            if len(critical_clashes) >= 8:
                break
        if not critical_clashes:
            for angle in range(0,91,2):
                full_clashes += sample(angle,True)
                if len(full_clashes) >= 8:
                    break
    finally:
        door.rotation_euler = old_rot
        bpy.context.view_layer.update()
    detail={"hinge_samples": 361 if not critical_clashes else "stopped_on_collision",
            "full_sweep_samples": 46 if not critical_clashes and not full_clashes else "stopped_on_collision",
            "critical_collision_samples":critical_clashes,
            "full_collision_samples": full_clashes}
    receipt(label+"_actual_world_triangle_motion",not critical_clashes and not full_clashes,detail)
    return {"parts":len(objs),"native_movement":detail}

def main():
    receipt("runtime_blender4", bpy.app.version[0] == 4)
    srcpath = P / "Sources/geometry_spec.json"
    receipt("pinned_authoring_spec_sha", sha(srcpath)==SPEC_SHA,
            {"measured_sha256":sha(srcpath),"expected":SPEC_SHA})
    source=json.loads(srcpath.read_text("utf-8"))
    receipt("source_version_0_1_6",source.get("version")=="0.1.6")
    for rel,expected in BINS.items():
        f=P/rel
        measured=sha(f) if f.is_file() else None
        REPORT["files"][rel]={"sha256":measured,"size":f.stat().st_size if f.is_file() else None}
        receipt("exact_native_sha_"+rel,measured==expected and f.stat().st_size>1024,
                {"expected":expected,"measured":measured})
    receipt("blender_magic", (P/"Sources/Blender/P15-03.blend").read_bytes()[:7]==b"BLENDER")
    receipt("binary_fbx_magic",all((P/f"Models/FBX/{f}").read_bytes().startswith(b"Kaydara FBX Binary")
            for f in ["P15-03.fbx","P15-03_Body.fbx","P15-03_Door.fbx"]))
    bpy.ops.wm.open_mainfile(filepath=str(P/"Sources/Blender/P15-03.blend"))
    REPORT["blend"] = check_scene("blend",source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(P/"Models/FBX/P15-03.fbx"))
    REPORT["fbx"] = check_scene("fbx",source)
    REPORT["result"]="NATIVE_PRODUCER_MOTION_PASS_C01_02_PENDING"

try:
    main()
except Exception as exc:
    REPORT["error"]=repr(exc)
    REPORT["result"]="HOLD"
finally:
    (OUT/"P15-03_PASS19_NATIVE_MOTION.json").write_text(
        json.dumps(REPORT,indent=2)+"\n",encoding="utf-8")
    print("C01_PASS19_RESULT",json.dumps(
        {"result":REPORT["result"],"checks":len(REPORT["stages"]),
         "error":REPORT.get("error"),"sha":REPORT["files"]}))
if REPORT["result"]=="HOLD":
    sys.exit(1)
