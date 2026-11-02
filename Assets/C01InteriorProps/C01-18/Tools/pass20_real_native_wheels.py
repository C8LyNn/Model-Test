"""C01-18 W20: actual Blender native .blend and FBX P18-03 four-wheel/hub rolling QA.
Non-destructive, no export or altered asset. SHA-pinned real Git LFS binaries.
All contacts reported separately for rubber and moving hub vs rigid bearing interfaces.
"""
import bpy,math,pathlib,hashlib,json,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=pathlib.Path(sys.argv[sys.argv.index("--")+1]).resolve()
PIN={"blend":"ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56",
"fbx":"f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926"}
FILES={"blend":ROOT/"Sources"/"P18-03.blend","fbx":ROOT/"Models"/"P18-03.fbx"}
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as fp:
  for b in iter(lambda:fp.read(1<<20),b""):h.update(b)
 return h.hexdigest()
for k,p in FILES.items():
 assert p.stat().st_size>100000,("Not hydrated",p)
 assert sha(p)==PIN[k],("Source SHA drift",k,sha(p))
assert FILES["blend"].read_bytes().startswith(b"BLENDER-")
assert FILES["fbx"].read_bytes().startswith(b"Kaydara FBX Binary  ")
assert bpy.app.version>=(4,0,0),"Real Blender4 required"
WHEELS=("Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF")
def geometry_bvh(obj):
 obj.data.calc_loop_triangles()
 vs=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
 triangles=[tuple(p.vertices) for p in obj.data.loop_triangles]
 return BVHTree.FromPolygons(vs,triangles,all_triangles=True,epsilon=0)
def bounds_world(obj):
 pts=[obj.matrix_world@Vector(b) for b in obj.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def overlaps_bbox(a,b):
 return all(min(a[i][1],b[i][1])-max(a[i][0],b[i][0])>=0 for i in range(3))
def gather(tag):
 meshes={o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
 assert len(meshes)==63,(tag,len(meshes))
 assert sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes.values())==1780
 assert all(o.data.uv_layers for o in meshes.values()),"Missing UV0"
 contact_poses=[];summary={}
 for wid in WHEELS:
  wheel=meshes[wid]
  h1=meshes[wid+"_Hub_In"];h2=meshes[wid+"_Hub_Out"]
  assert h1.parent==wheel and h2.parent==wheel,("Incorrect moving hub parent",tag,wid)
  static_names=("Cart_Shelf_0","Cart_Shelf_1")+tuple(
      k for k in meshes if k.startswith("Cart_Upright_"))+tuple(
      wid+"_"+part for part in ("ForkInner","ForkOuter","ForkCrown","Anchor","Gusset","AnchorRetainer","Axle","AxleFastener"))
  stationary=[meshes[k] for k in static_names]
  assert len(stationary)==14 and all(o!=wheel and o.parent!=wheel for o in stationary)
  st_bvh={o.name:geometry_bvh(o) for o in stationary}
  st_box={o.name:bounds_world(o) for o in stationary}
  center=wheel.matrix_world.translation
  assert abs(center.z-.105)<.001,(tag,wid,"wrong axle height",tuple(center))
  assert abs(abs(center.x)-.39)<.001
  # Rotate around the WORLD X axle, not the Blender-importer's local Euler X.
  # FBX import can leave an axis-conversion rotation on object/parents.
  # The local-Euler method distorted the wheel orbit and falsely reported -43 mm floor penetration.
  rest_world=wheel.matrix_world.copy()
  contacts=[];rubber_contacts=[];ground=[]
  for deg in range(0,360,5):
   spin=Matrix.Translation(center) @ Matrix.Rotation(math.radians(deg),4,'X') @ Matrix.Translation(-center)
   wheel.matrix_world=spin @ rest_world
   bpy.context.view_layer.update()
   wb=bounds_world(wheel)
   ground.append(wb[2][0])
   for mob in (wheel,h1,h2):
    box=bounds_world(mob)
    for st in stationary:
     if not overlaps_bbox(box,st_box[st.name]):continue
     hits=geometry_bvh(mob).overlap(st_bvh[st.name])
     if not hits:continue
     witness={"wheel":wid,"angle_degrees":deg,"moving":mob.name,
               "fixed":st.name,"triangle_pair_count":len(hits),
               "classification":"BEARING_AXLE_CONTACT_EXPECTED" if st.name.endswith(("Axle","AxleFastener")) and mob!=wheel else "REQUIRES_ASSEMBLY_TRIAGE"}
     contacts.append(witness)
     if mob==wheel and not st.name.endswith(("Axle","AxleFastener")):rubber_contacts.append(witness)
  wheel.matrix_world=rest_world
  bpy.context.view_layer.update()
  summary[wid]={"wheel_axle_blender_xyz_m":[round(float(v),7) for v in center],
   "moving_children":[h1.name,h2.name],
   "angles_sampled":72,"rigid_parts_checked":14,"rubber_to_nonbearing_fixed_BVH_contacts":rubber_contacts,
   "moving_wheel_or_hub_other_contacts":contacts,
   "rolling_min_ground_m":min(ground),"rolling_max_ground_m":max(ground),
   "resting_ground_m":bounds_world(wheel)[2][0],
   "method":"WORLD X-axis rotation about original actual wheel object-space origin via 4x4 Matrix, BVH world triangle overlap and AABB broadphase at 5-degree increments. Contact can mean touch or volume intersection."}
 return {"format":tag,"mesh_parts":len(meshes),"triangles":1780,
         "per_wheel":summary,
         "nonbearing_rubber_contact_count":sum(len(a["rubber_to_nonbearing_fixed_BVH_contacts"]) for a in summary.values()),
         "total_contact_witnesses":sum(len(a["moving_wheel_or_hub_other_contacts"]) for a in summary.values())}
bpy.ops.wm.open_mainfile(filepath=str(FILES["blend"]))
source=gather("native_blend")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FILES["fbx"]))
binary=gather("binary_fbx_reimport")
result={"asset":"P18-03","wave":"W20","model_blend_sha256":PIN["blend"],"model_fbx_sha256":PIN["fbx"],
"source":source,"fbx":binary,"source_and_fbx_agree_on_nonbearing_rubber":source["nonbearing_rubber_contact_count"]==binary["nonbearing_rubber_contact_count"],
"source_and_fbx_agree_on_parts_and_children":list(source["per_wheel"].keys())==list(binary["per_wheel"].keys()),
"no_geometry_modification_or_reexport":True,"C01_02_independent":"PENDING","Unity_PhysX":"NOT_RUN","release":"HOLD",
"producer_disposition":"RUBBER_TO_RIGID_CLEAR_SAMPLED" if binary["nonbearing_rubber_contact_count"]==0 else "RUBBER_CONTACTS_REQUIRE_QA",
"coverage_limit":"Only axle spin in place, no caster steering, cart movement, wheel-ground integration or two-sided material rendering. Metal hub/bearing contacts explicitly reported, NOT categorically an error."}
out=ROOT/"QA"/"Pass20"/"P18-03_REAL_NATIVE_WHEEL_HUB_MOTION_QA.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print("C01_W20_P18_03_REAL_NATIVE_WHEEL_QA",json.dumps({
"blend":PIN["blend"],"fbx":PIN["fbx"],
"rubber_contacts_source":source["nonbearing_rubber_contact_count"],
"rubber_contacts_fbx":binary["nonbearing_rubber_contact_count"],
"metal_contact_witnesses_fbx":binary["total_contact_witnesses"],
"wheel_ground_envelope":{k:[round(v["rolling_min_ground_m"],6),round(v["rolling_max_ground_m"],6)] for k,v in binary["per_wheel"].items()}}),flush=True)
assert result["source_and_fbx_agree_on_nonbearing_rubber"],"source and FBX wheel contact disagreement"
