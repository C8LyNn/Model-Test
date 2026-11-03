"""W26 C01-19 P19-03 targeted real Blender n-gon repair.
Original exact-SHA BLEND/FBX only. Triangulate ten high-order faces in existing
desk mesh; no weld, no decimate, no vertex movement, no geometry replacement.
Fail closed unless mesh count, world surface envelope, UV sets, hierarchy, and
triangle budget are identical. Native save, FBX export, actual reimport,
Workbench before/after, and exact SHA are compulsory.
Independent C01-02 and Unity remain PENDING.
"""
import bpy,bmesh,hashlib,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
ID="P19-03";D=R/"Models"/ID
BLEND=D/(ID+".blend");FBX=D/(ID+".fbx")
QA=R/"QA"/"PASS26"/"P19-03_NGON_REPAIR";QA.mkdir(parents=True,exist_ok=True)
BEFORE_BLEND="3652b4f738783e3fab0940311d77b5cd9e6435a23ef60c2c7249f209fa4b11cd"
BEFORE_FBX="1bd730b2382879d7d9c2f3d67c4b9646b8ca036c04de663e53b3019c403af2df"
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(BLEND)==BEFORE_BLEND and digest(FBX)==BEFORE_FBX,"SIGNED ORIGINAL BINARY DRIFT"
assert BLEND.read_bytes().startswith(b"BLENDER-v400")
assert FBX.read_bytes().startswith(b"Kaydara FBX Binary")
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
obj=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert len(obj)==5 and sum(len(o.data.vertices) for o in obj)==72
def surface_metrics(items):
 verts=[o.matrix_world@v.co for o in items for v in o.data.vertices]
 lo=[min(float(v[j]) for v in verts) for j in range(3)]
 hi=[max(float(v[j]) for v in verts) for j in range(3)]
 return dict(meshes=len(items),verts=sum(len(o.data.vertices) for o in items),
  tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in items),
  ngons=sum(len(p.vertices)>4 for o in items for p in o.data.polygons),
  uv0_meshes=sum(bool(o.data.uv_layers) for o in items),
  zero_areas=sum(p.area<1e-12 for o in items for p in o.data.polygons),
  world_bounds_min=lo,world_bounds_max=hi)
def uvsets(o):
 if not o.data.uv_layers:return {}
 layer=o.data.uv_layers.active.data
 d={}
 for p in o.data.polygons:
  for li in p.loop_indices:
   index=o.data.loops[li].vertex_index
   val=tuple(round(float(c),7) for c in layer[li].uv)
   d.setdefault(index,set()).add(val)
 return {str(k):sorted(v) for k,v in d.items()}
def workbench(filename,wire=False):
 scene=bpy.context.scene;scene.render.engine="BLENDER_WORKBENCH"
 scene.render.resolution_x=1060;scene.render.resolution_y=780;scene.render.resolution_percentage=100
 meshes=[o for o in scene.objects if o.type=="MESH"]
 vv=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 lo=Vector([min(v[j] for v in vv) for j in range(3)])
 hi=Vector([max(v[j] for v in vv) for j in range(3)])
 mid=(lo+hi)*.5;span=max((hi-lo).length,.5)
 camdata=bpy.data.cameras.new("W26_TEMP_CAM")
 cam=bpy.data.objects.new("W26_TEMP_CAM",camdata)
 bpy.context.collection.objects.link(cam)
 cam.location=mid+Vector((span*1.4,-span*1.8,span*1.2))
 cam.rotation_euler=(mid-cam.location).to_track_quat("-Z","Y").to_euler()
 camdata.type="ORTHO";camdata.ortho_scale=span*1.75
 old_cam=scene.camera;scene.camera=cam
 orig=[(o,o.show_wire,o.show_all_edges) for o in meshes]
 try:
  for o in meshes:o.show_wire=wire;o.show_all_edges=wire
  scene.render.filepath=str(QA/filename);scene.render.image_settings.file_format="PNG"
  bpy.ops.render.render(write_still=True)
  assert (QA/filename).stat().st_size>1000
 finally:
  scene.camera=old_cam;bpy.data.objects.remove(cam,do_unlink=True)
  for o,w,e in orig:o.show_wire=w;o.show_all_edges=e
before=surface_metrics(obj)
assert before["meshes"]==5 and before["verts"]==72 and before["tris"]==128
assert before["ngons"]==10 and before["uv0_meshes"]==5 and before["zero_areas"]==0
hierarchy=[(o.name,o.data.name,o.parent.name if o.parent else None,
  tuple(round(float(x),8) for row in o.matrix_world for x in row)) for o in obj]
vpos={o.name:[tuple(float(x) for x in v.co) for v in o.data.vertices] for o in obj}
uv_before={o.name:uvsets(o) for o in obj}
workbench("BEFORE_ACTUAL_BLENDER_SHADED.png",False)
workbench("BEFORE_ACTUAL_BLENDER_WIREFRAME.png",True)
targets=[o for o in obj if sum(len(p.vertices)>4 for p in o.data.polygons)]
assert len(targets)==1 and targets[0].name=="Leg_-0.64_0.29",[(x.name,x.data.name) for x in targets]
target=targets[0]
bm=bmesh.new();bm.from_mesh(target.data)
ngons=[f for f in bm.faces if len(f.verts)>4]
assert len(ngons)==10
face_info=[dict(old_vertex_indices=[v.index for v in f.verts],
  old_area_m2=float(f.calc_area()),material_index=f.material_index,
  smooth=f.smooth,nverts=len(f.verts)) for f in ngons]
ret=bmesh.ops.triangulate(bm,faces=ngons,quad_method="BEAUTY",ngon_method="EAR_CLIP")
assert len(ret.get("faces",[]))>=10
bm.normal_update()
bm.to_mesh(target.data);bm.free()
target.data.update()
after=surface_metrics(obj)
assert after["meshes"]==5 and after["verts"]==72 and after["tris"]==128
assert after["ngons"]==0 and after["uv0_meshes"]==5 and after["zero_areas"]==0
assert hierarchy==[(o.name,o.data.name,o.parent.name if o.parent else None,
  tuple(round(float(x),8) for row in o.matrix_world for x in row)) for o in obj]
assert vpos=={o.name:[tuple(float(x) for x in v.co) for v in o.data.vertices] for o in obj}
assert uv_before=={o.name:uvsets(o) for o in obj},"UV CORNER SEAM / VALUES DRIFT"
bbox_err=max(abs(float(a)-float(b)) for key in ("world_bounds_min","world_bounds_max")
  for a,b in zip(before[key],after[key]))
assert bbox_err<1e-7,("BBOX DRIFT",bbox_err)
for o in obj:
 bm=bmesh.new();bm.from_mesh(o.data)
 assert all(e.is_manifold for e in bm.edges),(o.name,"MANIFOLD FAIL")
 assert all(f.calc_area()>1e-10 for f in bm.faces),(o.name,"MICRO/DEGENERATE FACE")
 bm.free()
workbench("AFTER_ACTUAL_BLENDER_SHADED.png",False)
workbench("AFTER_ACTUAL_BLENDER_WIREFRAME.png",True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=False)
assert BLEND.read_bytes().startswith(b"BLENDER-v400")
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
 if o.type in {"MESH","EMPTY"}:o.select_set(True)
bpy.context.view_layer.objects.active=target
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,axis_forward="-Z",
 axis_up="Y",apply_unit_scale=True,global_scale=1,bake_anim=False,
 add_leaf_bones=False,object_types={"MESH","EMPTY"})
assert FBX.read_bytes().startswith(b"Kaydara FBX Binary")
original=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(FBX))
imported=[o for o in bpy.context.scene.objects if o not in original]
fbx_mesh=[o for o in imported if o.type=="MESH"]
check=surface_metrics(fbx_mesh)
assert check["meshes"]==5 and check["verts"]==72 and check["tris"]==128,check
assert check["ngons"]==0 and check["zero_areas"]==0 and check["uv0_meshes"]==5,check
roundtrip_bbox=max(abs(a-b) for key in ("world_bounds_min","world_bounds_max")
 for a,b in zip(before[key],check[key]))
assert roundtrip_bbox<1e-4,("FBX WORLD BBOX DRIFT",roundtrip_bbox)
for o in imported:
 if o.type=="MESH":
  bm=bmesh.new();bm.from_mesh(o.data)
  assert all(e.is_manifold for e in bm.edges),(o.name,"FBX NONMANIFOLD")
  assert all(f.calc_area()>1e-10 for f in bm.faces),(o.name,"FBX MICRO")
  bm.free()
# render only actual FBX, without simultaneously displaying source meshes
for o in obj:o.hide_render=True
workbench("AFTER_REAL_FBX_REIMPORT_SHADED.png",False)
for o in obj:o.hide_render=False
for o in imported:bpy.data.objects.remove(o,do_unlink=True)
r=dict(schema="c01-19/p19-03/W26/targeted-ngon-triangulation-v1",
asset_id=ID,old_blend_sha256=BEFORE_BLEND,old_fbx_sha256=BEFORE_FBX,
new_blend_sha256=digest(BLEND),new_fbx_sha256=digest(FBX),
Blender_version=bpy.app.version_string,change="10 existing >4 vertex n-gon faces EAR_CLIP triangulated in one existing mesh; untouched all 72 original vertex positions; no weld, remesh, decimate or model replacement",
modified_mesh=target.name,old_complex_faces=face_info,
before=before,after=after,reimported_current_fbx=check,
unchanged_exact_vertex_positions=True,unchanged_pivots_hierarchy=True,unchanged_UV0_corner_value_sets=True,
max_bbox_shift_m=bbox_err,reimport_bbox_delta_m=roundtrip_bbox,
preview_files=["BEFORE_ACTUAL_BLENDER_SHADED.png","BEFORE_ACTUAL_BLENDER_WIREFRAME.png",
"AFTER_ACTUAL_BLENDER_SHADED.png","AFTER_ACTUAL_BLENDER_WIREFRAME.png","AFTER_REAL_FBX_REIMPORT_SHADED.png"],
c01_02_independent_qa="PENDING_NEW_EXACT_SHA",unity_6_urp="NOT_RUN",release="HOLD_NO_MERGE")
(QA/"REPAIR_AND_ROUNDTRIP.json").write_text(json.dumps(r,indent=2))
print("P19_03_W26_REAL_BLENDER_NGON_REPAIR_PASS",r["new_blend_sha256"],r["new_fbx_sha256"],flush=True)
