"""W27 C01-19 read-only physically signed FBX UV-area / near-edge visual witness.
Scope solely P19-07 and P19-08. Frozen external doors are not loaded or inspected.
No producer BLEND/FBX save/export. No weld, no decimation, no geometry edits.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent.parent
ROOT=R/"QA"/"PASS27";ROOT.mkdir(parents=True,exist_ok=True)
SHA={
"P19-07":("a6dc5d3287dc1b4842de35f6a3e1c8e7c885fd8c161016c11243ed2c760dbc28","eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81"),
"P19-08":("9f878a0c1f9fb28e9b9748801e16a18319da4391dac8062285f80c1f8c5c81c5","9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c")}
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as file:
  for block in iter(lambda:file.read(1048576),b""):h.update(block)
 return h.hexdigest()
def world_bbox(items):
 v=[o.matrix_world@v.co for o in items for v in o.data.vertices]
 return [[min(float(p[j]) for p in v) for j in range(3)],
         [max(float(p[j]) for p in v) for j in range(3)]]
def area_uv(uv):
 return sum(abs((uv[i][0]-uv[0][0])*(uv[i+1][1]-uv[0][1])-(uv[i][1]-uv[0][1])*(uv[i+1][0]-uv[0][0]))*.5 for i in range(1,len(uv)-1))
def area_3d(points):
 return sum(((points[i]-points[0]).cross(points[i+1]-points[0])).length*.5 for i in range(1,len(points)-1))
def digest_round(v):return [round(float(x),9) for x in v]
def inspect(items):
 result=[];candidate=[];totals=dict(meshes=0,verts=0,triangles=0,zero_uv_area_faces_positive_3d=0,
  zero_uv_3d_area_m2=0.0,tj_near_edge_candidates=0,boundary_edges=0,nonmanifold_edges=0,zero_3d_area_faces=0,
  image_texture_nodes_on_collapsed_materials=0)
 for o in items:
  m=o.data;uvdata=m.uv_layers.active.data if m.uv_layers else None
  world=[o.matrix_world@v.co for v in m.vertices]
  faces=[];near_zero_3d=[];raw_zero_uv=[]
  textured_materials=[]
  for mat in m.materials:
   n=[{"type":n.type,"image":n.image.name if n.image else None} for n in mat.node_tree.nodes if n.type=="TEX_IMAGE"] if mat and mat.use_nodes and mat.node_tree else []
   textured_materials.append({"name":mat.name if mat else None,"uses_nodes":bool(mat and mat.use_nodes),"image_texture_nodes":n})
  for pi,p in enumerate(m.polygons):
   pts=[world[i] for i in p.vertices]
   area=area_3d(pts)
   uv=[tuple(float(q) for q in uvdata[li].uv) for li in p.loop_indices] if uvdata else []
   uva=area_uv(uv) if uv else None
   if area<=1e-14:
    totals["zero_3d_area_faces"]+=1
    near_zero_3d.append(dict(polygon_index=pi,vertices=list(p.vertices),world_area_by_fan_m2=float(area),
      world_vertex_xyz_m=[digest_round(x) for x in pts]))
   if uva is not None and uva<=1e-14:
    raw_zero_uv.append(dict(polygon_index=pi,world_area_m2=float(area),UV_area=float(uva),material_index=p.material_index))
   if uva is not None and uva<=1e-14 and area>1e-14:
    slot=p.material_index;material=textured_materials[slot] if slot<len(textured_materials) else {}
    if material.get("image_texture_nodes"):totals["image_texture_nodes_on_collapsed_materials"]+=1
    faces.append(dict(polygon_index=pi,local_vertex_indices=list(p.vertices),vertices_world_m=[digest_round(x) for x in pts],
      three_d_area_m2=float(area),UV0_area=float(uva),UV0_loop_values=[list(x) for x in uv],
      material_index=slot,material=material,centroid_world_m=digest_round(sum(pts,Vector())/len(pts))))
    totals["zero_uv_area_faces_positive_3d"]+=1;totals["zero_uv_3d_area_m2"]+=float(area)
  bm=bmesh.new();bm.from_mesh(m)
  total_bound=sum(e.is_boundary for e in bm.edges)
  total_nonmanifold=sum(len(e.link_faces)>2 for e in bm.edges)
  bm.free()
  near=[]
  for e in m.edges:
   i,j=e.vertices;a,b=world[i],world[j];delta=b-a;dd=delta.length_squared
   if dd<1e-14:continue
   for k,v in enumerate(world):
    if k in (i,j):continue
    t=(v-a).dot(delta)/dd
    if not 1e-5<t<1-1e-5:continue
    dist=(v-a-t*delta).length
    if dist<2e-7:
     near.append(dict(vertex_index=k,edge_indices=[i,j],distance_m=float(dist),fraction=float(t),
       world_xyz=digest_round(v)))
  totals["meshes"]+=1;totals["verts"]+=len(m.vertices)
  totals["triangles"]+=sum(max(0,len(p.vertices)-2) for p in m.polygons)
  totals["tj_near_edge_candidates"]+=len(near)
  totals["boundary_edges"]+=total_bound;totals["nonmanifold_edges"]+=total_nonmanifold
  result.append(dict(object=o.name,original_mesh_datablock=m.name,uv0=bool(uvdata),materials=textured_materials,
   collapsed_polygons=faces,collapsed_count=len(faces),raw_zero_uv_area_any_3d=raw_zero_uv,raw_zero_uv_count=len(raw_zero_uv),world_area_le_1e_14_witnesses=near_zero_3d,near_edge_contacts=near,
   same_mesh_near_edge_candidates=len(near),boundary_edges=total_bound,nonmanifold_edges=total_nonmanifold))
  candidate.extend([Vector(x["centroid_world_m"]) for x in faces])
  candidate.extend([Vector(x["world_xyz"]) for x in near])
 return dict(totals=totals,objects=result,world_bbox=world_bbox(items),focus_points=[list(x) for x in candidate[:80]])
def workbench(out,items,center,scale,filename,wire=False):
 sc=bpy.context.scene
 sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO";sc.display.shading.color_type="OBJECT"
 sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100
 camera_data=bpy.data.cameras.new("W27_TEMP_CAMERA")
 camera=bpy.data.objects.new("W27_TEMP_CAMERA",camera_data)
 bpy.context.collection.objects.link(camera)
 camera.location=center+Vector((scale*1.2,-scale*1.65,scale*1.15))
 camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
 camera_data.type="ORTHO";camera_data.ortho_scale=scale*1.8
 prevcam=sc.camera;sc.camera=camera
 before=[(o,o.hide_render) for o in items]
 wire_obj=None;edge_curve=None
 try:
  if wire:
   # Genuine world-space *original indexed geometry edges*. Not viewport show_wire,
   # which does not reliably appear in offline workbench renders.
   edge_curve=bpy.data.curves.new("W27_ORIGINAL_INDEXED_FBX_EDGES","CURVE")
   edge_curve.dimensions="3D";edge_curve.resolution_u=1
   edge_curve.bevel_depth=0.00065;edge_curve.bevel_resolution=0
   for mesh in items:
    p=[mesh.matrix_world@v.co for v in mesh.data.vertices]
    for e in mesh.data.edges:
     line=edge_curve.splines.new("POLY")
     line.points.add(1)
     for n,k in enumerate(e.vertices):
      xyz=p[k];line.points[n].co=(xyz[0],xyz[1],xyz[2],1)
   wire_obj=bpy.data.objects.new("W27_REAL_FBX_EDGE_WIREFRAME",edge_curve)
   bpy.context.collection.objects.link(wire_obj)
   wire_obj.color=(0.08,0.08,0.08,1)
   for o in items:o.hide_render=True
  sc.render.filepath=str(out/filename);sc.render.image_settings.file_format="PNG"
  bpy.ops.render.render(write_still=True)
  file=out/filename
  assert file.stat().st_size>1000 and file.open("rb").read(8)==b"\x89PNG\r\n\x1a\n"
 finally:
  sc.camera=prevcam
  for o,state in before:o.hide_render=state
  if wire_obj:bpy.data.objects.remove(wire_obj,do_unlink=True)
  if edge_curve:bpy.data.curves.remove(edge_curve,do_unlink=True)
  bpy.data.objects.remove(camera,do_unlink=True)
  bpy.data.cameras.remove(camera_data,do_unlink=True)
def images(out,items,data,kind):
 lo,hi=[Vector(v) for v in data["world_bbox"]]
 center=(lo+hi)/2;span=max((hi-lo).length,.30)
 focus=[Vector(v) for v in data["focus_points"]]
 localcenter=sum(focus,Vector())/len(focus) if focus else center
 images=[]
 for label,c,s in [("whole",center,span),("suspects",localcenter,.28)]:
  for wire in (False,True):
   filename=kind+"_"+label+("_real_edge_wire.png" if wire else "_shaded.png")
   workbench(out,items,c,s,filename,wire)
   images.append(filename)
 return images
summary=[]
for mid,shas in SHA.items():
 source=R/"Models"/mid/(mid+".blend");fbx=R/"Models"/mid/(mid+".fbx")
 assert (sha(source),sha(fbx))==shas,(mid,"SIGNED_SHA_MISMATCH")
 assert source.open("rb").read(8)==b"BLENDER-"
 assert fbx.open("rb").read(21).startswith(b"Kaydara FBX Binary")
 out=ROOT/mid;out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(source))
 original=[o for o in bpy.context.scene.objects if o.type=="MESH"]
 source_result=inspect(original)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(fbx))
 actual=[o for o in bpy.context.scene.objects if o.type=="MESH"]
 imported=inspect(actual)
 imgs=images(out,actual,imported,"ACTUAL_SIGNED_FBX")
 assert imported["totals"]["meshes"]==6
 assert imported["totals"]["triangles"]==(252 if mid=="P19-07" else 282)
 assert imported["totals"]["tj_near_edge_candidates"]==(17 if mid=="P19-07" else 2)
 assert imported["totals"]["boundary_edges"]==0 and imported["totals"]["nonmanifold_edges"]==0
 # Do not equate a new world-space fan-area threshold flag with a confirmed
 # Blender BMesh or FBX indexed-triangle defect: retain exact witness for C01-02.
 # Independent direct indexed-FBX Newell parser found 8 P19-07 UV-zero polys.
 # This Blender-imported UV/area classifier can legitimately disagree due
 # to importer UV normalization or a different 3D/UV area tolerance; retain
 # the actual per-face raw witnesses and flag reconciliation to C01-02.
 print("W27_IMPORTER_VS_RAW_UV_COUNT",mid,"actual",imported["totals"]["zero_uv_area_faces_positive_3d"],
       "raw_zero_uv",sum(len(o["raw_zero_uv_area_any_3d"]) for o in imported["objects"]),
       "C01_02_previous",8 if mid=="P19-07" else 0,flush=True)
 assert sha(source)==shas[0] and sha(fbx)==shas[1]
 assert sha(out/imgs[0])!=sha(out/imgs[1]),"TRUE WIRE RENDER MUST DIFFER FROM SHADED"
 rec=dict(schema="C01-19-W27-reality-readonly-UV-collapse-near-edge-witness-v1",
   asset=mid,source_blend_SHA256=shas[0],actual_signed_fbx_SHA256=shas[1],
   Blender=bpy.app.version_string,source_blend=source_result,actual_reimported_signed_fbx=imported,
   previews=imgs,blender_producer_native_changed=False,fbx_exported=False,
   world_fan_area_threshold_note="W26 BMesh found 0 zero-area; W27 world-fan-area and UV classifier may use different numerical/importer rules from C01-02 direct FBX polygon audit; preserve actual per-face raw data for independent reconciliation, no automatic geometry edit",c01_02_independent_visual_conclusion="PENDING",
   Unity="NOT_RUN",conclusion="OBSERVED_NUMERICAL_CANDIDATES_ONLY__VISUAL_AND_MATERIAL_IMPACT_REQUIRES_INDEPENDENT_ACCEPTANCE")
 (out/"W27_TARGETED_REAL_NATIVE_UV_AND_EDGE_WITNESS.json").write_text(json.dumps(rec,indent=2))
 summary.append(dict(asset=mid,blend_sha=shas[0],fbx_sha=shas[1],
  original_blend_uv_faces=source_result["totals"]["zero_uv_area_faces_positive_3d"],
  signed_fbx_uv_faces=imported["totals"]["zero_uv_area_faces_positive_3d"],
  signed_fbx_uv_3d_surface_m2=imported["totals"]["zero_uv_3d_area_m2"],
  image_textures_on_collapsed_faces=imported["totals"]["image_texture_nodes_on_collapsed_materials"],
  raw_zero_uv_area_polygons_any_3d=sum(len(o["raw_zero_uv_area_any_3d"]) for o in imported["objects"]),
  previous_c01_02_direct_fbx_zero_uv_polygons=(8 if mid=="P19-07" else 0),
  tj_candidates=imported["totals"]["tj_near_edge_candidates"],
  previews=imgs,source_changed=False,unity="NOT_RUN"))
 print("C01_W27_UV_EDGE_NATIVE_SUCCESS",mid,json.dumps(summary[-1]),flush=True)
(ROOT/"W27_SUMMARY.json").write_text(json.dumps(dict(scope="2 existing non-door P19 assets",models=summary,
 real_blender=True,full_SHA_verified=True,geometry_edits=0,exports=0,
 c01_02_independent="PENDING",unity6="NOT_RUN"),indent=2))
