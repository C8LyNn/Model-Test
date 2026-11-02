#!/usr/bin/env python3
"""C01-17 W19 independent rigid-sweep BVH gate on REAL Blender source + new FBX.
No mesh proxies, AABB substitution, or simulated Unity acceptance.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
SRC=ROOT/"C01InteriorProps_Source"
BLEND=SRC/"Blender/P17-03.blend"
FBX=ROOT/"Assets/C01InteriorProps/Models/P17-03.fbx"
assert BLEND.read_bytes().startswith(b"BLENDER")
assert FBX.read_bytes().startswith(b"Kaydara FBX Binary")
MOVING=("LeverShaft","LeverGrip","PivotAnchorVisual")
FIXED=("TopCap","LeverSocket","SocketRetainer_L","SocketRetainer_R",
       "CoverBolt_L","CoverBolt_R","PanelBolt_LB","PanelBolt_LT","PanelBolt_RB","PanelBolt_RT")

def current(name):
    objects=[o for o in bpy.context.scene.objects if o.name==name]
    assert len(objects)==1,(name,[o.name for o in bpy.context.scene.objects])
    return objects[0]

def world_bvh(o):
    """True mesh-loop triangles in world coordinates, after evaluated pivot transform."""
    mesh=o.data
    mesh.calc_loop_triangles()
    world=[tuple(o.matrix_world@v.co) for v in mesh.vertices]
    faces=[tuple(t.vertices) for t in mesh.loop_triangles]
    assert len(faces)>0 and len(world)>0
    return BVHTree.FromPolygons(world,faces,all_triangles=True)

def inspect_native(kind):
    if kind=="BLEND":
        bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(FBX),axis_forward="-Z",axis_up="Y")
    objects={n:current(n) for n in ("LeverPivot",)+MOVING+FIXED}
    pivot=objects["LeverPivot"]
    assert pivot.type=="EMPTY"
    assert {child.name for child in pivot.children}==set(MOVING),(
        kind,"pivot children",[x.name for x in pivot.children])
    assert all(objects[x].type=="MESH" for x in MOVING+FIXED)
    assert all(o.parent!=pivot for k,o in objects.items() if k in FIXED)
    samples=[]
    initial=pivot.rotation_euler.copy()
    for degrees in range(-45,46,5):
        pivot.rotation_mode="XYZ"
        pivot.rotation_euler[0]=math.radians(degrees)
        bpy.context.view_layer.update()
        source={name:world_bvh(objects[name]) for name in MOVING}
        target={name:world_bvh(objects[name]) for name in FIXED}
        contacts=[]
        for a in MOVING:
            for b in FIXED:
                pairs=source[a].overlap(target[b])
                if pairs:
                    contacts.append({"moving":a,"stationary":b,"triangle_intersections":len(pairs)})
        samples.append({"angle_deg":degrees,"contacts":contacts})
    pivot.rotation_euler=initial
    bpy.context.view_layer.update()
    errors=[s for s in samples if s["contacts"]]
    return {"asset":"P17-03","source":kind,"angles_checked":len(samples),
            "angle_span":[-45,45],"step_deg":5,"sweep_samples":samples,
            "collision_samples":len(errors),"status":"PASS" if not errors else "FAIL"}

reports=[inspect_native("BLEND"),inspect_native("FBX")]
qa=SRC/"QA/PASS19"
qa.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={"model":"P17-03","blender_runtime":bpy.app.version_string,
        "blend_sha256":sha(BLEND),"fbx_sha256":sha(FBX),
        "physical_file_headers":"PASS",
        "source_and_FBX_BVH_triangle_sweep":reports,
        "mesh_collider_behavior_Unity6":"NOT RUN",
        "C01_02_final_independent_QA":"PENDING",
        "source_export_release":"HOLD" if any(x["collision_samples"] for x in reports) else "PRODUCER_NATIVE_MOTION_CANDIDATE",
        "unity":"NOT RUN"}
(qa/"P17-03_PASS19_REAL_BLENDER_FBX_MOTION_QA.json").write_text(json.dumps(report,indent=2)+"\n")
print("PASS19 REAL BVH",json.dumps({"summary":report["source_export_release"],
             "samples":[{"source":x["source"],"collision_samples":x["collision_samples"]} for x in reports],
             "blend_sha256":report["blend_sha256"],"fbx_sha256":report["fbx_sha256"]}),flush=True)
if any(x["collision_samples"] for x in reports):
    raise RuntimeError("W19 P17-03 STILL COLLIDES in real BVH: "+repr(
        [(x["source"],[s for s in x["sweep_samples"] if s["contacts"]][:3]) for x in reports]))
