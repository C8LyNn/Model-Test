"""C01-19 / W26 actual native Blender 4.x mesh audit (READ-ONLY producer files).
Explicitly excludes delegated Claude door/gate assets. No weld, remesh, export or save.
Writes reproducible original BLEND vs original FBX measurements and workbench previews.
A candidate does NOT become a confirmed defect without visual/functional classification.
"""
import bpy, bmesh, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
W02=ROOT.name.endswith("-W02")
S={
 "P19-01":("b4c695f3731ba1cfc575134f41ac795faedbf23ec4cfb58daaeb8bc44b8d8e98","f3b9f806f4dcaafe00f24ac22b0805bf06a49d4216cb1339460ed1be9b26a2f2"),
 "P19-02":("ff0448b34e70ab65380889dfc1d46e426d88873684e831775306cfca28e1a99f","b0d68ce917a938b4bdaa32f4b2d48dcab5275c752c141260cabd3d82a5c9374f"),
 "P19-03":("3652b4f738783e3fab0940311d77b5cd9e6435a23ef60c2c7249f209fa4b11cd","1bd730b2382879d7d9c2f3d67c4b9646b8ca036c04de663e53b3019c403af2df"),
 "P19-04":("8690c61df28d2126e6d84cba00326f6d47fa54f6be56edcedcda4c816b283b70","a8ef74e3972e58b8964d8fd17f121b3cb4977c5c98c9b5ad0928630e77258469"),
 "P19-05":("7905086e87660461d46e6d633b16fc655142939ac4cbc0df0c670067da9314b2","d07b4884cfe1de2c48a96dc9407c2eccdfbdbdf703551c71ae195bd3fd8c9d87"),
 "P19-06":("08f0ed1791beb7c4c4e37ffb1dc3016ebeddf0b94e5e63eb491ec934c51ac4bd","61e371d97c7ff5d17dbc8c5673c8edf489df0b8bdb1b4337396f41f8d4f477ea"),
 "P19-07":("a6dc5d3287dc1b4842de35f6a3e1c8e7c885fd8c161016c11243ed2c760dbc28","eb579a85355756c0d803f58ec96fac509e33788d8142390349aebbffdba50e81"),
 "P19-08":("9f878a0c1f9fb28e9b9748801e16a18319da4391dac8062285f80c1f8c5c81c5","9de76d296482e2d302b5b0a14c30692dbdb6adacd90fcd4e022da9ab35ec658c")
}
IDS=[("P19-%02d"%i) for i in (range(5,9) if W02 else range(1,5))]
OUT=ROOT/"QA"/"PASS26";OUT.mkdir(parents=True,exist_ok=True)
assert len(IDS)==4 and all(k in S for k in IDS)
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def round3(v):return [round(float(x),8) for x in v]
def mesh_objects():return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def inspect():
 objs=mesh_objects()
 assert objs,"Native scene contains no mesh"
 data=[];global_positions=[];tj_all=[];totals=dict(meshes=len(objs),verts=0,triangle_equivalents=0,ngons=0,
   boundary_edges=0,nonmanifold_edges=0,loose_edges=0,zero_area_faces=0,
   micro_faces_lt_1e_10_m2=0,missing_uv0_meshes=0,nonfinite_uv_corners=0,duplicated_geometric_faces=0,
   t_junction_candidates=0)
 for o in objs:
  m=o.data
  verts=[o.matrix_world@v.co for v in m.vertices]
  global_positions.extend(verts)
  bm=bmesh.new();bm.from_mesh(m)
  bound=sum(e.is_boundary for e in bm.edges)
  nonm=sum(len(e.link_faces)>2 for e in bm.edges)
  wire=sum(e.is_wire for e in bm.edges)
  zero=sum(f.calc_area()<=1e-14 for f in bm.faces)
  micro=sum(1e-14<f.calc_area()<1e-10 for f in bm.faces)
  polygons=len(m.polygons);tri=sum(max(0,len(f.vertices)-2) for f in m.polygons)
  ngons=sum(len(f.vertices)>4 for f in m.polygons)
  uv0=bool(m.uv_layers)
  baduv=0
  if uv0:
   for x in m.uv_layers.active.data:
    if not (math.isfinite(x.uv[0]) and math.isfinite(x.uv[1])):baduv+=1
  duplicate=0;face_set=set()
  for p in m.polygons:
   signature=tuple(sorted(tuple(round3(verts[j])) for j in p.vertices))
   if signature in face_set:duplicate+=1
   face_set.add(signature)
  tj=[]
  for edge in m.edges:
   a,b=edge.vertices;va,vb=verts[a],verts[b];delta=vb-va;dd=delta.length_squared
   if dd<1e-14:continue
   for i,v in enumerate(verts):
    if i==a or i==b:continue
    t=(v-va).dot(delta)/dd
    if 1e-5<t<1-1e-5:
     dist=(v-va-t*delta).length
     if dist<2e-7:
      tj.append(dict(mesh=o.name,vertex=i,edge=[a,b],fraction=round(float(t),8),
         distance_m=float(dist),world_xyz_m=round3(v)))
  bm.free()
  st=dict(name=o.name,mesh_data_name=m.name,vertices=len(verts),faces=polygons,
   triangle_equivalents=tri,ngons=ngons,boundary_edges=bound,nonmanifold_edges=nonm,
   loose_edges=wire,zero_area_faces=zero,micro_faces=micro,uv0=uv0,
   nonfinite_uv_corners=baduv,duplicate_geometric_faces=duplicate,
   t_junction_count=len(tj),t_junction_candidates=tj[:80],
   material_slot_count=len(o.material_slots),parent=o.parent.name if o.parent else None,
   matrix_world_4x4=[[round(float(x),8) for x in row] for row in o.matrix_world])
  data.append(st);tj_all.extend(tj)
  for key,num in [("verts",len(verts)),("triangle_equivalents",tri),("ngons",ngons),
    ("boundary_edges",bound),("nonmanifold_edges",nonm),("loose_edges",wire),
    ("zero_area_faces",zero),("micro_faces_lt_1e_10_m2",micro),
    ("missing_uv0_meshes",0 if uv0 else 1),("nonfinite_uv_corners",baduv),
    ("duplicated_geometric_faces",duplicate),("t_junction_candidates",len(tj))]:
   totals[key]+=num
 lo=[min(float(p[j]) for p in global_positions) for j in range(3)]
 hi=[max(float(p[j]) for p in global_positions) for j in range(3)]
 return dict(totals=totals,objects=data,world_bounds_min_m=round3(lo),
             world_bounds_max_m=round3(hi),t_junction_candidate_sample=tj_all[:150])
def render(folder,tag,review=None):
 sc=bpy.context.scene
 sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO"
 sc.render.resolution_x=1050;sc.render.resolution_y=780
 sc.render.resolution_percentage=100
 obj=mesh_objects();v=[o.matrix_world@p.co for o in obj for p in o.data.vertices]
 lo=Vector([min(p[i] for p in v) for i in range(3)])
 hi=Vector([max(p[i] for p in v) for i in range(3)])
 middle=(lo+hi)/2;span=max((hi-lo).length,.35)
 saved=sc.camera
 camera_data=bpy.data.cameras.new("C01_W26_QA_CAMERA")
 cam=bpy.data.objects.new("C01_W26_QA_CAMERA",camera_data)
 bpy.context.collection.objects.link(cam)
 cam.location=middle+Vector((span*1.4,-span*1.8,span*1.1))
 cam.rotation_euler=(middle-cam.location).to_track_quat("-Z","Y").to_euler()
 camera_data.type="ORTHO";camera_data.ortho_scale=span*1.75;sc.camera=cam
 prev=[(o,o.show_wire,o.show_all_edges) for o in obj]
 try:
  for wire in (False,True):
   for o in obj:o.show_wire=wire;o.show_all_edges=wire
   fn=tag+("_wireframe.png" if wire else "_shaded.png")
   sc.render.filepath=str(folder/fn);sc.render.image_settings.file_format="PNG"
   bpy.ops.render.render(write_still=True)
   assert (folder/fn).stat().st_size>1000
 finally:
  sc.camera=saved
  bpy.data.objects.remove(cam,do_unlink=True)
  for o,w,e in prev:o.show_wire=w;o.show_all_edges=e
summary=[]
for mid in IDS:
 folder=OUT/mid;folder.mkdir(parents=True,exist_ok=True)
 base=ROOT/"Models"/mid
 blend=base/(mid+".blend");fbx=base/(mid+".fbx")
 assert blend.is_file() and fbx.is_file()
 actual=(sha(blend),sha(fbx));assert actual==S[mid],(mid,"NATIVE SHA MISMATCH",actual,S[mid])
 assert blend.read_bytes()[:8]==b"BLENDER-" and fbx.read_bytes()[:21].startswith(b"Kaydara FBX Binary")
 bpy.ops.wm.open_mainfile(filepath=str(blend))
 source=inspect();render(folder,"source_BLEND")
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(fbx))
 imported=inspect();render(folder,"original_FBX")
 risks=dict(
   actual_nonmanifold_faces=imported["totals"]["nonmanifold_edges"],
   actual_degenerate_source_faces=source["totals"]["zero_area_faces"],
   actual_degenerate_import_faces=imported["totals"]["zero_area_faces"],
   source_uv0_missing=source["totals"]["missing_uv0_meshes"],
   fbx_uv0_missing=imported["totals"]["missing_uv0_meshes"],
   fbx_duplicate_geometric_faces=imported["totals"]["duplicated_geometric_faces"],
   fbx_t_junction_proximity_candidates=imported["totals"]["t_junction_candidates"])
 rec=dict(asset_id=mid,blend_SHA256=actual[0],fbx_SHA256=actual[1],
  blender_version=bpy.app.version_string,sha_matches_signed_LFS=True,
  actual_source_BLEND=source,actual_reimported_FBX=imported,
  risks_require_independent_interpretation=risks,
  source_geometry_changed=False,fbx_export_performed=False,
  independent_c01_02="NOT_RUN_NEW_W26_INDEPENDENT_SIGNOFF",
  Unity_6_URP_Editor="NOT_RUN",
  disposition="INDEPENDENT_VISUAL_CLASSIFICATION_REQUIRED_IF_RISK; NO_AUTOMATIC_GEOMETRY_EDIT",
  screenshots=["source_BLEND_shaded.png","source_BLEND_wireframe.png",
    "original_FBX_shaded.png","original_FBX_wireframe.png"])
 (folder/"REAL_W26_NATIVE_AUDIT.json").write_text(json.dumps(rec,indent=2))
 summary.append(dict(asset_id=mid,blend_sha256=actual[0],fbx_sha256=actual[1],
   source_counts=source["totals"],fbx_counts=imported["totals"],
   independent_qa="PENDING",source_modified=False,unity="NOT_RUN"))
 print("C01_W26_REAL_BLENDER_PASS",mid,actual[1],json.dumps(risks),flush=True)
(OUT/"SUMMARY.json").write_text(json.dumps(dict(
 schema="C01-19/W26/real-native-blend-original-fbx-readonly-qa-v1",
 wave="W02" if W02 else "W01",models=summary,
 claude_door_scope="EXCLUDED",source_modified=False,export_performed=False,
 unity_editor="NOT_RUN",independent_signoff="PENDING"),indent=2))
assert len(summary)==4
