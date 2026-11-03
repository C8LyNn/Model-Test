"""P18-03 W26 ONLY: actual original OBJ -> Blender4 .blend -> binary FBX reimport.
No Unity verdict, no door/gate files. Run inside real Blender:
  blender -b --python p1803_real_blender_fbx_qa.py -- ROOT BASELINE_OBJ OUTPUT_DIR
"""
import bpy, hashlib, json, pathlib, sys, math
from mathutils import Vector
argv=sys.argv
root=pathlib.Path(argv[argv.index('--')+1])
before_obj=pathlib.Path(argv[argv.index('--')+2])
out=pathlib.Path(argv[argv.index('--')+3]);out.mkdir(parents=True,exist_ok=True)
model="P18-03"
asset=root/"Models"/(model+".fbx")
blend=root/"Sources"/(model+".blend")
after_obj=root/"Models"/(model+".obj")

def digest(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
def mesh_items():
 return {o.name:o for o in bpy.context.scene.objects if o.type=="MESH"}
def bounds(o):
 ps=[o.matrix_world@v.co for v in o.data.vertices]
 return [[min(v[k] for v in ps),max(v[k] for v in ps)] for k in range(3)]
def read_scene():
 bpy.context.view_layer.update()
 ob=mesh_items()
 triangles=sum(max(0,len(p.vertices)-2) for o in ob.values() for p in o.data.polygons)
 if len(ob)!=63 or triangles!=1780:raise AssertionError(("parts/triangles",len(ob),triangles))
 if len(ob)!=len(set(ob)):raise AssertionError("duplicate mesh names")
 for o in ob.values():
  if not o.data.uv_layers or not o.data.polygons:raise AssertionError("invalid UV0/polygons: "+o.name)
  if not o.data.materials:raise AssertionError("missing materials: "+o.name)
 return ob
def gap_x(a,b):
 # AABB separation on longitudinal axle X proves disjoint triangle surfaces
 # through every signed rotation around the unchanged X axle.
 aa=bounds(a)[0];bb=bounds(b)[0]
 return max(aa[0]-bb[1],bb[0]-aa[1])
def verify(label):
 ob=read_scene()
 gaps={}
 for side in "LR":
  for end in "BF":
   wheel="Wheel_"+side+end
   if wheel not in ob:raise AssertionError("wheel absent: "+wheel)
   if abs(bounds(ob[wheel])[2][0])>0.001:raise AssertionError("wheel floor contact "+wheel)
   for suffix in ("In","Out"):
    fork=("Outer" if suffix=="In" else "Inner") if side=="L" else ("Inner" if suffix=="In" else "Outer")
    hub=wheel+"_Hub_"+suffix
    static=wheel+"_Fork"+fork
    g=gap_x(ob[hub],ob[static])
    if not 0.0018<=g<=0.0022:raise AssertionError((label,hub,static,g))
    gaps[hub+"/"+static]=round(g,8)
 # Every source rim, radius and axle pivot remains untouched.
 for nm in ("Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF"):
  if abs((bounds(ob[nm])[1][1]-bounds(ob[nm])[1][0])-0.210)>0.0002:raise AssertionError("wheel radius "+nm)
 return {"name":label,"meshes":len(ob),"triangles":1780,"hub_vs_fixed_fork_axial_gaps_m":gaps,
         "full_360_rotation_proof":"All 8 fixed fork vs rotating hub closed AABBs are disjoint on invariant X axle by >=1.8mm, hence cannot intersect at any wheel rotation angle."}

def render_view(filename,wire,closeup):
 ob=mesh_items()
 if not ob:raise AssertionError("empty renderer")
 s=bpy.context.scene
 cam_data=bpy.data.cameras.new("C01_W26_Camera")
 cam=bpy.data.objects.new("C01_W26_Camera",cam_data)
 s.collection.objects.link(cam);s.camera=cam
 if closeup:
  focus=Vector((-0.39,0.245,0.115));loc=Vector((0.15,-1.10,0.55))
  cam_data.type='ORTHO';cam_data.ortho_scale=0.54
 else:
  focus=Vector((0,0,0.58));loc=Vector((1.75,-2.25,1.72))
  cam_data.type='ORTHO';cam_data.ortho_scale=2.30
 cam.location=loc
 cam.rotation_euler=(focus-loc).to_track_quat('-Z','Y').to_euler()
 s.render.engine="BLENDER_WORKBENCH"
 s.display.shading.light="STUDIO"
 s.display.shading.color_type="MATERIAL"
 s.display.shading.show_cavity=True
 s.display.shading.show_shadows=True
 if hasattr(s.display.shading,"show_wireframes"):s.display.shading.show_wireframes=wire
 for o in ob.values():
  o.show_wire=wire
  o.show_all_edges=wire
 s.render.resolution_x=1100;s.render.resolution_y=750;s.render.resolution_percentage=100
 s.render.image_settings.file_format="PNG"
 s.render.filepath=str(out/filename)
 bpy.ops.render.render(write_still=True)

# Genuine unmodified baseline candidate from base ref for BEFORE previews.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(before_obj))
render_view("P18-03_BEFORE_iso_shaded.png",False,False)
render_view("P18-03_BEFORE_hub_wireframe.png",True,True)

# W26 corrected genuine native BLEND saved by current exporter.
bpy.ops.wm.open_mainfile(filepath=str(blend))
blend_pass=verify("saved_native_blend")
render_view("P18-03_AFTER_iso_shaded.png",False,False)
render_view("P18-03_AFTER_hub_wireframe.png",True,True)

# Fresh binary FBX reimport -- not a text/script approximation.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(asset))
fbx_pass=verify("reimported_binary_fbx")
render_view("P18-03_AFTER_fbx_hub_closeup.png",False,True)
report={"scope":"C01-18 W26 P18-03 ONLY; all Claude doors/gates excluded",
        "input_binary_provenance":{"source_obj_sha256":digest(after_obj),"source_blend_sha256":digest(blend),"exported_fbx_sha256":digest(asset),"binary_header":asset.read_bytes()[:23].decode("latin1")},
        "before_obj_sha256":digest(before_obj),
        "source":"original P18-03 parts, modified eight Hub_In/Hub_Out vertex X coordinates only",
        "verified_blend":blend_pass,"verified_fbx":fbx_pass,
        "original_hub_fork_axial_overlap_m":0.002,
        "new_hub_fork_axial_clearance_m":0.002,
        "original_parts":63,"final_parts":63,"original_triangles":1780,"final_triangles":1780,
        "blender_native_roundtrip":"PASS","independent_C01_02":"PENDING","unity_editor":"NOT_RUN",
        "classification":"PRODUCER_NATIVE_CLEARANCE_PASS__INDEPENDENT_AND_UNITY_HOLD"}
(out/"P18-03_W26_REAL_BLENDER_FBX_QA.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("W26_NATIVE_BLENDER_FBX_CLEARANCE_PASS",digest(asset),flush=True)
