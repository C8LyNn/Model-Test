"""C01-18 W20: surgical native hierarchy repair on P18-07: lid-mounted grip follows real hinge.
Input: exact W19 genuine Blender .blend; output QA/Pass20/Native only until measured PASS.
Changes: 3 existing object parent references, NO mesh/UV0/material/pivot/rest-transform edits.
"""
import bpy,sys,pathlib,hashlib,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
S=ROOT/"Sources"/"P18-07.blend"
OUT=ROOT/"QA"/"Pass20"/"Native";OUT.mkdir(parents=True,exist_ok=True)
OLD="ca81b1b5b03354f6988657324f2f30b28ff1b785529388fb692469ffb2d3f9c3"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
assert sha(S)==OLD,("W19 immutable source SHA changed",sha(S))
assert S.read_bytes()[:8]==b"BLENDER-"
assert bpy.app.version>=(4,0,0)
bpy.ops.wm.open_mainfile(filepath=str(S))
meshes={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
assert len(meshes)==10
def tris():return sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes.values())
assert tris()==120
hinge=bpy.data.objects.get("Toolbox_LidHinge")
assert hinge and hinge.type=="EMPTY"
orig_pivot=hinge.matrix_world.copy()
assert meshes["Bin_Lid"].parent==hinge and meshes["Lid_Label"].parent==hinge
handles=("Handle_Post_L","Handle_Post_R","Handle_Grip")
def signature(o):
 return (tuple(tuple(round(float(c),8) for c in v.co) for v in o.data.vertices),
         tuple(tuple(p.vertices) for p in o.data.polygons),
         tuple(tuple(tuple(round(float(q),8) for q in e.uv) for e in layer.data) for layer in o.data.uv_layers),
         tuple(m.name if m else None for m in o.data.materials))
before_signatures={n:signature(o) for n,o in meshes.items()}
before_matrix={n:o.matrix_world.copy() for n,o in meshes.items()}
for n in handles:
 o=meshes[n]
 assert o.parent!=hinge,("Already parented",n)
 w=o.matrix_world.copy()
 o.parent=hinge
 o.matrix_world=w
bpy.context.view_layer.update()
assert all(meshes[n].parent==hinge for n in handles)
assert all(signature(o)==before_signatures[n] for n,o in meshes.items())
assert all(all(abs((o.matrix_world-before_matrix[n])[i][j])<1e-5 for i in range(4) for j in range(4)) for n,o in meshes.items()),"Rest-frame drift"
assert all(abs((hinge.matrix_world-orig_pivot)[i][j])<1e-7 for i in range(4) for j in range(4))
assert tris()==120
def bvh(o):
 o.data.calc_loop_triangles()
 verts=[tuple(o.matrix_world@v.co) for v in o.data.vertices]
 faces=[tuple(t.vertices) for t in o.data.loop_triangles]
 return BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0)
def motion(label):
 allmeshes={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
 h=bpy.data.objects["Toolbox_LidHinge"]
 assert len(allmeshes)==10
 moving=("Bin_Lid","Lid_Label","Handle_Post_L","Handle_Post_R","Handle_Grip")
 assert all(allmeshes[n].parent==h for n in moving)
 fixed=[o for n,o in allmeshes.items() if n not in moving]
 rest=h.rotation_euler.copy()
 records=[];bad=[]
 for angle in range(0,111,5):
  h.rotation_euler=rest.copy()
  h.rotation_euler.x=rest.x-math.radians(angle)
  bpy.context.view_layer.update()
  fx={o.name:bvh(o) for o in fixed}
  for name in moving:
   mm=bvh(allmeshes[name])
   for stat in fixed:
    hits=mm.overlap(fx[stat.name])
    if not hits:continue
    permitted=(name=="Bin_Lid" and stat.name=="Bin_Chassis" and angle==0) or (
      name=="Bin_Lid" and stat.name=="Front_Lock" and angle<=5)
    entry={"moving":name,"static":stat.name,"angle_deg":angle,"triangle_pairs":len(hits),
           "gate":"ENGAGED_LATCH_REVIEW" if name=="Bin_Lid" and stat.name=="Front_Lock" else ("INTENTIONAL_CLOSED_SEAM" if permitted else "UNEXPECTED_CONTACT")}
    records.append(entry)
    if not permitted:bad.append(entry)
 h.rotation_euler=rest
 bpy.context.view_layer.update()
 return {"stage":label,"positions_tested":23,"moving_parts":list(moving),
         "contact_witnesses":records,"unexpected_contacts":bad}
after_source=motion("modified_authentic_blend")
newblend=OUT/"P18-07_W20.blend"
newfbx=OUT/"P18-07_W20.fbx"
bpy.ops.wm.save_as_mainfile(filepath=str(newblend))
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.context.scene.objects:
 if o.type in ("MESH","EMPTY"):o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(newfbx),use_selection=True,
 axis_forward="-Z",axis_up="Y",add_leaf_bones=False,apply_unit_scale=True,object_types={"MESH","EMPTY"})
assert newblend.read_bytes().startswith(b"BLENDER-")
assert newfbx.read_bytes().startswith(b"Kaydara FBX Binary  ")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(newfbx))
after_fbx=motion("real_binary_fbx_reimport")
imported=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert len(imported)==10 and all(o.data.uv_layers for o in imported)
assert sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in imported)==120
def normalized(entries):
 return sorted((e["moving"],e["static"],e["angle_deg"],e["gate"]) for e in entries)
same=normalized(after_source["contact_witnesses"])==normalized(after_fbx["contact_witnesses"])
result={"asset":"P18-07","wave":"W20","source_blend_old_sha256":OLD,
 "native_blend_sha256":sha(newblend),"binary_fbx_sha256":sha(newfbx),
 "new_native_blend_bytes":newblend.stat().st_size,"new_binary_fbx_bytes":newfbx.stat().st_size,
 "change":"Move existing Handle_Post_L, Handle_Post_R, Handle_Grip under existing Toolbox_LidHinge; preserve original mesh geometry, UV, materials, rest-frame world transforms and hinge pivot",
 "modified_mesh_parts":10,"triangles":120,"source":after_source,"fbx":after_fbx,
 "fbx_source_motion_agreement":same,
 "full_3D_latch_unlock":"NOT_IMPLEMENTED; engaged lock seam at rest and 5 degrees requires separate review",
 "C01_02_independent":"NOT_RUN","Unity6":"NOT_RUN",
 "promotion":"CANDIDATE_PASS" if same and not after_source["unexpected_contacts"] and not after_fbx["unexpected_contacts"] else "HOLD_UNEXPECTED_CONTACTS"}
file=OUT/"P18-07_W20_NATIVE_HINGE_REPAIR.json"
file.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("C01_W20_P18_07_HANDLE_NATIVE_RESULT",json.dumps({
  "status":result["promotion"],"agreement":same,
  "unexpected_source":after_source["unexpected_contacts"],"unexpected_fbx":after_fbx["unexpected_contacts"],
  "blend":result["native_blend_sha256"],"fbx":result["binary_fbx_sha256"]}),flush=True)
assert same,"Exporter changed material movement vs original Blender"
assert not after_source["unexpected_contacts"] and not after_fbx["unexpected_contacts"],"Unexpected collision: native candidate stays quarantined"
