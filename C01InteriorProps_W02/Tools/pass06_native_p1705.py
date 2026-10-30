#!/usr/bin/env python3
"""PASS06 native source repair, P17-05 ONLY. Requires REAL Blender 4.x.
Preserves all source mesh data; moves the already-authored metallic display rail 1 mm
towards the front (-Y in native Blender after glTF Y-up import). Fails closed
if PASS03 source identities differ. Re-exports actual binary FBX and reimports.
Usage: blender -b -t 2 --factory-startup --python-exit-code 1 \
  --python C01InteriorProps_W02/Tools/pass06_native_p1705.py -- REPO_ROOT
"""
import bpy, hashlib, json, math, shutil, sys
from pathlib import Path
from mathutils import Vector

R=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
SRC=R/"C01InteriorProps_W02"
BLEND=SRC/"Blender"/"P17-05.blend"
FBX=R/"Assets/C01InteriorProps/W02/Models/P17-05.fbx"
GLTF=R/"Assets/C01InteriorProps/W02/Models/P17-05.gltf"
SPEC=SRC/"Specs"/"P17-05.json"
OUT=SRC/"QA"/"PASS06"
OUT.mkdir(parents=True,exist_ok=True)
ORIG=OUT/"Originals"
ORIG.mkdir(exist_ok=True)

EXPECTED_BEFORE_BLEND="07be57396ccab85423745dc71db2e820eacd00f8191cb86809091c4d14a6dbbd"
EXPECTED_BEFORE_FBX="3fa314481f87d66f9a878936028b809cd78440d781146a058594e28f3f4e1740"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def fail(message):raise RuntimeError("PASS06 P17-05 FAIL CLOSED: "+str(message))
def check(cond,message):
    if not cond:fail(message)
check(bpy.app.version[0]==4,"require Blender 4.x, got "+bpy.app.version_string)
for f in (BLEND,FBX,GLTF,SPEC):check(f.is_file(),"missing "+str(f))
check(BLEND.read_bytes().startswith(b"BLENDER-"),"native blend signature")
check(FBX.read_bytes().startswith(b"Kaydara FBX Binary"),"native binary FBX signature")
check(sha(BLEND)==EXPECTED_BEFORE_BLEND,"source .blend differs from pinned PASS03; REFUSE overwrite")
check(sha(FBX)==EXPECTED_BEFORE_FBX,"source FBX differs from pinned PASS03; REFUSE overwrite")
g=json.loads(GLTF.read_text())
s=json.loads(SPEC.read_text())
node=next(x for x in g["nodes"] if x["name"]=="LowerDisplayRail")
part=next(x for x in s["parts"] if x["name"]=="LowerDisplayRail")
check(abs(node["translation"][2]-.121)<1e-8,"repaired glTF rail Z must be .121")
check(abs(part["p"][2]-.121)<1e-8,"repaired specification Z must be .121")
check(s["triangle_count"]==240 and s["mesh_parts"]==20,"unexpected source spec")
bcopy=ORIG/"P17-05_BEFORE.blend"
fcopy=ORIG/"P17-05_BEFORE.fbx"
shutil.copyfile(BLEND,bcopy);shutil.copyfile(FBX,fcopy)

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene=bpy.context.scene
mesh=[o for o in scene.objects if o.type=="MESH"]
check(len(mesh)==20,"unexpected native mesh object count")
rail=[o for o in mesh if o.name=="LowerDisplayRail"]
check(len(rail)==1,"missing/duplicate LowerDisplayRail object")
rail=rail[0]
def world_bounds(objs):
    pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],
            [max(p[i] for p in pts) for i in range(3)]]
def snap(objs):
    return {o.name:dict(tris=sum(len(p.vertices)-2 for p in o.data.polygons),
                        local_verts=[tuple(round(float(c),8) for c in v.co) for v in o.data.vertices],
                        uv=[tuple(round(float(k),8) for k in x.uv) for u in o.data.uv_layers for x in u.data],
                        materials=[m.name if m else None for m in o.data.materials],
                        matrix=[[float(a) for a in row] for row in o.matrix_world]) for o in objs}
pre=snap(mesh)
old_world=rail.matrix_world.translation.copy()
# Blender glTF imported axes: source +Z front -> native -Y front.
check(abs(old_world.x)<.015 and abs(old_world.y+.12)<.015 and abs(old_world.z-.957)<.015,
      "original rail is not where PASS03 glTF placement predicts: "+str(tuple(old_world)))
bounds_before=world_bounds(mesh)
empties_before={o.name:tuple(tuple(row) for row in o.matrix_world) for o in scene.objects if o.type=="EMPTY"}

def capture(stage,focus=False):
    cam_data=bpy.data.cameras.new("PASS06_CAPTURE")
    cam=bpy.data.objects.new("PASS06_CAPTURE",cam_data)
    scene.collection.objects.link(cam)
    target=Vector((0,-.11,.96 if focus else .75))
    cam.location=(Vector((.65,-1.95,1.35)) if focus else Vector((2.4,-3.0,2.4)))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    cam_data.type="ORTHO";cam_data.ortho_scale=.95 if focus else 2.7
    scene.camera=cam
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.light="STUDIO"
    scene.display.shading.show_cavity=True
    scene.render.resolution_x=1100;scene.render.resolution_y=1100
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    path=OUT/("P17-05_"+stage+("_DETAIL" if focus else "_SHADED")+".png")
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    return path
before_images=[capture("BEFORE"),capture("BEFORE",focus=True)]

world_delta=Vector((0,-.001,0))
# Move one existing Blender object, no mesh-editing or join across pieces.
if rail.parent:
    rail.location+=rail.parent.matrix_world.inverted().to_3x3()@world_delta
else:
    rail.location+=world_delta
bpy.context.view_layer.update()
check((rail.matrix_world.translation-(old_world+world_delta)).length<1e-7,"wrong native transform after local correction")
after=snap(mesh)
for name,old in pre.items():
    new=after[name]
    for k in ("tris","local_verts","uv","materials"):
        check(old[k]==new[k],name+" source mesh property changed: "+k)
    if name!="LowerDisplayRail":check(old["matrix"]==new["matrix"],name+" unrelated transform changed")
check(sum(x["tris"] for x in after.values())==240,"triangle count changed")
bounds_after=world_bounds(mesh)
check(all(abs(bounds_before[j][i]-bounds_after[j][i])<1e-6 for j in range(2) for i in range(3)),
      "outer silhouette extents changed")
check(empties_before=={o.name:tuple(tuple(row) for row in o.matrix_world) for o in scene.objects if o.type=="EMPTY"},
      "empty/root pivot hierarchy moved")
after_images=[capture("AFTER"),capture("AFTER",focus=True)]
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.object.select_all(action="DESELECT")
for o in scene.objects:
    if o.type in ("MESH","EMPTY"):o.select_set(True)
bpy.context.view_layer.objects.active=mesh[0]
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={"MESH","EMPTY"},
  axis_forward="-Z",axis_up="Y",apply_unit_scale=True,global_scale=1.0,bake_anim=False)
check(BLEND.read_bytes().startswith(b"BLENDER-"),"new .blend signature invalid")
check(FBX.read_bytes().startswith(b"Kaydara FBX Binary"),"new binary FBX signature invalid")
check(sha(BLEND)!=EXPECTED_BEFORE_BLEND and sha(FBX)!=EXPECTED_BEFORE_FBX,
      "new native files identical despite expected position correction")
post_blend_sha=sha(BLEND);post_fbx_sha=sha(FBX)

# Actual FBX reimport into a fresh Blender scene, independent of source datablocks.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FBX),axis_forward="-Z",axis_up="Y")
imported=[o for o in bpy.context.scene.objects if o.type=="MESH"]
check(len(imported)==20,"FBX changed number of mesh parts")
check(sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in imported)==240,
      "FBX triangle count changed")
check(all(o.data.uv_layers and len(o.data.uv_layers.active.data)>0 for o in imported),
      "FBX lost UV0")
check(all(all(p.area>1e-10 for p in o.data.polygons) for o in imported),
      "FBX contains degenerate face")
bpy.context.view_layer.update()
bounds_reimport=world_bounds(imported)
check(all(abs(bounds_after[j][i]-bounds_reimport[j][i])<.005 for j in range(2) for i in range(3)),
      "FBX imported extent changed")
check(any("LowerDisplayRail" in o.name for o in imported),"FBX rail missing")
report=dict(model_id="P17-05",execution="REAL BLENDER 4.x",blender_version=bpy.app.version_string,
   source_before_blend_sha256=EXPECTED_BEFORE_BLEND,source_after_blend_sha256=post_blend_sha,
   fbx_before_sha256=EXPECTED_BEFORE_FBX,fbx_after_sha256=post_fbx_sha,
   moved_mesh="LowerDisplayRail",world_delta_m=list(world_delta),triangles_before=240,triangles_after=240,
   mesh_parts_before=20,mesh_parts_after=20,bounds_before=bounds_before,bounds_after=bounds_after,
   bounds_after_reimport=bounds_reimport,uv0="PASS 20/20",material_names_unchanged=True,
   all_mesh_vertices_unchanged=True,empty_pivots_unchanged=True,
   blender_source="PASS",fbx_roundtrip="PASS",unity="NOT RUN",independent_c01_02="PENDING",
   renders=[str(p.relative_to(R)) for p in before_images+after_images])
(OUT/"P17-05_NATIVE_REPAIR_RESULT.json").write_text(json.dumps(report,indent=2)+"\n")
print("PASS06 REAL BLENDER SOURCE+FBX",json.dumps(report),flush=True)
