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
    "Sources/Blender/P15-03.blend": "e787a9455baa08d5e6b198b4c47d236376b240e08781792020b93be899ca38de",
    "Models/FBX/P15-03.fbx": "ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149",
    "Models/FBX/P15-03_Body.fbx": "28b5ac854c9ecd869c587a6e337e3cc76919141a1fad38ab2d0a078ab0f6802c",
    "Models/FBX/P15-03_Door.fbx": "c4a7aa9fd054b7106faf692868681290f6880e45f0e0a7d7bcc52f5e88ad0d7d",
}
SPEC_SHA = "9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3"
REPORT = {
    "gate": "C01-15_PASS26_POST_UV_REAL_NATIVE_P15-03_HINGE_SWEEP_FIXED_AABB",
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
    return all(a[1][i] <= b[2][i] and b[1][i] <= a[2][i] for i in range(3))
def triangle_hits(a,b):
    if not aabb_intersect(a,b):
        return []
    return a[0].overlap(b[0])

def real_uv_zero_area_count(ob):
    m=ob.data
    u=m.uv_layers.active
    if not u:return -1
    n=0
    for p in m.polygons:
        ll=list(p.loop_indices)
        for j in range(1,len(ll)-1):
            a,b,c=[u.data[ll[k]].uv for k in (0,j,j+1)]
            n += abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5<1e-10
    return n

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
    uv_bad={name:real_uv_zero_area_count(ob) for name,ob in objs.items()}
    receipt(label+"_NEW_FBXd_UV0_no_collapsed_triangles",sum(uv_bad.values())==0,
        {"total":sum(uv_bad.values()),"details":{k:v for k,v in uv_bad.items() if v}})
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


def render_true_mesh_wire_from_actual_signed_fbx():
    """Actual Blender Workbench shaded and triangle-edge geometry overlay; no exporter."""
    meshes=[o for o in bpy.data.objects if o.type=="MESH"]
    camera_data=bpy.data.cameras.new("C01_PASS26_TEMP_CAMERA")
    cam=bpy.data.objects.new("C01_PASS26_TEMP_CAMERA",camera_data)
    bpy.context.scene.collection.objects.link(cam)
    target=__import__("mathutils").Vector((0,0,.9))
    cam.location=target+__import__("mathutils").Vector((4.4,-5.2,4.0))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    camera_data.type="ORTHO";camera_data.ortho_scale=3.2
    sc=bpy.context.scene;sc.camera=cam;sc.render.engine="BLENDER_WORKBENCH"
    sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
    sc.render.resolution_x=900;sc.render.resolution_y=700;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"
    def snap(name):
        path=OUT/name;sc.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        receipt("genuine_workbench_image_"+name,path.is_file() and path.stat().st_size>1000)
    snap("P15-03_POST_UV_SHADED.png")
    mat=bpy.data.materials.new("C01_PASS26_TEMP_VISIBLE_BLACK_TRI_EDGE")
    mat.diffuse_color=(.015,.015,.018,1)
    overlay=[]
    for obj in meshes:
        wire=obj.copy()
        wire.data=obj.data.copy()
        bpy.context.scene.collection.objects.link(wire)
        wire.name="C01_PASS26_TEMP_WIRE_"+obj.name
        wire.data.materials.clear()
        wire.data.materials.append(mat)
        wire.modifiers.new("C01_TEMP_REAL_TRIANGULATION","TRIANGULATE")
        edge=wire.modifiers.new("C01_TEMP_TRUE_TRIANGLE_EDGE_TUBES","WIREFRAME")
        edge.thickness=.0018;edge.offset=1;edge.use_replace=True
        overlay.append(wire)
    bpy.context.view_layer.update()
    snap("P15-03_POST_UV_REAL_TRIANGLE_WIREFRAME.png")
    # Source originals are not saved and the overlays are never exported.
    for obj in overlay:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.objects.remove(cam,do_unlink=True)

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
    render_true_mesh_wire_from_actual_signed_fbx()
    REPORT["result"]="NATIVE_POST_UV_MOTION_BVH_AND_TRUE_WIREFRAME_PASS_INDEPENDENT_QA_PENDING"

try:
    main()
except Exception as exc:
    REPORT["error"]=repr(exc)
    REPORT["result"]="HOLD"
finally:
    (OUT/"P15-03_PASS26_POST_UV_NATIVE_MOTION.json").write_text(
        json.dumps(REPORT,indent=2)+"\n",encoding="utf-8")
    print("C01_PASS19_RESULT",json.dumps(
        {"result":REPORT["result"],"checks":len(REPORT["stages"]),
         "error":REPORT.get("error"),"sha":REPORT["files"]}))
if REPORT["result"]=="HOLD":
    sys.exit(1)
