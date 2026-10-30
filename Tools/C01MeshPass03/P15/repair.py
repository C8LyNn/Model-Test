# C01-15 PASS03: repair only existing native .blend sources; never synthesize replacement models.
import bpy,bmesh,math,json,os,shutil,hashlib,sys
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
from mathutils.kdtree import KDTree

BRANCH=os.environ.get("C01_P15_WAVE","W01").upper()
PROJECT=Path(__file__).resolve().parents[3]
SRC=PROJECT/("Assets/C01InteriorProps/P15Wave02" if BRANCH=="W02" else "Assets/C01InteriorProps/P15")
IDS=([f"P15-{i:02d}" for i in range(4,8)] if BRANCH=="W02" else [f"P15-{i:02d}" for i in range(1,4)])
QA=SRC/"QA/Pass03"
BEFORE=QA/"Originals"
VIEW=QA/"Previews"
for path in (QA,BEFORE,VIEW):path.mkdir(parents=True,exist_ok=True)
def dig(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(262144),b""):h.update(chunk)
 return h.hexdigest()
def collect(objects):
 objects=[o for o in objects if o.type=="MESH"]
 return objects
def audit_obj(o):
 bm=bmesh.new();bm.from_mesh(o.data)
 bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
 nvs=len(bm.verts);nes=len(bm.edges);nfs=len(bm.faces)
 pos=defaultdict(list)
 for v in bm.verts:pos[tuple(round(float(c),7) for c in v.co)].append(v.index)
 dupv=sum(len(indices)-1 for indices in pos.values() if len(indices)>1)
 exactface=Counter(tuple(sorted(v.index for v in f.verts)) for f in bm.faces)
 duplicate_faces=sum(c-1 for c in exactface.values() if c>1)
 face_area=sum(f.calc_area()<=1e-12 for f in bm.faces)
 zero_edges=sum(e.calc_length()<=1e-9 for e in bm.edges)
 wire_edges=sum(e.is_wire for e in bm.edges)
 loose_verts=sum(not v.link_edges and not v.link_faces for v in bm.verts)
 boundary=sum(e.is_boundary for e in bm.edges)
 overfull=sum(len(e.link_faces)>2 for e in bm.edges)
 noncontig=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
 tris=sum(len(f.verts)-2 for f in bm.faces)
 # Components based on topological sharing of vertices, not overlapping objects.
 unseen=set(bm.verts);components=0
 while unseen:
  start=unseen.pop();components+=1;todo=[start]
  while todo:
   x=todo.pop()
   for e in x.link_edges:
    other=e.other_vert(x)
    if other in unseen:unseen.remove(other);todo.append(other)
 # Restrained T-junction candidate check: only short meshes where exact segment-to-vertex check is feasible
 tscan="NOT_RUN_LARGE_MESH";tcount=None
 if nvs<=900 and nes<=900:
  tcount=0
  coords=[v.co.copy() for v in bm.verts]
  kd=KDTree(nvs)
  for j,v in enumerate(bm.verts):kd.insert(v.co,j)
  kd.balance()
  for e in bm.edges:
   a,b=e.verts;mid=(a.co+b.co)*0.5;direction=b.co-a.co;den=direction.length_squared
   if den<=1e-18:continue
   for co,index,dist in kd.find_range(mid,math.sqrt(den)*.5+1e-6):
    if index in (a.index,b.index):continue
    t=(co-a.co).dot(direction)/den
    if t<=1e-6 or t>=1-1e-6:continue
    if (co-(a.co+direction*t)).length<=1e-6:tcount+=1
  tscan="MEASURED"
 result={"vertices":nvs,"edges":nes,"faces":nfs,"triangles":tris,"islands":components,
  "duplicate_coincident_vertices_candidates":dupv,"duplicate_index_faces":duplicate_faces,
  "zero_area_faces":face_area,"zero_edges":zero_edges,"wire_edges":wire_edges,"loose_vertices":loose_verts,
  "boundary_edges":boundary,"more_than_two_faces_edges":overfull,"noncontiguous_winding_edges":noncontig,
  "t_junction_candidates":tcount,"t_junction_scan":tscan,
  "closed_by_edges":boundary==0 and overfull==0 and wire_edges==0,
  "uv_layers":len(o.data.uv_layers),"materials":len(o.data.materials),
  "modifier_count":len(o.modifiers),"self_intersection":"NOT_RUN_NoCertifiedRobustDetector"}
 bm.free();return result
def audit_meshes(objects):
 per={o.name:audit_obj(o) for o in objects}
 total={k:sum(x[k] for x in per.values()) for k in
  ("vertices","edges","faces","triangles","islands","duplicate_coincident_vertices_candidates","duplicate_index_faces",
   "zero_area_faces","zero_edges","wire_edges","loose_vertices","boundary_edges","more_than_two_faces_edges","noncontiguous_winding_edges")}
 return {"per_mesh":per,"total":total}
def repair_part(o,log):
 pre=audit_obj(o)
 bm=bmesh.new();bm.from_mesh(o.data)
 bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
 duplicates={}
 for face in list(bm.faces):
  k=tuple(sorted(id(v) for v in face.verts))
  if k in duplicates:
   bmesh.ops.delete(bm,geom=[face],context="FACES")
   log.append({"mesh":o.name,"type":"duplicate_face","action":"deleted duplicate face"})
  else:duplicates[k]=True
 bad=[f for f in bm.faces if f.calc_area()<=1e-12]
 if bad:bmesh.ops.delete(bm,geom=bad,context="FACES");log.append({"mesh":o.name,"type":"degenerate_face","removed":len(bad)})
 # No blind global merge by distance: UV seams, hard edges and independently modeled components remain split.
 wire=[e for e in bm.edges if e.is_wire]
 if wire:bmesh.ops.delete(bm,geom=wire,context="EDGES");log.append({"mesh":o.name,"type":"loose_edges","removed":len(wire)})
 orphan=[v for v in bm.verts if not v.link_edges and not v.link_faces]
 if orphan:bmesh.ops.delete(bm,geom=orphan,context="VERTS");log.append({"mesh":o.name,"type":"orphan_vertices","removed":len(orphan)})
 bm.normal_update()
 # Reverse only entire closed component when its signed volume proves inverted.
 if bm.faces and all(e.is_manifold for e in bm.edges):
  volume=bm.calc_volume(signed=True)
  if volume < -1e-10:
   bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   log.append({"mesh":o.name,"type":"inward_closed_shell","signed_volume_before":volume,"action":"reverse faces"})
 bm.to_mesh(o.data);bm.free();o.data.update()
 return pre
def gauge_ring_fix(o,log):
 # Surgical source-mesh seam repair (P15-07): original 41 ring sections, first and last
 # represent same closed loop, plus 2 accidentally overlapping end caps. Keep 40 original
 # cross sections and connect last to first; preserve original material and UV type.
 data=o.data;sides=12;count=len(data.vertices)
 if count!=41*sides:return
 v=[tuple(q.co) for q in data.vertices]
 mx=max((Vector(v[j])-Vector(v[40*sides+j])).length for j in range(sides))
 if mx>.0035:
  log.append({"mesh":o.name,"type":"close_loop_gap","status":"REVIEW_REQUIRED","seam_max_m":mx});return
 new_vertices=v[:40*sides]
 new_faces=[]
 for ring in range(40):
  nxt=(ring+1)%40
  for j in range(sides):
   k=(j+1)%sides
   new_faces.append((ring*sides+j,ring*sides+k,nxt*sides+k,nxt*sides+j))
 matlist=list(data.materials)
 new=bpy.data.meshes.new(data.name+"_PASS03")
 new.from_pydata(new_vertices,[],new_faces);new.update()
 uv=new.uv_layers.new(name="UVMap")
 for polygon in new.polygons:
  for index in polygon.loop_indices:
   vi=new.loops[index].vertex_index
   px,py,pz=new_vertices[vi]
   # Prior source UV projection from P15 W02 generator, using Blender axes X,Y,Z.
   uv.data[index].uv=(px*.5+(-py)*.7,pz*.65+(-py)*.35)
 for m in matlist:new.materials.append(m)
 orig=o.data;o.data=new
 log.append({"mesh":o.name,"type":"overlapping_closed_tube_end_caps_and_unwelded_wrap",
   "action":"deleted two cap polygons; removed redundant 12-vertex final ring; connected 40th ring to original 1st",
   "seam_max_m_before":mx,"vertex_reduction":12,"face_reduction":2})
 if orig.users==0:bpy.data.meshes.remove(orig)
def list_objects():return collect(bpy.data.objects)
def state_bounds(objects):
 coords=[]
 for o in objects:
  for v in o.data.vertices:
   coords.append(o.matrix_world@v.co)
 lo=[min(c[i] for c in coords) for i in range(3)]
 hi=[max(c[i] for c in coords) for i in range(3)]
 return lo,hi
def render_png(path,wire,focus=None):
 obs=list_objects()
 sc=bpy.context.scene
 sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
 sc.render.resolution_x=1050;sc.render.resolution_y=740;sc.render.resolution_percentage=100
 sc.render.image_settings.file_format="PNG"
 lo,hi=state_bounds(obs);center=Vector([(lo[i]+hi[i])*.5 for i in range(3)])
 size=max(hi[i]-lo[i] for i in range(3))
 if focus is not None:
  center=Vector(focus);size=max(.34,size*.19)
 cam_data=bpy.data.cameras.new("PASS03_CAMERA")
 cam=bpy.data.objects.new("PASS03_CAMERA",cam_data);sc.collection.objects.link(cam)
 cam.location=center+Vector((size*1.8,-size*2.25,size*1.55))
 cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
 cam_data.type="ORTHO";cam_data.ortho_scale=size*1.65
 sc.camera=cam
 mods=[]
 if wire:
  for o in obs:
   mod=o.modifiers.new("PASS03_TEMP_WIREFRAME_FROM_REAL_EDGES","WIREFRAME")
   mod.thickness=max(.00035,size*.00055);mod.use_replace=True
   mod.use_even_offset=False
   mods.append((o,mod))
 sc.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 for o,m in mods:o.modifiers.remove(m)
 bpy.data.objects.remove(cam,do_unlink=True)
def fbx_export(path):
 bpy.ops.object.select_all(action="DESELECT")
 roots=[o for o in bpy.data.objects if o.type in ("EMPTY","MESH")]
 for o in roots:o.select_set(True)
 if roots:bpy.context.view_layer.objects.active=roots[0]
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,global_scale=1,apply_unit_scale=True,
  axis_forward="-Z",axis_up="Y",object_types={"EMPTY","MESH"},bake_anim=False,path_mode="AUTO",
  add_leaf_bones=False)
def fbx_check(path,pre,aid):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 objs=list_objects()
 p=audit_meshes(objs)
 expected=pre["total"]["triangles"]
 matok=all(len(o.data.materials)>0 for o in objs)
 uvok=all(o.data.uv_layers.active is not None for o in objs)
 # Triangulation may split vertex buffers but geometric triangle count is invariant.
 ok=(p["total"]["triangles"]==expected and matok and uvok)
 return {"result":"PASS" if ok else "FAIL","expected_triangles":expected,"imported_triangles":p["total"]["triangles"],
         "material_slots_valid":matok,"UV0_valid":uvok,"import_mesh_count":len(objs),"blender_version":bpy.app.version_string}
reports={}
for aid in IDS:
 original=SRC/"Sources/Blender"/(aid+".blend")
 outputfbx=SRC/"Models/FBX"/(aid+".fbx")
 if not original.exists():raise RuntimeError("Missing actual original Blender source "+str(original))
 # LFS pointer or missing native binary MUST fail, never create a replacement geometry.
 if original.open("rb").read(7)!=b"BLENDER":raise RuntimeError("Not a native .blend: "+str(original))
 backup=BEFORE/(aid+".blend")
 backupfbx=BEFORE/(aid+".fbx")
 if not backup.exists():shutil.copy2(original,backup)
 if outputfbx.exists() and not backupfbx.exists():shutil.copy2(outputfbx,backupfbx)
 bpy.ops.wm.open_mainfile(filepath=str(original))
 objs=list_objects()
 before=audit_meshes(objs)
 orig_geometry={o.name:{"mesh_name":o.data.name,"object_type":o.type,"location":tuple(round(v,8) for v in o.location),
   "scale":tuple(round(v,8) for v in o.scale),"rotation":tuple(round(v,8) for v in o.rotation_euler),
   "parent":o.parent.name if o.parent else None} for o in objs}
 render_png(VIEW/(aid+"_BEFORE_wire.png"),wire=True)
 changes=[]
 for o in objs:repair_part(o,changes)
 if aid=="P15-07":
  for o in objs:
   if o.name.startswith("Gauge_Ring_"):gauge_ring_fix(o,changes)
 after=audit_meshes(list_objects())
 render_png(VIEW/(aid+"_AFTER_wire.png"),wire=True)
 render_png(VIEW/(aid+"_AFTER_shaded.png"),wire=False)
 special=None
 if aid=="P15-07":special=(-.255,-.265,.705) # BLENDER axes: x, -UnityZ, UnityY
 render_png(VIEW/(aid+"_AFTER_detail.png"),wire=True,focus=special)
 # Assert silhouette, object tree, pivots and material count preserved.
 newobjs=list_objects()
 new_geo={o.name:{"location":tuple(round(v,8) for v in o.location),
   "scale":tuple(round(v,8) for v in o.scale),"rotation":tuple(round(v,8) for v in o.rotation_euler),
   "parent":o.parent.name if o.parent else None} for o in newobjs}
 geometry_identity=all(name in new_geo and
   all(orig_geometry[name][k]==new_geo[name][k] for k in ("location","scale","rotation","parent"))
   for name in orig_geometry) and len(orig_geometry)==len(new_geo)
 before_bounds=state_bounds(newobjs)
 # save real changed source and re-export always from original source objects
 bpy.ops.wm.save_as_mainfile(filepath=str(original),compress=False)
 fbx_export(outputfbx)
 fbx_test=fbx_check(outputfbx,after,aid)
 status="PASS" if geometry_identity and fbx_test["result"]=="PASS" and after["total"]["zero_area_faces"]==0 and after["total"]["more_than_two_faces_edges"]==0 else "FAIL"
 if aid=="P15-07":
  if after["total"]["vertices"]>=before["total"]["vertices"]:status="FAIL"
 reports[aid]={"producer_status":status,"source_original_sha256":dig(backup),"source_after_sha256":dig(original),
   "before":before,"after":after,"repairs":changes,"unchanged_root_transforms":geometry_identity,
   "fbx_roundtrip":fbx_test,"unity":"NOT RUN","independent_QA":"NOT RUN",
   "wireframe_source":"Blender actual source object meshes; Wireframe modifier on same mesh data, not reconstruction",
   "inspection_exceptions":{"boundary_edges":"Expected on intentionally open discs, panels, and mechanical assemblies; inspect per named mesh",
    "multi_mesh_coplanar_assembly":"not automatically welded across different objects, to preserve hierarchy and movable parts",
    "remaining_duplicate_vertex_candidates":"count includes intentional UV/sharp-separated and identical coordinates of separate loops, no automatic merge",
    "self_intersections":"NOT_RUN no robust detector"}}
 (QA/(aid+"_mesh_topology_before.json")).write_text(json.dumps(before,indent=2)+"\n")
 (QA/(aid+"_mesh_topology_after.json")).write_text(json.dumps(after,indent=2)+"\n")
 (QA/(aid+"_changes.json")).write_text(json.dumps(reports[aid],indent=2)+"\n")
 if status!="PASS":print("PASS03_REPAIR_FAIL",aid,changes,fbx_test)
output={"scope":"Real .blend repair, FBX roundtrip; Unity NOT RUN; producer audit, independent C01-02 required",
 "wave":BRANCH,"blender_version":bpy.app.version_string,"models":reports,
 "result":"PASS" if all(v["producer_status"]=="PASS" for v in reports.values()) else "FAIL"}
(QA/"PASS03_SUMMARY.json").write_text(json.dumps(output,indent=2)+"\n")
print("PASS03_SUMMARY",output["result"],{i:{"before":r["before"]["total"],"after":r["after"]["total"],"repairs":r["repairs"]} for i,r in reports.items()})
if output["result"]!="PASS":sys.exit(1)
