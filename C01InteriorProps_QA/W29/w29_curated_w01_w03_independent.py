#!/usr/bin/env python3
"""C01-02 W29: independent exact CURRENT CURATED W01/W02/W03 real BLEND+FBX QA.
No W04/delegated doors, gates, prefab or ship import, no production model writes.
"""
import bpy,pathlib,json,hashlib,sys,math,traceback,importlib.util
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
SRC=ROOT/"producer_walls"/"Assets/C01Architecture/Walls_W01_W04"
OUT=ROOT/"C01InteriorProps_QA"/"W29"/"curated_walls_results"
OUT.mkdir(parents=True,exist_ok=True)
WALLS={
"W01":("W01_FULL_WALL_1M","80a8999cc0a039eb4f5f907c38c492ec4c4ed49c22a66d44f36fbe14cb1356b2","4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f"),
"W02":("W02_PANEL_WALL_1M","ba135eac38faa8d76f70282b8c1613013b64450a9e4f7b72368ade3df8ae4372","7dfcf0fe84952e607a74845ad193acfbb9f4fc029e7f168a94a7bac2edacb78b"),
"W03":("W03_CORNER_90_1M","77e1a52db293d4fc6b27b27e151c89865eb4473465bfeafefcc85935b810f9cc","4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c")
}
def exact(path,expected,magic):
 b=path.read_bytes();actual=hashlib.sha256(b).hexdigest()
 if actual!=expected or not b.startswith(magic):raise RuntimeError("native exact SHA/header check FAIL: "+str(path)+" "+actual)
 return {"sha256":actual,"bytes":len(b)}
def objects():return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def snapshot():
 objs=objects();vertexCount=triangleCount=uvMissing=uvCollapsed=degenerate=0
 normal_bad=0
 lo=[float("inf")]*3;hi=[-float("inf")]*3;parts=[]
 for o in objs:
  me=o.data;me.calc_loop_triangles()
  vertexCount+=len(me.vertices)
  triangleCount+=len(me.loop_triangles)
  uv=me.uv_layers.active
  uvMissing+=int(uv is None)
  for v in me.vertices:
   xyz=o.matrix_world@v.co
   for a in range(3):lo[a]=min(lo[a],xyz[a]);hi[a]=max(hi[a],xyz[a])
  for tri in me.loop_triangles:
   pts=[o.matrix_world@me.vertices[i].co for i in tri.vertices]
   area=(pts[1]-pts[0]).cross(pts[2]-pts[0]).length*.5
   if area<1e-13:degenerate+=1
   if uv is not None:
    a,b,c=[uv.data[i].uv for i in tri.loops]
    uva=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5
    if area>1e-11 and uva<1e-13:uvCollapsed+=1
   if not all(math.isfinite(float(v)) for p in pts for v in p):normal_bad+=1
  parts.append({"name":o.name,"verts":len(me.vertices),"triangles":len(me.loop_triangles),
       "uv0":uv is not None,"materials":[x.name if x else None for x in me.materials],
       "pivot_world":[float(x) for x in o.matrix_world.translation]})
 return {"meshes":len(objs),"vertices":vertexCount,"triangles":triangleCount,"uv0_missing_meshes":uvMissing,
 "collapsed_positive3d_uv0_triangles":uvCollapsed,"degenerate_world_triangles":degenerate,
 "nonfinite_position_count":normal_bad,"bounds_min":lo,"bounds_max":hi,"parts":parts}
def screenshots(id):
 scene=bpy.context.scene
 meshes=objects()
 pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 mn=Vector([min(x[i] for x in pts) for i in range(3)]);mx=Vector([max(x[i] for x in pts) for i in range(3)])
 center=(mn+mx)*.5;size=max(mx-mn)
 camdata=bpy.data.cameras.new("C01_02_W29_TEMP_QA_CAMERA")
 cam=bpy.data.objects.new("C01_02_W29_TEMP_QA_CAMERA",camdata);scene.collection.objects.link(cam)
 camdata.type="ORTHO"
 cam.location=center+Vector((1.2,-1.5,1.0))*max(size,.3)
 cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
 bpy.context.view_layer.update()
 inverse=cam.matrix_world.inverted()
 projected=[inverse@p for p in pts]
 width=max(p.x for p in projected)-min(p.x for p in projected)
 height=max(p.y for p in projected)-min(p.y for p in projected)
 camdata.ortho_scale=max(.10,width,height*16/9)*1.25
 scene.camera=cam
 scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
 scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
 scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG"
 def shot(label):
  p=OUT/f"{id}_CURRENT_CURATED_FBX_{label}_1920x1080.png"
  scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  raw=p.read_bytes()
  if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw)<1000:raise RuntimeError("real PNG missing")
  return {"name":p.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"resolution":[1920,1080]}
 shot1=shot("SHADED")
 cr=bpy.data.curves.new("W29_ORIGINAL_FBX_REAL_INDEXED_EDGE_WIRE_NOT_ASSET","CURVE")
 cr.dimensions="3D";cr.bevel_depth=max(.00025,size*.0002)
 n=0
 for o in meshes:
  for e in o.data.edges:
   p=o.matrix_world@o.data.vertices[e.vertices[0]].co
   q=o.matrix_world@o.data.vertices[e.vertices[1]].co
   if (p-q).length<1e-12:continue
   line=cr.splines.new("POLY");line.points.add(1)
   line.points[0].co=(*p,1);line.points[1].co=(*q,1);n+=1
 mat=bpy.data.materials.new("W29_TEMP_WIRE_BLACK");mat.diffuse_color=(.005,.005,.005,1);cr.materials.append(mat)
 wire=bpy.data.objects.new("W29_CURRENT_CURATED_WIRE_HELPER_NOT_ASSET",cr);scene.collection.objects.link(wire)
 shot2=shot("TRUE_WIRE")
 if shot1["sha256"]==shot2["sha256"]:raise RuntimeError("No effective independent original edge-wire screenshot")
 return {"shaded":shot1,"true_wire":shot2,"original_indexed_edge_segments":n}
def main():
 if bpy.app.version[0]!=4:raise RuntimeError("Genuine Blender4 required")
 results=[]
 for id,(name,bsha,fsha) in WALLS.items():
  entry={"asset_id":id,"source_owner":"C01-11","producer_PR":22,"independent_C01_02":True,
         "current_curated_fbx_sha256":fsha,"historical_w26_candidate_version_is_different":True,
         "current_curated_static_status":"NOT_RUN","unity":"NOT_RUN","visual_URP":"NOT_RUN",
         "no_asset_modifications":True,"no_frozen_door_or_gate_assets_accessed":True}
  try:
   bfile=SRC/"Blender"/(name+".blend")
   ffile=SRC/"FBX"/(name+".fbx")
   entry["full_blend"]=exact(bfile,bsha,b"BLENDER")
   entry["full_fbx"]=exact(ffile,fsha,b"Kaydara FBX Binary")
   bpy.ops.wm.open_mainfile(filepath=str(bfile))
   entry["actual_source_blend"]=snapshot()
   bpy.ops.wm.read_factory_settings(use_empty=True)
   bpy.ops.import_scene.fbx(filepath=str(ffile))
   entry["actual_signed_imported_fbx"]=snapshot()
   x=entry["actual_source_blend"];y=entry["actual_signed_imported_fbx"]
   if x["meshes"]!=y["meshes"] or x["triangles"]!=y["triangles"]:raise RuntimeError("Source/import object or triangle mismatch")
   if x["degenerate_world_triangles"] or y["degenerate_world_triangles"] or x["nonfinite_position_count"] or y["nonfinite_position_count"]:raise RuntimeError("Real source/import degenerate or nonfinite geometry")
   if x["uv0_missing_meshes"] or y["uv0_missing_meshes"]:raise RuntimeError("Missing UV0 in current curated model")
   delta=max(abs(a-b) for a,b in zip(x["bounds_min"]+x["bounds_max"],y["bounds_min"]+y["bounds_max"]))
   entry["actual_bbox_delta_m"]=delta
   if delta>.0001:raise RuntimeError("Real source/import bounding box mismatch >0.1mm")
   entry["screenshots"]=screenshots(id)
   entry["current_curated_static_status"]="INDEPENDENT_SAME_CURATED_SHA_SOURCE_AND_FBX_BASIC_MESH_GEOMETRY_IMPORT_PASS"
   if x["collapsed_positive3d_uv0_triangles"] or y["collapsed_positive3d_uv0_triangles"]:
    entry["UV0_review"]="ZERO_UV_AREA_TRIANGLES_RECORDED_REVIEW_ONLY_NO_AUTO_REPAIR"
   else: entry["UV0_review"]="BOTH_SOURCE_AND_IMPORT_NO_ZERO_UV0_POSITIVE3D_TRIANGLE"
  except Exception as e:
   entry["current_curated_static_status"]="HOLD_FAILED_OR_UNPROVEN";entry["exception"]=repr(e);entry["traceback"]=traceback.format_exc(limit=3)
  (OUT/f"{id}_W29_CURRENT_CURATED_REAL_BLENDER_FBX_QA.json").write_text(json.dumps(entry,indent=2)+"\n")
  results.append({"id":id,"status":entry["current_curated_static_status"],"sha":fsha,"UV0_review":entry.get("UV0_review"),"error":entry.get("exception")})
  print("W29_C01_02_CURRENT_CURATED_WALL",id,entry["current_curated_static_status"],entry.get("exception",""),flush=True)
 (OUT/"W29_W01_W02_W03_EXACT_CURATED_SOURCE_QA_SUMMARY.json").write_text(json.dumps({"scope":"W01 W02 W03 non-door current curated only","results":results,"no_W04_or_external_door_test":True,"unity":"NOT_RUN","final_release":"HOLD"},indent=2)+"\n")
 if any(x["status"]=="HOLD_FAILED_OR_UNPROVEN" for x in results):sys.exit(1)
main()
