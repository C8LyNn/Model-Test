"""W21 C01-18: real Blender4 + actual binary FBX P18-07 locked-vs-unlocked latch witness.
READ ONLY: No source mesh, hierarchy, native BLEND, binary FBX or geometry modification.
Unlocked means Front_Lock EXCLUDED FROM COLLISION CHECK ONLY, not a working game animation.
The 1mm deeper lock remains unchanged, final mechanical release not established.
"""
import bpy,sys,pathlib,hashlib,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
BASE={"blend":"5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d",
"fbx":"858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554"}
FILES={"blend":ROOT/"Sources"/"P18-07.blend","fbx":ROOT/"Models"/"P18-07.fbx"}
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as fd:
  for c in iter(lambda:fd.read(1048576),b""): h.update(c)
 return h.hexdigest()
for fmt,path in FILES.items():
 assert path.stat().st_size>=40000,("Unhydrated input",path)
 assert sha(path)==BASE[fmt],("SHA DRIFT",fmt,sha(path))
assert FILES["blend"].read_bytes()[:8]==b"BLENDER-"
assert FILES["fbx"].read_bytes().startswith(b"Kaydara FBX Binary  ")
assert bpy.app.version>=(4,0,0)
MOV=("Bin_Lid","Lid_Label","Handle_Post_L","Handle_Post_R","Handle_Grip")
def bvh(obj):
 obj.data.calc_loop_triangles()
 pts=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
 tri=[tuple(t.vertices) for t in obj.data.loop_triangles]
 return BVHTree.FromPolygons(pts,tri,all_triangles=True,epsilon=0)
def audit(stage):
 meshes={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
 assert len(meshes)==10,(stage,len(meshes))
 assert sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes.values())==120
 assert all(o.data.uv_layers for o in meshes.values())
 hinge=bpy.data.objects.get("Toolbox_LidHinge")
 assert hinge and hinge.type=="EMPTY"
 assert all(meshes[n].parent==hinge for n in MOV),("Hinge lost",stage)
 fixed={n:o for n,o in meshes.items() if n not in MOV}
 assert len(fixed)==5 and "Front_Lock" in fixed
 # Variant states change only which original fixed objects participate in BVH.
 active={"LOCKED":fixed,
         "UNLOCKED_COLLIDER_DISABLED":{k:v for k,v in fixed.items() if k!="Front_Lock"}}
 initial=hinge.rotation_euler.copy()
 views={name:[] for name in active}
 contacts={name:[] for name in active}
 for angle in range(0,111,5):
  hinge.rotation_euler=initial.copy()
  hinge.rotation_euler.x=initial.x-math.radians(angle)
  bpy.context.view_layer.update()
  all_bvh={n:bvh(o) for n,o in meshes.items()}
  for state,targets in active.items():
   entries=[]
   for mov in MOV:
    for stat in targets:
     hits=all_bvh[mov].overlap(all_bvh[stat])
     if not hits:continue
     label="CLOSED_LID_CHASSIS_SEAM" if (mov=="Bin_Lid" and stat=="Bin_Chassis" and angle==0) else ("ENGAGED_LATCH_CONTACT" if stat=="Front_Lock" else "UNEXPECTED")
     item={"angle":angle,"moving":mov,"fixed":stat,"triangle_pairs":len(hits),"type":label}
     entries.append(item);contacts[state].append(item)
   views[state].append({"degrees":angle,"pairs":entries})
 hinge.rotation_euler=initial
 bpy.context.view_layer.update()
 return {"source":stage,"meshes":10,"triangles":120,"angles":23,"moving":list(MOV),
  "hinge_blender_world_xyz":[float(c) for c in hinge.matrix_world.translation],
  "contacts":contacts,
  "summary":{s:{"total_contacts":len(a),
     "lock_contacts":sum(z["type"]=="ENGAGED_LATCH_CONTACT" for z in a),
     "unexpected_contacts":sum(z["type"]=="UNEXPECTED" for z in a),
     "closed_seam":sum(z["type"]=="CLOSED_LID_CHASSIS_SEAM" for z in a)} for s,a in contacts.items()},
  "samples":views}
bpy.ops.wm.open_mainfile(filepath=str(FILES["blend"]))
native=audit("actual_blender_native")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FILES["fbx"]))
imported=audit("actual_binary_fbx_reimport")
def compact(x):
 return sorted((p["angle"],p["moving"],p["fixed"],p["type"],p["triangle_pairs"]) for p in x)
same=all(compact(native["contacts"][s])==compact(imported["contacts"][s]) for s in native["contacts"])
assert same,"Native vs binary FBX variant contact list diverged"
assert native["summary"]["LOCKED"]["lock_contacts"]>0,"Engaged latch no longer blocks"
assert native["summary"]["UNLOCKED_COLLIDER_DISABLED"]["unexpected_contacts"]==0,"Unlocked mechanical collision"
assert imported["summary"]["UNLOCKED_COLLIDER_DISABLED"]["unexpected_contacts"]==0
assert native["summary"]["UNLOCKED_COLLIDER_DISABLED"]["closed_seam"]<=1
assert imported["summary"]["UNLOCKED_COLLIDER_DISABLED"]["closed_seam"]<=1
out={"wave":"W21","owner":"C01-18","model":"P18-07","pin_sha256":BASE,
 "note":"Virtual latch collision-state test, neither actual unlocking mechanics nor Unity runtime",
 "native":native,"binary_fbx":imported,"source_fbx_exact_contact_parity":same,
 "conditional_moving_unlocked_state":"PRODUCER_BVH_PASS_WITH_LOCK_COLLIDER_DISABLED_ONLY",
 "locked_state":"ENGAGED_LATCH_HOLDS_MOTION_AT_0_5_DEGREES",
 "latch_unlock_animation_or_physics":"NOT_IMPLEMENTED_NOT_TESTED",
 "shape_changes":0,"native_reexport":"NOT_RUN_UNCHANGED_SOURCE",
 "independent_C01_02":"PENDING","unity6":"NOT_RUN","final_approval":"HOLD"}
q=ROOT/"QA"/"Pass21"/"P18-07_REAL_BLENDER_FBX_LATCH_STATES.json"
q.parent.mkdir(parents=True,exist_ok=True)
q.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("C01_W21_P18_07_NATIVE_ACTUAL_LATCH_CONTACT_PASS",json.dumps({
 "blend":BASE["blend"],"fbx":BASE["fbx"],"parity":same,
 "locked":native["summary"]["LOCKED"],
 "unlocked":native["summary"]["UNLOCKED_COLLIDER_DISABLED"],
 "result":out["conditional_moving_unlocked_state"]}),flush=True)
