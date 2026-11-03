"""C01-19 W29 / P19-01 confirmed P1 mattress↔stripe z-fight: actual Blender 4 native surgical fix.
ONLY signed source BLEND/FBX of existing P19-01. No weld, remesh, new asset IDs,
door or ship edits. Retains original 4 named mesh parts, root, materials, UV0
and all original vertices except the 8 EXISTING stripe Z endpoints.
Raise accent ribbon as 1.55mm physically attached upholstery applique:
stripe bottom penetrates mattress top by just 0.05mm (intentional hidden support),
stripe visible upper surface stands 1.50mm above mattress top (no coplanarity).
Real original and repaired shaded/wire rendered at identical C01-02 camera,
save original native BLEND, export genuine FBX and import physical FBX again.
Independent C01-02 current NEW SHA visual/geometry review required after producer.
"""
import bpy, math, json, hashlib, sys, traceback
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent.parent
ID="P19-01";FILES=ROOT/"Models"/ID
BLEND=FILES/(ID+".blend");FBX=FILES/(ID+".fbx")
QA=ROOT/"QA"/"PASS29"/"P19-01"
QA.mkdir(parents=True,exist_ok=True)
ORIGINAL_BLEND_SHA="b4c695f3731ba1cfc575134f41ac795faedbf23ec4cfb58daaeb8bc44b8d8e98"
ORIGINAL_FBX_SHA="f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2"
EXPECTED_NAMES={"Leg_-0.44_-0.975","Mattress","Mattress_Accent_Stripe","Headboard"}
DESIRED_RISE_M=0.00150
DESIRED_EMBED_M=0.00005
report=dict(schema="C01-19/W29/P19-01/REAL-SIGNED-SURGICAL-STRIPE-FBX-REIMPORT-v1",
 asset_id=ID,original_BLEND_SHA256=ORIGINAL_BLEND_SHA,original_FBX_SHA256=ORIGINAL_FBX_SHA,
 correction="Shorten only the existing accent stripe volume from underside, emboss visible top 1.5mm above mattress; 0.05mm hidden structural embed in mattress. NO clipping/normal/weld/model replacement.",
 corrects_c01_02="P1 confirmed mattress-stripe coplanar zfight, real 17 native + imported BVH pairs, original FBX before/hidden stripe shaded A/B Actions run 41724216356",
 status="NOT_RUN",independent_C01_02="NEW_SHA_PRESUMED_PENDING",unity_6000_3_14f1_URP="NOT_RUN_OWNER_ACTION_REQUIRED",
 modified_mesh= "Mattress_Accent_Stripe",modified_mesh_vertex_indices=[],
 door_and_other_model_edits=0,final_approved=False)
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def obj_meshes():
 items={o.name:o for o in bpy.data.objects if o.type=="MESH"}
 assert set(items)==EXPECTED_NAMES,("ORIGINAL NATIVE 4 MESH ID CHANGED",set(items))
 return items
def tri_total(items):return sum(sum(max(0,len(p.vertices)-2) for p in o.data.polygons) for o in items.values())
def uv_snapshot(o):
 out={}
 for layer in o.data.uv_layers:
  out[layer.name]=[tuple(round(float(t),8) for t in v.uv) for v in layer.data]
 return out
def mat_names(o):return [m.name if m else None for m in o.data.materials]
def static_ref(items):
 return {name:dict(vertices=[tuple(v.co) for v in o.data.vertices],
  polygons=[tuple(p.vertices) for p in o.data.polygons],
  polygons_material=[int(p.material_index) for p in o.data.polygons],
  UV0=uv_snapshot(o),materials=mat_names(o),
  parent=o.parent.name if o.parent else None,
  matrix_world=[tuple(float(v) for v in row) for row in o.matrix_world],
  vcount=len(o.data.vertices),polygons_count=len(o.data.polygons))
  for name,o in items.items()}
def bounds(o):
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 return [[min(float(p[i]) for p in pts) for i in range(3)],
         [max(float(p[i]) for p in pts) for i in range(3)]]
def bvh(o):
 o.data.calc_loop_triangles()
 world=[o.matrix_world@v.co for v in o.data.vertices]
 return BVHTree.FromPolygons(world,[list(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def measure(items):
 a=items["Mattress"];b=items["Mattress_Accent_Stripe"]
 ba,bb=bounds(a),bounds(b)
 tops=bb[1][2]-ba[1][2];embed=ba[1][2]-bb[0][2]
 hits=bvh(a).overlap(bvh(b))
 return dict(mattress_world_bounds_m=ba,stripe_world_bounds_m=bb,
  top_delta_stripe_above_mattress_m=tops,
  bottom_stripe_embed_into_mattress_m=embed,
  stripe_thickness_m=bb[1][2]-bb[0][2],
  stripe_mattress_bvh_triangle_intersections=len(hits),
  overlap_pair_indices=hits[:28],
  meshes=len(items),vertices=sum(len(o.data.vertices) for o in items.values()),
  triangle_equivalents=tri_total(items),
  UV0_present=sum(bool(o.data.uv_layers) for o in items.values()),
  all_meshes_closed=all(not e.is_loose for o in items.values() for e in o.data.edges),
  all_finite_coordinates=all(math.isfinite(float(x)) for o in items.values() for v in o.data.vertices for x in v.co))
def render_pair(label,items):
 sc=bpy.context.scene
 original_cam=sc.camera
 old=[(o,o.hide_render) for o in items.values()]
 cdat=bpy.data.cameras.new("W29_P1901_GENUINE_COMPARISON_CAMERA")
 cam=bpy.data.objects.new("W29_P1901_GENUINE_COMPARISON_CAMERA",cdat)
 sc.collection.objects.link(cam)
 target=Vector((0,.60,.61))
 cam.location=target+Vector((1.4,-1.8,1.40))
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 cdat.type="ORTHO";cdat.ortho_scale=1.85
 sc.camera=cam
 sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
 sc.display.shading.show_cavity=True;sc.display.shading.show_shadows=True
 sc.render.resolution_x=1024;sc.render.resolution_y=800;sc.render.resolution_percentage=100
 sc.render.image_settings.file_format="PNG"
 imgs={}
 def take(name):
  p=QA/(label+"_"+name+".png")
  sc.render.filepath=str(p)
  bpy.ops.render.render(write_still=True)
  assert p.stat().st_size>1000 and p.open("rb").read(8)==b"\x89PNG\r\n\x1a\n"
  imgs[name]=dict(file=p.name,sha256=sha(p),bytes=p.stat().st_size)
 try:
  take("SHADED_SAME_CAMERA")
  original_mesh_visibility={o.name:o.hide_render for o in items.values()}
  sc.display.shading.color_type="OBJECT"
  # Render actual indexed FBX edges as geometry instead of using show_wire
  # (view-port only wire toggles often vanish in headless Workbench renders).
  curves=bpy.data.curves.new("W29_REAL_INDEXED_EDGES","CURVE")
  curves.dimensions="3D";curves.resolution_u=1
  curves.bevel_depth=0.0005;curves.bevel_resolution=0
  for o in items.values():
   xyz=[o.matrix_world@v.co for v in o.data.vertices]
   for e in o.data.edges:
    line=curves.splines.new("POLY")
    line.points.add(1)
    for t,ix in enumerate(e.vertices):
     v=xyz[ix];line.points[t].co=(v.x,v.y,v.z,1)
  edges=bpy.data.objects.new("W29_GENUINE_FBX_WORLD_WIRE",curves)
  sc.collection.objects.link(edges)
  for o in items.values():o.hide_render=True
  try:take("TRUE_INDEXED_WIREFRAME_SAME_CAMERA")
  finally:
   for o in items.values():o.hide_render=original_mesh_visibility[o.name]
   bpy.data.objects.remove(edges,do_unlink=True)
   bpy.data.curves.remove(curves,do_unlink=True)
  assert imgs["SHADED_SAME_CAMERA"]["sha256"]!=imgs["TRUE_INDEXED_WIREFRAME_SAME_CAMERA"]["sha256"]
 finally:
  sc.camera=original_cam
  bpy.data.objects.remove(cam,do_unlink=True)
  bpy.data.cameras.remove(cdat,do_unlink=True)
  for o,val in old:o.hide_render=val
 return imgs
try:
 assert bpy.app.version[0]==4,("Genuine Blender4 required",bpy.app.version_string)
 report["blender_version"]=bpy.app.version_string
 assert sha(BLEND)==ORIGINAL_BLEND_SHA and sha(FBX)==ORIGINAL_FBX_SHA,"NATIVE SIGNED EXACT BYTE SHA MISMATCH"
 assert BLEND.open("rb").read(8)==b"BLENDER-"
 assert FBX.open("rb").read(22).startswith(b"Kaydara FBX Binary")
 report["original_binary_sizes_bytes"]=dict(blend=BLEND.stat().st_size,fbx=FBX.stat().st_size)
 # Independent of source Blender: current signed FBX physical import witness.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(FBX))
 imported_old=obj_meshes()
 baseline_fbx=measure(imported_old)
 assert baseline_fbx["meshes"]==4 and baseline_fbx["vertices"]==269 and baseline_fbx["triangle_equivalents"]==470,baseline_fbx
 assert abs(baseline_fbx["top_delta_stripe_above_mattress_m"])<5e-6,baseline_fbx
 assert baseline_fbx["stripe_mattress_bvh_triangle_intersections"]>=15,baseline_fbx
 report["original_reimported_fbx_before"]=baseline_fbx
 report["true_original_fbxscreenshots"]=render_pair("BEFORE_ORIGINAL_SIGNED_FBX",imported_old)
 bpy.ops.wm.open_mainfile(filepath=str(BLEND))
 objs=obj_meshes()
 before=measure(objs)
 source_ref=static_ref(objs)
 assert before["vertices"]==269 and before["triangle_equivalents"]==470
 assert before["UV0_present"]==4 and before["all_finite_coordinates"]
 assert abs(before["top_delta_stripe_above_mattress_m"])<5e-6, before
 stripe=objs["Mattress_Accent_Stripe"];mattress=objs["Mattress"]
 assert len(stripe.data.vertices)==8 and len(stripe.data.polygons)==12
 assert len(mattress.data.vertices)==8 and len(mattress.data.polygons)==12
 assert stripe.parent and stripe.parent.name=="P19-01_ROOT"
 mattress_top=bounds(mattress)[1][2]
 original_limits=bounds(stripe)
 smin,smax=original_limits[0][2],original_limits[1][2]
 assert 0.0095<smax-smin<0.0105,(smin,smax)
 # fail closed unless all 8 original stripe vertices belong to exactly top/bottom.
 coords=[]
 for v in stripe.data.vertices:
  world=stripe.matrix_world@v.co
  if abs(world.z-smin)<1e-5:selector="bottom"
  elif abs(world.z-smax)<1e-5:selector="top"
  else:raise RuntimeError(("NOT_TWO_PLANE_STRIPE",v.index,tuple(world)))
  coords.append((v.index,selector,world))
 assert sum(s=="top" for _,s,_ in coords)==4 and sum(s=="bottom" for _,s,_ in coords)==4
 report["original_source_blend_before"]=before
 report["unchanged_pivot_matrix_and_hierarchy_pre_edit"]=True
 report["original_stripe_world_z_planes_m"]={"bottom":smin,"top":smax}
 for ix,sel,w in coords:
  target= mattress_top+(DESIRED_RISE_M if sel=="top" else -DESIRED_EMBED_M)
  adjusted=w.copy();adjusted.z=target
  local=stripe.matrix_world.inverted_safe()@adjusted
  assert abs((stripe.matrix_world@local).z-target)<1e-7
  stripe.data.vertices[ix].co=local
  report["modified_mesh_vertex_indices"].append(ix)
 stripe.data.update()
 after=measure(objs)
 assert after["meshes"]==4 and after["vertices"]==269 and after["triangle_equivalents"]==470
 assert after["UV0_present"]==4 and after["all_finite_coordinates"]
 assert 0.0014<after["top_delta_stripe_above_mattress_m"]<0.0016,after
 assert 0.00003<after["bottom_stripe_embed_into_mattress_m"]<0.00008,after
 assert 0.0014<after["stripe_thickness_m"]<0.0017
 assert sorted(report["modified_mesh_vertex_indices"])==list(range(8))
 after_ref=static_ref(objs)
 # All original mesh coordinates/polygons/UV/material/hierarchy stay bitwise unchanged
 # except the targeted 8 stripe vertex Z planes (XY conserved).
 for name in EXPECTED_NAMES:
  x,y=source_ref[name],after_ref[name]
  for key in ("polygons","polygons_material","UV0","materials","parent","matrix_world","vcount","polygons_count"):
   assert x[key]==y[key],("UNAUTHORIZED_MESH_OR_MATERIAL_DRIFT",name,key)
  if name!="Mattress_Accent_Stripe":
   assert x["vertices"]==y["vertices"],("NON_TARGET_VERTEX_CHANGED",name)
  else:
   for original,new in zip(x["vertices"],y["vertices"]):
    assert original[:2]==new[:2],("STRIPE_XY_MOVED",original,new)
 # Preserve all original face triangle winding and never introduce degeneracy.
 for o in objs.values():
  assert all(p.area>1e-10 for p in o.data.polygons),(o.name,"DEGENERATE_TRIANGLE")
  assert all(len(p.vertices)==3 for p in o.data.polygons),(o.name,"NON_TRIANGLE")
 report["producer_source_blend_after"]=after
 report["source_before_after_invariants"]=dict(original_meshes=4,original_vertices=269,original_triangles=470,
   unchanged_other_three_mesh_vertex_arrays=True,unchanged_every_face_index_winding=True,
   unchanged_uv0_every_corner=True,unchanged_material_names_and_faces=True,
   unchanged_all_parent_pivots_world_object_matrices=True,original_stripe_XY_unchanged=True,
   intentional_existing_stripe_vertex_z_adjustment_only=True)
 report["repaired_blend_screenshots"]=render_pair("AFTER_REPAIRED_NATIVE_BLEND",objs)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=False)
 assert BLEND.open("rb").read(8)==b"BLENDER-"
 bpy.ops.object.select_all(action="DESELECT")
 for o in bpy.context.scene.objects:
  if o.type in {"MESH","EMPTY"}:o.select_set(True)
 bpy.context.view_layer.objects.active=stripe
 bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,axis_forward="-Z",axis_up="Y",
  apply_unit_scale=True,global_scale=1,bake_anim=False,add_leaf_bones=False,object_types={"MESH","EMPTY"})
 assert FBX.open("rb").read(22).startswith(b"Kaydara FBX Binary")
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(FBX))
 fbxs=obj_meshes()
 imported=measure(fbxs)
 assert imported["meshes"]==4 and imported["vertices"]==269 and imported["triangle_equivalents"]==470
 assert imported["UV0_present"]==4 and imported["all_finite_coordinates"]
 assert 0.0013<imported["top_delta_stripe_above_mattress_m"]<0.0017,imported
 assert 0.000025<imported["bottom_stripe_embed_into_mattress_m"]<0.00009,imported
 assert 0.0013<imported["stripe_thickness_m"]<0.0018,imported
 # Genuine FBX vs authored source bbox match under 100µm tolerance.
 err=max(abs(a-b) for name in EXPECTED_NAMES for ia,ib in zip(bounds(objs[name]) if False else [after["mattress_world_bounds_m"][0],after["mattress_world_bounds_m"][1]] if name=="Mattress" else [after["stripe_world_bounds_m"][0],after["stripe_world_bounds_m"][1]] if name=="Mattress_Accent_Stripe" else bounds(fbxs[name]),bounds(fbxs[name])) for a,b in zip(ia,ib))
 assert err<1e-4,err
 for o in fbxs.values():
  assert all(p.area>1e-10 for p in o.data.polygons),("FBX_ZERO_AREA",o.name)
  assert all(len(p.vertices)==3 for p in o.data.polygons),(o.name,"FBX_TRIANGLES")
 report["new_signed_blend_SHA256"]=sha(BLEND)
 report["new_signed_fbx_SHA256"]=sha(FBX)
 assert report["new_signed_blend_SHA256"]!=ORIGINAL_BLEND_SHA and report["new_signed_fbx_SHA256"]!=ORIGINAL_FBX_SHA
 report["new_native_sizes_bytes"]={"blend":BLEND.stat().st_size,"fbx":FBX.stat().st_size}
 report["actual_new_fbx_reimport"]=imported
 report["actual_new_fbx_screenshots"]=render_pair("AFTER_SIGNED_FBXSHA_REIMPORT",fbxs)
 allimgs=[i for k in ("true_original_fbxscreenshots","repaired_blend_screenshots","actual_new_fbx_screenshots") for i in report[k].values()]
 assert len(allimgs)==6
 assert all(i["bytes"]>1000 and (QA/i["file"]).open("rb").read(8)==b"\x89PNG\r\n\x1a\n" for i in allimgs)
 assert report["true_original_fbxscreenshots"]["SHADED_SAME_CAMERA"]["sha256"]!=report["actual_new_fbx_screenshots"]["SHADED_SAME_CAMERA"]["sha256"],"BEFORE_AFTER_VISUAL_IDENTICAL"
 assert imported["stripe_mattress_bvh_triangle_intersections"]<=baseline_fbx["stripe_mattress_bvh_triangle_intersections"],("CONTACT_REGRESSION",imported,baseline_fbx)
 # Original 17 BVH hits must reduce; residual attachment-contact side triangles
 # can be intentional 0.05mm embed, which independent C01-02 must classify.
 report["new_native_closed_mesh_QA"]="PASS_PHYSICAL_BLENDER_4_SAVE_FBX_EXPORT_REIMPORT_SIGNED"
 report["status"]="PRODUCER_REAL_NATIVE_REPAIR_PASS__INDEPENDENT_C01_02_NEW_SHA_REQUIRED"
 print("W29_P19_01_NATIVE_STRIPE_FIX_PASS",report["new_signed_blend_SHA256"],report["new_signed_fbx_SHA256"],
  "oldHits",baseline_fbx["stripe_mattress_bvh_triangle_intersections"],"newHits",imported["stripe_mattress_bvh_triangle_intersections"],flush=True)
except Exception as e:
 report["status"]="PRODUCER_QA_FAIL_NO_GITHUB_COMMIT"
 report["error"]=repr(e)
 report["traceback"]=traceback.format_exc(limit=7)
 print("W29_P19_01_NATIVE_STRIPE_FIX_FAIL",repr(e),flush=True)
finally:
 (QA/"W29_P19_01_ACTUAL_BLENDER_FBX_REPAIR.json").write_text(json.dumps(report,indent=2)+"\n")
if report["status"]!="PRODUCER_REAL_NATIVE_REPAIR_PASS__INDEPENDENT_C01_02_NEW_SHA_REQUIRED":
 sys.exit(1)
