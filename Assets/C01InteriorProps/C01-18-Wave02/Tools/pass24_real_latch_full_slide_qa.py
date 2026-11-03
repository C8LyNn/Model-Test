"""C01-18 W24 actual original P18-07 Blender 4 + reimported binary FBX:
closed-lid visual Front_Lock sliding in 2mm increments, all 9 other model
meshes, physical world-space triangle BVH and dynamic Unity-axis envelope.
Read-only existing native assets; exports 0, Unity Editor NOT_RUN.
"""
import bpy, pathlib, hashlib, json, sys
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

R=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
EXPECTED={
 "blend":"5fd990d8153430dd4f1a8893ebef0097465a404d1b2c6bbd77777de695b3e87d",
 "fbx":"858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554"}
FILES={"blend":R/"Sources"/"P18-07.blend","fbx":R/"Models"/"P18-07.fbx"}
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for buf in iter(lambda:f.read(1048576),b""):h.update(buf)
 return h.hexdigest()
for key,p in FILES.items():
 assert p.stat().st_size>40000 and digest(p)==EXPECTED[key],("signed immutable native SHA drift",key,p)
assert FILES["blend"].read_bytes()[:8]==b"BLENDER-"
assert FILES["fbx"].read_bytes().startswith(b"Kaydara FBX Binary")
assert bpy.app.version>=(4,0,0)
def world(obj):
 obj.data.calc_loop_triangles()
 verts=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
 tri=[tuple(t.vertices) for t in obj.data.loop_triangles]
 return verts,tri
def box_unity(meshes):
 # Original authoring Unity (x,y,z) -> original Blender (x,-z,y).
 v=[(q[0],q[2],-q[1]) for obj in meshes.values() for q in world(obj)[0]]
 lo=[min(p[k] for p in v) for k in range(3)]
 hi=[max(p[k] for p in v) for k in range(3)]
 return {"min_xyz_m":[round(x,9) for x in lo],
         "max_xyz_m":[round(x,9) for x in hi],
         "dimensions_xyz_m":[round(hi[k]-lo[k],9) for k in range(3)]}
def check(fmt):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if fmt=="blend":bpy.ops.wm.open_mainfile(filepath=str(FILES["blend"]))
 else:bpy.ops.import_scene.fbx(filepath=str(FILES["fbx"]))
 m={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
 assert len(m)==10,(fmt,"mesh parts",len(m))
 assert sum(sum(len(p.vertices)-2 for p in obj.data.polygons) for obj in m.values())==120
 assert "Front_Lock" in m and "Bin_Lid" in m and "Bin_Chassis" in m
 lock=m["Front_Lock"]
 original=lock.matrix_world.copy()
 samples=[]
 for mm in range(0,21,2):
  # W23 validated signed Blender WORLD (0,-.020,0).
  lock.matrix_world=Matrix.Translation(Vector((0,-mm/1000.,0)))@original
  bpy.context.view_layer.update()
  lv,lt=world(lock)
  lock_bvh=BVHTree.FromPolygons(lv,lt,all_triangles=True,epsilon=0)
  hits={}
  for name,obj in m.items():
   if name=="Front_Lock":continue
   ov,ot=world(obj)
   other=BVHTree.FromPolygons(ov,ot,all_triangles=True,epsilon=0)
   pairs=lock_bvh.overlap(other)
   if pairs:hits[name]=len(pairs)
  samples.append({"retract_mm":mm,"collision_triangle_pairs":hits,
                  "total_pairs":sum(hits.values()),"world_locked_lid_static":True,
                  "bbox_unity":box_unity(m)})
 lock.matrix_world=original
 bpy.context.view_layer.update()
 return samples
a=check("blend")
b=check("fbx")
def compact(samples):
 return [(x["retract_mm"],x["collision_triangle_pairs"],x["bbox_unity"]["dimensions_xyz_m"]) for x in samples]
equal=compact(a)==compact(b)
assert equal,("imported FBX changed original signed Blender lock-slide geometry",compact(a),compact(b))
assert a[0]["collision_triangle_pairs"].get("Bin_Lid")==13
assert "Bin_Lid" not in a[-1]["collision_triangle_pairs"]
assert not any(n!="Bin_Lid" for n in a[-1]["collision_triangle_pairs"]),"final 20mm slide still intersects other mesh parts"
# Validate progressive lock-to-lid contacts, but a temporary contact while lid
# remains CLOSED is the expected state and does NOT certify frictionless sliding.
assert all(x["collision_triangle_pairs"].get("Bin_Lid",0)<=13 for x in a)
summary={
 "real_blend_and_reimport_fbx_sample_contact_parity":equal,
 "original_locked_lid_triangle_pairs":a[0]["collision_triangle_pairs"].get("Bin_Lid",0),
 "fully_retracted_20mm_triangle_pairs":a[-1]["total_pairs"],
 "initial_dynamic_bounds_unity_xyz_m":a[0]["bbox_unity"]["dimensions_xyz_m"],
 "fully_retracted_dynamic_bounds_unity_xyz_m":a[-1]["bbox_unity"]["dimensions_xyz_m"],
 "depth_extent_increase_mm":round(1000*(a[-1]["bbox_unity"]["dimensions_xyz_m"][2]-a[0]["bbox_unity"]["dimensions_xyz_m"][2]),6)
}
data={
 "asset":"P18-07","wave":24,"test":"real signed Blender4 original BLEND plus true binary FBX reimport world BVH",
 "input_native_sha256":EXPECTED,"sampled_visible_lock_retraction_mm":[x["retract_mm"] for x in a],
 "original_lid_locked_rest_at_0deg":True,
 "mesh_count":10,"triangle_count":120,
 "source_blend":a,"reimported_binary_fbx":b,"summary":summary,
 "design_note":"Moving visible Front_Lock OUTWARDS may increase operational footprint; nominal 0.340m closed depth + current 0.341m actual plus extended latch must be separately reviewed by C01-01 / C01-13. Computed bbox is from exact rendered triangles, not PhysX collider sweeps.",
 "moving_lid_during_retract":"BLOCKED_BY_W24_RUNTIME_SOURCE",
 "independent_qc":"C01_02_PENDING",
 "owner_depth_tolerance":"C01_01_PENDING",
 "Unity6_Editor_and_PlayMode":"NOT_RUN",
 "original_mesh_changes":0,"native_reexports":0,"doors_touched":0,"release":"HOLD"
}
path=R/"QA"/"Pass24"/"P18-07_REAL_BLENDER_FBX_20MM_SLIDE_ENVELOPE.json"
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(data,indent=2)+"\n")
print("C01_W24_P1807_SIGNED_BLENDER_FBX_SLIDE_QA_EXECUTED",json.dumps(summary),flush=True)
