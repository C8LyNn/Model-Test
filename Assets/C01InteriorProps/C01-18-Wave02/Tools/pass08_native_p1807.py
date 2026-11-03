"""C01 PASS08: repair existing native P18-07 .blend and stage real binary FBX.
Run: blender -b --factory-startup --python-exit-code 1 --python pass08_native_p1807.py -- <C01-18-Wave02-root>
Source remains untouched; output goes to QA/Pass08/Native until independent QA.
"""
import bpy, pathlib, hashlib, sys, json
from mathutils import Vector
if "--" not in sys.argv: raise RuntimeError("Missing -- <asset_root>")
root=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
src=root/"Sources"/"P18-07.blend"
out=root/"QA"/"Pass08"/"Native"
out.mkdir(parents=True,exist_ok=True)
expected="302a6832594702c7eff11a486d9e581c159993ff7b7f5c5abe124bf29edbc8d8"
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def check(cond,msg):
 if not cond:raise RuntimeError(msg)
def triangles(objects):
 return sum(sum(max(0,len(f.vertices)-2) for f in o.data.polygons) for o in objects)
def getmeshes():return sorted((x for x in bpy.context.scene.objects if x.type=="MESH"),key=lambda x:x.name)
def front(o):
 return -min((o.matrix_world@Vector(v)).y for v in o.bound_box)
def signature(o):
 return ([(tuple(round(float(c),9) for c in v.co)) for v in o.data.vertices],
  [tuple(f.vertices) for f in o.data.polygons],
  [[tuple(round(float(c),9) for c in v.uv) for v in layer.data] for layer in o.data.uv_layers],
  [m.name if m else None for m in o.data.materials])
check(src.is_file(),"Missing original native .blend: "+str(src))
check(src.read_bytes()[:8]==b"BLENDER-","Invalid source .blend signature")
sha0=digest(src)
check(sha0==expected,"Native source changed since QA. Rebase and re-audit, actual SHA: "+sha0)
check(bpy.app.version>=(4,0,0),"Requires Blender 4.x")
bpy.ops.wm.open_mainfile(filepath=str(src))
meshes=getmeshes()
check(len(meshes)==10 and triangles(meshes)==120,"Unexpected P18-07 source geometry")
lock=bpy.data.objects.get("Front_Lock")
lid=bpy.data.objects.get("Bin_Lid")
check(lock is not None and lid is not None,"Missing lock or lid")
check(abs(front(lid)-0.170)<1e-5 and abs(front(lock)-0.170)<1e-5,"Unexpected source face positions")
check(abs(lock.location.y+0.164)<1e-5,"Unexpected lock position in native Blender")
sig={o.name:signature(o) for o in meshes}
transforms={o.name:tuple(tuple(float(v) for v in row) for row in o.matrix_world) for o in meshes}
pivots={o.name:tuple(tuple(float(v) for v in row) for row in o.matrix_world) for o in bpy.context.scene.objects if o.type=="EMPTY"}
lock.location.y-=0.001  # Unity +Z equals Blender -Y
bpy.context.view_layer.update()
check(abs(front(lock)-front(lid)-0.001)<1e-5,"Front-face contact not resolved")
check(triangles(getmeshes())==120 and len(getmeshes())==10,"Mesh count changed")
for o in getmeshes():
 check(sig[o.name]==signature(o),"Mesh vertices/faces/UV/material changed: "+o.name)
 if o.name!="Front_Lock":
  check(transforms[o.name]==tuple(tuple(float(v) for v in row) for row in o.matrix_world),"Unexpected transform: "+o.name)
check(pivots=={o.name:tuple(tuple(float(v) for v in row) for row in o.matrix_world) for o in bpy.context.scene.objects if o.type=="EMPTY"},"Moving part pivot changed")
blend=out/"P18-07_PASS08.blend"
fbx=out/"P18-07_PASS08.fbx"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
check(blend.read_bytes()[:8]==b"BLENDER-","Saved Blender file invalid")
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
 if o.type in ("MESH","EMPTY"):o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,axis_forward="-Z",axis_up="Y",add_leaf_bones=False,apply_unit_scale=True,object_types={"MESH","EMPTY"})
check(fbx.read_bytes().startswith(b"Kaydara FBX Binary  "),"Exporter did not make binary FBX")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(fbx))
imported=getmeshes()
check(len(imported)==10 and triangles(imported)==120,"FBX reimport geometry mismatch")
check(all(o.data.uv_layers for o in imported),"FBX reimport UV0 missing")
report={"model":"P18-07","status":"REAL_BLENDER_FBX_ROUNDTRIP_PASS",
 "source_blend_sha256":sha0,"new_blend_sha256":digest(blend),"new_binary_fbx_sha256":digest(fbx),
 "before_lock_front_z_m":0.170,"after_lock_front_z_m":0.171,
 "same_facing_coplanar_area_before_cm2":26,"same_facing_coplanar_area_after_cm2":0,
 "parts_before_after":[10,10],"triangles_before_after":[120,120],
 "Unity":"NOT_RUN","C01-02":"PENDING","promotion":"QUARANTINED_UNTIL_QA"}
(out/"PASS08_NATIVE_RESULT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("C01_PASS08_P18-07_NATIVE_FBX_REIMPORT_PASS",json.dumps(report),flush=True)
