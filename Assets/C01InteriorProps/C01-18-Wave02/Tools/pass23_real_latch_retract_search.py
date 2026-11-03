"""P18-07 W23 real signed BLEND+FBX: find short axis-aligned visual-latch retraction
with original native hinge 23 poses, five lid/handle meshes and exact BVH triangles.
No source asset edits, no geometry export, and no Unity PASS claim.
"""
import bpy, json, sys, math, pathlib,hashlib
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
SHA={"blend":"5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d",
     "fbx":"858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554"}
FILES={"blend":R/"Sources"/"P18-07.blend","fbx":R/"Models"/"P18-07.fbx"}
MOV=["Bin_Lid","Lid_Label","Handle_Post_L","Handle_Post_R","Handle_Grip"]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
for k,p in FILES.items():
 assert p.stat().st_size>=41000 and sha(p)==SHA[k],("SHA drift",k)
assert FILES["blend"].read_bytes().startswith(b"BLENDER-")
assert FILES["fbx"].read_bytes().startswith(b"Kaydara FBX Binary")
def swept(which,delta):
 meshes={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
 assert len(meshes)==10
 lock=meshes["Front_Lock"];hinge=bpy.data.objects["Toolbox_LidHinge"]
 assert hinge.type=="EMPTY" and all(meshes[n].parent==hinge for n in MOV)
 basis=hinge.rotation_euler.copy();lock_mat=lock.matrix_world.copy()
 # Δ is in ORIGINAL (export-consistent) Blender world coordinates for this test.
 lock.matrix_world=Matrix.Translation(Vector(delta))@lock_mat
 bpy.context.view_layer.update()
 lock.data.calc_loop_triangles()
 fixed=BVHTree.FromObject(lock,bpy.context.evaluated_depsgraph_get(),epsilon=0)
 contacts=[]
 for deg in range(0,111,5):
  hinge.rotation_euler=basis.copy();hinge.rotation_euler.x=basis.x-math.radians(deg)
  bpy.context.view_layer.update()
  for n in MOV:
   mesh=meshes[n];mesh.data.calc_loop_triangles()
   movable=BVHTree.FromObject(mesh,bpy.context.evaluated_depsgraph_get(),epsilon=0)
   hits=movable.overlap(fixed)
   if hits:contacts.append({"angle":deg,"moving":n,"triangle_pairs":len(hits)})
 hinge.rotation_euler=basis;lock.matrix_world=lock_mat
 bpy.context.view_layer.update()
 return contacts
def open_scene(fmt):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if fmt=="blend":bpy.ops.wm.open_mainfile(filepath=str(FILES["blend"]))
 else:bpy.ops.import_scene.fbx(filepath=str(FILES["fbx"]))
def check(fmt,offsets):
 open_scene(fmt)
 return [(d,swept(fmt,d)) for d in offsets]
offsets=[(0,0,0)]
for mm in range(5,126,5):
 d=mm/1000
 for axis in range(3):
  for sign in [-1,1]:
   v=[0.,0.,0.];v[axis]=sign*d;offsets.append(tuple(v))
# Early exit per branch when a first passing displacement found: all source, then FBX.
open_scene("blend")
original=swept("blend",(0,0,0))
assert any(t["angle"]==0 for t in original) and any(t["angle"]==5 for t in original)
winners=[]
for delta in offsets[1:]:
 contacts=swept("blend",delta)
 if not contacts:winners.append(delta)
# Test every winner on FBX actual reimport, select 3 lowest displacement options
assert winners,"No geometric short-axis retraction found within 125mm"
winners.sort(key=lambda x:(round(sum(abs(y) for y in x),6), 0 if x[2]<0 else 1,0 if x[1]<0 else 1,x))
open_scene("fbx")
fbx_original=swept("fbx",(0,0,0))
assert [(t["angle"],t["moving"],t["triangle_pairs"]) for t in fbx_original]==[(t["angle"],t["moving"],t["triangle_pairs"]) for t in original]
results=[]
for d in winners:
 c=swept("fbx",d)
 if not c:results.append({"world_delta_blender_m":d,"contact_count_source":0,"contact_count_imported_fbx":0})
selected=results[0] if results else None
assert selected,"No source+FBX common retracting axis"
out={"asset":"P18-07","wave":23,"sha256":SHA,"tool":"actual Blender4 BLEND & reimported FBX7400 indexed BVH",
"tested_offsets":len(offsets),"sampled_lid_angles_deg":list(range(0,111,5)),
"mesh_count":10,"moving_parts":MOV,
"original_static_latch_versus_lid_contacts_native":original,
"original_static_latch_versus_lid_contacts_fbx":fbx_original,
"geometrically_clean_retract_candidates_source":len(winners),
"geometrically_clean_retract_candidates_fbx":len(results),
"valid_candidate_offsets":results[:15],
"selected_geometric_retract":selected,
"semantic_hold":"The offsets are in Blender WORLD coordinates. Unity imported local axis, animation, renderer and colliders still require genuine licensed Editor/PlayMode before game acceptance.",
"native_asset_changes":0,"exports":0,"unity":"NOT_RUN","C01_02":"INDEPENDENT_RETEST_PENDING"}
q=R/"QA"/"Pass23"/"P18-07_REAL_SIGNED_LATCH_RETRACT_BVH.json";q.parent.mkdir(parents=True,exist_ok=True)
q.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
print("C01_18_W23_REAL_RETRACT_QA_PASS",json.dumps({"selected":selected,"tested_offsets":len(offsets),"native_valid":len(winners),"fbx_valid":len(results),"locked_original":original}),flush=True)
