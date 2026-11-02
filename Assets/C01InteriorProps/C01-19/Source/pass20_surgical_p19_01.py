"""C01-19 W20: surgical REAL Blender edge flips for two C01-02-confirmed P19-01 micro-slivers.
NO vertex movement, NO welding, NO new models, fail closed at all gates.
Original native BLEND/FBX must match previous physically hydrated Git LFS OIDs.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
MID="P19-01";MP=ROOT/"Models"/MID
SRC=MP/(MID+".blend");FBX=MP/(MID+".fbx")
QA=ROOT/"QA"/"PASS20"/MID;QA.mkdir(parents=True,exist_ok=True)
EXPECTED_BLEND="a8883117ec9e59b93cb988970c09d6cdaf496b8a73957a60aa3ca503f8be420f"
EXPECTED_FBX="e2e0bb9e095c1daed87e407814e88f8788cf503ab705d3e34513879038bcd559"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==EXPECTED_BLEND,("source drift",sha(SRC))
assert sha(FBX)==EXPECTED_FBX,("FBX drift",sha(FBX))
assert SRC.read_bytes().startswith(b"BLENDER-v400")
assert FBX.read_bytes().startswith(b"Kaydara FBX Binary  \x00\x1a\x00")
bpy.ops.wm.open_mainfile(filepath=str(SRC))
objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert len(objects)==4
target=[o for o in objects if o.data.name=="Cube.001"]
assert len(target)==1,[o.data.name for o in objects]
o=target[0];m=o.data
assert len(m.vertices)==245 and len(m.polygons)==434
assert all(len(f.vertices)==3 for o2 in objects for f in o2.data.polygons)
before_pos=[tuple(v.co) for v in m.vertices]
before_shapes={ob.name:(ob.parent.name if ob.parent else "",tuple(ob.location),tuple(ob.rotation_euler),tuple(ob.scale),len(ob.data.vertices),len(ob.data.polygons)) for ob in objects}
def bounds():
 xyz=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices]
 return [[min(p[j] for p in xyz) for j in range(3)],[max(p[j] for p in xyz) for j in range(3)]]
original_bounds=bounds()
def area(f):return f.calc_area()
def smallfaces(mesh,threshold=1e-10):
 return [{"indices":[v.index for v in f.verts],"area_m2":area(f)} for f in mesh.faces if area(f)<threshold]
def render(file,wire):
 sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH'
 sc.render.resolution_x=950;sc.render.resolution_y=740;sc.render.resolution_percentage=100
 oldcam=sc.camera
 original_type=sc.display.shading.type
 old_flags=[(ob,ob.show_wire,ob.show_all_edges) for ob in objects]
 for ob in objects:ob.show_wire=wire;ob.show_all_edges=wire
 sc.display.shading.type="WIREFRAME" if wire else "SOLID"
 xyz=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices]
 lo=Vector([min(v[i] for v in xyz) for i in range(3)])
 hi=Vector([max(v[i] for v in xyz) for i in range(3)])
 mid=(lo+hi)*.5;span=max((hi-lo).length,.5)
 camdat=bpy.data.cameras.new('PASS20_TEMP_CAMERA')
 cam=bpy.data.objects.new('PASS20_TEMP_CAMERA',camdat)
 bpy.context.collection.objects.link(cam)
 cam.location=mid+Vector((span*1.5,-span*1.8,span*1.25))
 cam.rotation_euler=(mid-cam.location).to_track_quat('-Z','Y').to_euler()
 camdat.type='ORTHO';camdat.ortho_scale=span*1.8;sc.camera=cam
 sc.render.filepath=str(QA/file);sc.render.image_settings.file_format='PNG'
 try:bpy.ops.render.render(write_still=True)
 finally:
  sc.camera=oldcam;sc.display.shading.type=original_type
  bpy.data.objects.remove(cam,do_unlink=True)
  for ob,w,a in old_flags:ob.show_wire=w;ob.show_all_edges=a
render("BEFORE_REAL_BLENDER_SHADED.png",False)
render("BEFORE_REAL_BLENDER_WIREFRAME.png",True)
bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table();bm.verts.index_update()
tiny_before=smallfaces(bm)
print("NATIVE_LOW_AREA",sorted([{"indices":[v.index for v in f.verts],"area_m2":f.calc_area()} for f in bm.faces],key=lambda v:v["area_m2"])[:12],flush=True)
print("NATIVE_FACE_MATCHES",[(needle,[(f.index,f.calc_area()) for f in bm.faces if {v.index for v in f.verts}==set(needle)]) for needle in [[3,106,107],[88,87,13]]],flush=True)
assert all(set(x["indices"]) in ({3,106,107},{88,87,13}) for x in tiny_before),tiny_before
flips=[{"small":[3,106,107],"old_edge":[3,107],"new_edge":[106,32]},
       {"small":[88,87,13],"old_edge":[87,13],"new_edge":[88,47]}]
patch_records=[]
for entry in flips:
 bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.verts.index_update()
 ia,ib=entry["old_edge"]
 edge=next((e for e in bm.edges if {v.index for v in e.verts}=={ia,ib}),None)
 assert edge is not None and len(edge.link_faces)==2,("edge not exactly 2-sided",entry)
 faces=list(edge.link_faces)
 assert any({v.index for v in f.verts}==set(entry["small"]) for f in faces),("wrong patch",entry)
 assert len({f.material_index for f in faces})==1,("material seam",entry)
 assert len({f.smooth for f in faces})==1,("shading seam",entry)
 assert all(len(f.verts)==3 for f in faces)
 oldvol=sum(f.calc_area() for f in faces)
 oldnormal=[f.normal.copy() for f in faces]
 assert oldnormal[0].dot(oldnormal[1])>.999999,("not coplanar",entry)
 corner_ids=set(v.index for f in faces for v in f.verts)
 assert len(corner_ids)==4,("not a quad patch",entry,corner_ids)
 # Capture and enforce exact per-vertex UV0 values across the full patch.
 uvmap={}
 for layer in bm.loops.layers.uv.values():
  vals={}
  for face in faces:
   for loop in face.loops:
    ix=loop.vert.index;co=tuple(float(y) for y in loop[layer].uv)
    if ix in vals:assert max(abs(a-b) for a,b in zip(vals[ix],co))<1e-6,("UV seam",entry,ix)
    vals[ix]=co
  assert set(vals)==corner_ids
  uvmap[layer]=vals
 result=bmesh.ops.rotate_edges(bm,edges=[edge],use_ccw=False)
 bm.faces.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.verts.index_update();bm.normal_update()
 newedge=next((e for e in bm.edges if {v.index for v in e.verts}==set(entry["new_edge"])),None)
 assert newedge is not None and len(newedge.link_faces)==2,("wrong new edge",entry)
 nfaces=list(newedge.link_faces)
 assert {v.index for f in nfaces for v in f.verts}==corner_ids
 newvol=sum(f.calc_area() for f in nfaces)
 assert abs(newvol-oldvol)<1e-7,("patch area drift",entry,oldvol,newvol)
 assert min(f.calc_area() for f in nfaces)>1e-7,("still sliver",entry)
 assert all(f.normal.dot(oldnormal[0])>.999999 for f in nfaces),("winding changed",entry)
 assert all(f.material_index==faces[0].material_index for f in nfaces) if faces[0].is_valid else True
 for layer,vals in uvmap.items():
  for f in nfaces:
   for loop in f.loops:loop[layer].uv=vals[loop.vert.index]
 for layer,vals in uvmap.items():
  for f in nfaces:
   for loop in f.loops:
    assert max(abs(a-b) for a,b in zip(vals[loop.vert.index],loop[layer].uv))<1e-6
 patch_records.append({"old_diagonal":entry["old_edge"],"new_diagonal":entry["new_edge"],
   "old_triangle_m2":[float(f.calc_area()) for f in nfaces],"new_min_triangle_area_m2":min(f.calc_area() for f in nfaces),
   "old_patch_area_m2":oldvol,"new_patch_area_m2":newvol,"uv0_explicitly_restored":True})
small_after=smallfaces(bm)
assert len(small_after)==0,small_after
assert all(e.is_manifold for e in bm.edges)
bm.normal_update();bm.to_mesh(m);bm.free();m.update()
assert len(m.vertices)==245 and len(m.polygons)==434
assert [tuple(v.co) for v in m.vertices]==before_pos
assert before_shapes=={ob.name:(ob.parent.name if ob.parent else "",tuple(ob.location),tuple(ob.rotation_euler),tuple(ob.scale),len(ob.data.vertices),len(ob.data.polygons)) for ob in objects}
assert max(abs(a-b) for i in range(2) for a,b in zip(original_bounds[i],bounds()[i]))<1e-6
assert sum(len(ob.data.polygons) for ob in objects)==470
render("AFTER_REAL_BLENDER_SHADED.png",False)
render("AFTER_REAL_BLENDER_WIREFRAME.png",True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC),compress=False)
assert SRC.read_bytes().startswith(b"BLENDER-v400")
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
 if ob.type in ("MESH","EMPTY"):ob.select_set(True)
bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,axis_forward='-Z',axis_up='Y',
 apply_unit_scale=True,global_scale=1,bake_anim=False,add_leaf_bones=False,object_types={'MESH','EMPTY'})
assert FBX.read_bytes().startswith(b"Kaydara FBX Binary  \x00\x1a\x00")
orig=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(FBX))
added=[ob for ob in bpy.context.scene.objects if ob not in orig]
reimport=[ob for ob in added if ob.type=="MESH"]
assert len(reimport)==4
assert sum(sum(len(f.vertices)-2 for f in ob.data.polygons) for ob in reimport)==470
assert sum(bool(ob.data.uv_layers) for ob in reimport)==4
micro=sum(1 for ob in reimport for f in ob.data.polygons if f.area<1e-10)
assert micro==0,("FBX reimport sliver regression",micro)
rebounds=[]
for ob in reimport:
 rebounds.extend(ob.matrix_world@v.co for v in ob.data.vertices)
rlo=[min(x[i] for x in rebounds) for i in range(3)]
rhi=[max(x[i] for x in rebounds) for i in range(3)]
err=max(abs(a-b) for vec1,vec2 in [(original_bounds[0],rlo),(original_bounds[1],rhi)] for a,b in zip(vec1,vec2))
assert err<1e-4,("FBX bbox mismatch",err)
for ob in added:bpy.data.objects.remove(ob,do_unlink=True)
receipt={"id":MID,"kind":"PASS20_SURGICAL_TWO_TRIANGLE_EDGE_FLIPS","blender":bpy.app.version_string,
"source_old_blend_sha256":EXPECTED_BLEND,"source_old_fbx_sha256":EXPECTED_FBX,
"new_blend_sha256":sha(SRC),"new_fbx_sha256":sha(FBX),
"original_vertices_preserved_bitwise":True,"old_mesh_count":4,"new_mesh_count":4,
"triangles":470,"slivers_before":tiny_before,"slivers_after":small_after,
"patches":patch_records,"manifold_after":True,"uv0_after":True,
"fbx_reimport":{"mesh_objects":4,"triangles":470,"micro_sliver_faces":micro,"uv0_objects":4,"bbox_max_error_m":err},
"realtime_Unity6":"NOT_RUN","C01_02_independent":"PENDING","release":"HOLD_NO_MERGE"}
(QA/"PASS20_REAL_NATIVE_EDGE_FLIP_RECEIPT.json").write_text(json.dumps(receipt,indent=2))
print("PASS20_ACTUAL_BLENDER_SURGICAL_FIX_SUCCESS",json.dumps({"new_blend":sha(SRC),"new_fbx":sha(FBX),"micro_faces":micro,"bbox_delta":err}),flush=True)
