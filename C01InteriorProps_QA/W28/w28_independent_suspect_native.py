#!/usr/bin/env python3
"""C01-02 W28 read-only independent 4 unchanged exact-SHA original BLEND/FBX suspects.
Only P17-01 P19-01 P19-07 P19-08. Never tests/extracts Claude ship doors.
Real Blender 4; source and current actual reimported FBX, shaded + native indexed-wire.
Does NOT claim Unity or subjective visual approval.
"""
import bpy, pathlib, json, math, os, hashlib, sys, traceback, importlib.util
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=ROOT/"producers"
OUT=ROOT/"C01InteriorProps_QA"/"W28"/"native-results"
OUT.mkdir(parents=True,exist_ok=True)
ASSETS={
"P19-01":{
"dir":"p19w1","rel":"Assets/C01InteriorProps/C01-19/Models/P19-01/P19-01",
"blend":"b4c695f3731ba1cfc575134f41ac795faedbf23ec4cfb58daaeb8bc44b8d8e98",
"fbx":"f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2",
"mesh":4,"tri":470,"uv_old":1},
"P19-07":{
"dir":"p19w2","rel":"Assets/C01InteriorProps/C01-19-W02/Models/P19-07/P19-07",
"blend":"a6dc5d3287dc1b4842de35f6a3e1c8e7c885fd8c161016c11243ed2c760dbc28",
"fbx":"eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81",
"mesh":6,"tri":252,"uv_old":8},
"P19-08":{
"dir":"p19w2","rel":"Assets/C01InteriorProps/C01-19-W02/Models/P19-08/P19-08",
"blend":"9f878a0c1f9fb28e9b9748801e16a18319da4391dac8062285f80c1f8c5c81c5",
"fbx":"9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c",
"mesh":6,"tri":282,"uv_old":0},
"P17-01":{
"dir":"p17","rel_blend":"C01InteriorProps_Source/Blender/P17-01.blend",
"rel_fbx":"Assets/C01InteriorProps/Models/P17-01.fbx",
"blend":"7e7fb3911d7f0d061dfa202804a42b18ef0d99510f95e6cc1b6b42d0c53c17eb",
"fbx":"cd6a5787bb7b4c088f0af35382385e4274c85c415c60467f9a22e46fe33ef02c",
"mesh":25,"tri":380,"uv_old":0}
}
def verified(path,oid,magic):
  if not path.is_file(): raise RuntimeError("Real native file not hydrated: "+str(path))
  x=path.read_bytes()
  have=hashlib.sha256(x).hexdigest()
  if have!=oid or not x.startswith(magic):raise RuntimeError("Fail-closed exact SHA/header: "+str(path)+" : "+have)
  return {"sha256":have,"bytes":len(x)}
def mesh_list():
  return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def data_snapshot():
  objs=mesh_list()
  verts=0;tri=0;ngon=0;brokenuv=0;images=0; image_materials=[];bounds_min=[float("inf")]*3;bounds_max=[-float("inf")]*3
  per_part={}
  for obj in objs:
    me=obj.data;me.calc_loop_triangles()
    for v in me.vertices:
      xyz=obj.matrix_world@v.co
      for k in range(3):bounds_min[k]=min(bounds_min[k],xyz[k]);bounds_max[k]=max(bounds_max[k],xyz[k])
    tc=len(me.loop_triangles)
    tri+=tc;verts+=len(me.vertices)
    ngon+=sum(len(p.vertices)>4 for p in me.polygons)
    brokenuv+=int(not me.uv_layers.active)
    for mat in me.materials:
      if mat and mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
          if node.bl_idname=="ShaderNodeTexImage":
            images+=1;image_materials.append({"object":obj.name,"material":mat.name,"texture_node":node.name})
    per_part[obj.name]={"vertices":len(me.vertices),"triangles":tc,
                       "uv0":me.uv_layers.active is not None,
                       "materials":[m.name if m else "NULL" for m in me.materials]}
  return {"meshes":len(objs),"vertices":verts,"triangles":tri,"n_gons":ngon,
          "missing_uv0_meshes":brokenuv,"image_texture_nodes":images,
          "image_texture_materials":image_materials,"bounds_min":bounds_min,"bounds_max":bounds_max,
          "part_names":sorted(per_part),"parts":per_part}
def render(asset):
  scene=bpy.context.scene
  objs=mesh_list()
  mins=[min((o.matrix_world@v.co)[k] for o in objs for v in o.data.vertices) for k in range(3)]
  maxs=[max((o.matrix_world@v.co)[k] for o in objs for v in o.data.vertices) for k in range(3)]
  midpoint=Vector([(a+b)*.5 for a,b in zip(mins,maxs)])
  size=max(b-a for a,b in zip(mins,maxs))
  camera_data=bpy.data.cameras.new("W28_C01_02_TEMP_QA_CAMERA")
  cam=bpy.data.objects.new("W28_C01_02_TEMP_QA_CAMERA",camera_data)
  scene.collection.objects.link(cam)
  cam.location=midpoint+Vector((size*1.7,-size*2.0,size*1.4))
  cam.rotation_euler=(midpoint-cam.location).to_track_quat("-Z","Y").to_euler()
  camera_data.type="ORTHO";camera_data.ortho_scale=size*1.8
  scene.camera=cam;scene.render.engine="BLENDER_WORKBENCH"
  scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
  scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
  scene.render.resolution_x=920;scene.render.resolution_y=690
  scene.render.resolution_percentage=100
  scene.render.image_settings.file_format="PNG"
  shots={}
  def shot(name):
    path=OUT/(asset+"_"+name+".png")
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    raw=path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw)<1000:raise RuntimeError("No real Blender PNG "+name)
    shots[name]={"name":path.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
  shot("REAL_FBX_SHADED")
  curves=bpy.data.curves.new("W28_C01_02_ORIGINAL_INDEXED_EDGE_CURVES","CURVE")
  curves.dimensions="3D";curves.resolution_u=1;curves.bevel_depth=.0008;curves.bevel_resolution=0
  mat=bpy.data.materials.new("W28_C01_02_TEMP_BLACK_WIRE");mat.diffuse_color=(0.008,0.008,0.008,1)
  count=0
  for obj in objs:
    for edge in obj.data.edges:
      p=obj.matrix_world@obj.data.vertices[edge.vertices[0]].co
      q=obj.matrix_world@obj.data.vertices[edge.vertices[1]].co
      if (p-q).length<1e-10:continue
      seg=curves.splines.new("POLY");seg.points.add(1)
      seg.points[0].co=(*p,1);seg.points[1].co=(*q,1);count+=1
  wire=bpy.data.objects.new("W28_C01_02_TEMP_TRUE_WIRE_OBJECT",curves)
  scene.collection.objects.link(wire);curves.materials.append(mat)
  shot("REAL_FBX_ORIGINAL_EDGE_WIRE")
  if shots["REAL_FBX_SHADED"]["sha256"]==shots["REAL_FBX_ORIGINAL_EDGE_WIRE"]["sha256"]:
    raise RuntimeError("Wire and shaded same pixels; this is not authentic edge evidence")
  return {"indexed_edges_rendered":count,"screenshots":shots}
def run(asset,spec,parser):
  rel=spec["rel"] if "rel" in spec else ""
  b=BASE/spec["dir"]/(spec.get("rel_blend",rel+".blend"))
  f=BASE/spec["dir"]/(spec.get("rel_fbx",rel+".fbx"))
  report={"asset_id":asset,"role":"C01-02","mode":"W28_INDEPENDENT_REAL_NATIVE_READ_ONLY",
          "sha_match":False,"status":"HOLD","unity":"NOT_RUN","visual_subjective":"PENDING_HUMAN_OR_UNITY_VIEW",
          "no_native_model_edits":True,"previous_original_fbx_zero_uv_polygons":spec["uv_old"]}
  try:
    report["original_blend"]=verified(b,spec["blend"],b"BLENDER")
    report["original_fbx"]=verified(f,spec["fbx"],b"Kaydara FBX Binary")
    report["sha_match"]=True
    raw=parser.analyze(f.read_bytes())
    report["original_raw_indexed_fbx_metrics"]={k:v for k,v in raw.items() if k!="parts"}
    if raw["zero_area_UV_polygons_with_positive_3D_area"]!=spec["uv_old"]:
      report["raw_uv_count_difference"]="HOLD_NEEDS_METHOD_RECONCILIATION"
    bpy.ops.wm.open_mainfile(filepath=str(b));src=data_snapshot()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(f));dst=data_snapshot()
    report["actual_source_blend"]=src;report["actual_imported_fbx"]=dst
    if src["meshes"]!=spec["mesh"] or dst["meshes"]!=spec["mesh"]:
      raise RuntimeError("Source/FBX part count unexpected")
    if src["triangles"]!=spec["tri"] or dst["triangles"]!=spec["tri"]:
      raise RuntimeError("Source/FBX triangle count unexpected")
    if src["missing_uv0_meshes"] or dst["missing_uv0_meshes"]:
      raise RuntimeError("Current UV0 absent")
    if set(src["part_names"])!=set(dst["part_names"]):
      raise RuntimeError("Source / FBX part identity mismatch")
    maxdim=max(abs(a-b) for a,b in zip(src["bounds_min"]+src["bounds_max"],dst["bounds_min"]+dst["bounds_max"]))
    if maxdim>.0001: raise RuntimeError(f"Source/import world AABB mismatch {maxdim}")
    report["max_source_to_import_bbox_delta_m"]=maxdim
    report["real_native_render"]=render(asset)
    report["status"]="INDEPENDENT_EXACT_SHA_NATIVE_IMPORT_GEOMETRY_STATIC_PASS__RISK_CLASSIFIED_NO_AUTOMATIC_MESH_REPAIR"
    report["interpretation"]="UV micro collapse / near-edge or small bolt normal dot values are not, by themselves, visible/functional defects; current FBX material/texture nodes measured, final Unity visual remains pending"
  except Exception as e:
    report["status"]="FAIL_OR_INCOMPLETE_HOLD"
    report["error"]=repr(e);report["traceback"]=traceback.format_exc(limit=3)
  (OUT/(asset+"_W28_ORIGINAL_NATIVE_TRIAGE.json")).write_text(json.dumps(report,indent=2)+"\n")
  print("C01_02_W28_SUSPECT",asset,report["status"],report.get("error",""),flush=True)
  return report
def main():
  if bpy.app.version[0]!=4:raise RuntimeError("Blender4 required")
  p=ROOT/"C01InteriorProps_QA/GLOBAL_MESH_W26/W26_FBX_POLYGON_QA.py"
  spec=importlib.util.spec_from_file_location("w26original",p)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  items=[run(k,v,mod) for k,v in ASSETS.items()]
  summary={"source":"real Blender4+FBX importer signed four current native models",
           "models":[{"asset":v["asset_id"],"status":v["status"],"sha":v.get("original_fbx",{}).get("sha256"),"error":v.get("error")} for v in items],
           "no_model_modifications":True,"no_unity_proof":True,"final_release":"HOLD"}
  (OUT/"W28_INDEPENDENT_SUSPECT_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
  if any(x["status"]=="FAIL_OR_INCOMPLETE_HOLD" for x in items):sys.exit(1)
main()
