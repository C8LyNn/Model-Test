#!/usr/bin/env python3
"""P19-01 only. C01-02 actual original signed .blend / FBX mattress/stripe contact.
Read only: no asset save/export/Claude doors/Unity claim.
"""
import bpy,sys,math,json,hashlib,pathlib,traceback
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=pathlib.Path(__file__).resolve().parents[2]
MODEL=ROOT/"producer_w1"/"Assets/C01InteriorProps/C01-19/Models/P19-01"
OUT=ROOT/"C01InteriorProps_QA"/"W28"/"p1901-contact-results"
OUT.mkdir(parents=True,exist_ok=True)
BLEND=MODEL/"P19-01.blend";FBX=MODEL/"P19-01.fbx"
SHABLEND="b4c695f3731ba1cfc575134f41ac795faedbf23ec4cfb58daaeb8bc44b8d8e98"
SHAFBX="f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2"
report={"model":"P19-01","unit":"meters","C01-02":"independent physical Blender4 read-only current native",
        "outcome":"HOLD","unity":"NOT_RUN","asset_edits":0,"fbx_reexport":False}
def checkFile(f,oid,magic):
  data=f.read_bytes()
  if hashlib.sha256(data).hexdigest()!=oid or not data.startswith(magic):
    raise RuntimeError("Native SHA/header FAIL "+str(f))
  return {"sha256":oid,"bytes":len(data)}
def bbox(o):
  coords=[o.matrix_world@v.co for v in o.data.vertices]
  return {"min":[min(v[i] for v in coords) for i in range(3)],
          "max":[max(v[i] for v in coords) for i in range(3)]}
def triangles(o):
  o.data.calc_loop_triangles()
  co=[o.matrix_world@v.co for v in o.data.vertices]
  return [tuple(co[i] for i in t.vertices) for t in o.data.loop_triangles]
def bvh(o):
  o.data.calc_loop_triangles()
  return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
              [tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=0.0)
def mat(o):
  return [{"name":m.name if m else "NULL", "color":list(m.diffuse_color) if m else None}
       for m in o.data.materials]
def geometry_state(label):
  a=bpy.data.objects.get("Mattress")
  b=bpy.data.objects.get("Mattress_Accent_Stripe")
  if a is None or b is None or a.type!="MESH" or b.type!="MESH":raise RuntimeError("Required original mattress/stripe meshes missing")
  ba,bb=bbox(a),bbox(b)
  triangles_a=triangles(a);triangles_b=triangles(b)
  ztopsA=[sum(v.z for v in t)/3 for t in triangles_a if (t[1]-t[0]).cross(t[2]-t[0]).normalized().z>.8]
  ztopsB=[sum(v.z for v in t)/3 for t in triangles_b if (t[1]-t[0]).cross(t[2]-t[0]).normalized().z>.8]
  hits=bvh(a).overlap(bvh(b))
  return {"label":label,"mattress":{"bounds_m":ba,"triangles":len(triangles_a),"material":mat(a)},
          "accent_stripe":{"bounds_m":bb,"triangles":len(triangles_b),"material":mat(b)},
          "xy_overlap_bbox_m":[max(0,min(ba["max"][i],bb["max"][i])-max(ba["min"][i],bb["min"][i])) for i in (0,1)],
          "z_overlap_bbox_m":max(0,min(ba["max"][2],bb["max"][2])-max(ba["min"][2],bb["min"][2])),
          "stripe_top_minus_mattress_top_m":bb["max"][2]-ba["max"][2],
          "mattress_upward_triangle_centroid_z":ztopsA[:30],
          "stripe_upward_triangle_centroid_z":ztopsB[:30],
          "exact_triangle_surface_BVH_overlap_count":len(hits),
          "sample_triangle_hit_indices":hits[:18]}
def render_pair():
  scene=bpy.context.scene
  objs=[o for o in bpy.data.objects if o.type=="MESH"]
  target=Vector((0,.60,.61))
  camera_data=bpy.data.cameras.new("P1901_C01_02_DIAGNOSTIC_CAMERA")
  cam=bpy.data.objects.new("P1901_C01_02_DIAGNOSTIC_CAMERA",camera_data)
  scene.collection.objects.link(cam);scene.camera=cam
  camera_data.type="ORTHO";camera_data.ortho_scale=1.85
  cam.location=target+Vector((1.4,-1.8,1.40))
  cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
  scene.render.engine="BLENDER_WORKBENCH"
  scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
  scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
  scene.render.resolution_x=1024;scene.render.resolution_y=800;scene.render.resolution_percentage=100
  scene.render.image_settings.file_format="PNG"
  output={}
  def save(n):
    path=OUT/("P19-01_"+n+".png");scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    data=path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):raise RuntimeError("No real rendered PNG")
    output[n]={"file":path.name,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
  stripe=bpy.data.objects["Mattress_Accent_Stripe"]
  save("ORIGINAL_FBXSHA_SHADED")
  stripe.hide_render=True;save("QA_ONLY_STRIPE_HIDDEN_COMPARISON")
  stripe.hide_render=False
  if output["ORIGINAL_FBXSHA_SHADED"]["sha256"]==output["QA_ONLY_STRIPE_HIDDEN_COMPARISON"]["sha256"]:
    raise RuntimeError("No visible stripe contribution in diagnostic comparison")
  return output
try:
  if bpy.app.version[0]!=4:raise RuntimeError("Blender4 only")
  report["real_blend"]=checkFile(BLEND,SHABLEND,b"BLENDER")
  report["real_fbx"]=checkFile(FBX,SHAFBX,b"Kaydara FBX Binary")
  bpy.ops.wm.open_mainfile(filepath=str(BLEND))
  report["source_actual_native"]=geometry_state("original_authored_BLENDER")
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.ops.import_scene.fbx(filepath=str(FBX))
  report["actual_imported_FBX"]=geometry_state("current_signed_original_FBX")
  report["shaded_ablation"]=render_pair()
  report["outcome"]="ACTUAL_NATIVE_GEOMETRY_AND_VISUAL_CAUSAL_COMPARISON_CAPTURED__OWNER_DEFECT_DECISION_REQUIRED"
except Exception as e:
  report["outcome"]="FAIL_OR_NOT_RUN"
  report["error"]=repr(e);report["traceback"]=traceback.format_exc(limit=5)
finally:
  (OUT/"P19-01_W28_MATTRESS_STRIPE_EXACT_SHA_WITNESS.json").write_text(json.dumps(report,indent=2)+"\n")
print("C01_02_W28_P19_01",report["outcome"],report.get("error",""),flush=True)
if report["outcome"]=="FAIL_OR_NOT_RUN":sys.exit(1)
