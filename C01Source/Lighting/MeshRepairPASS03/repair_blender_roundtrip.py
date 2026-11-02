"""C01-16 PASS 03: Source OBJ -> genuine Blender .blend + binary FBX and roundtrip.
Run from Blender 4.x with: blender -b -t 1 --python repair_blender_roundtrip.py -- P16-XX
Only repaired OBJ geometry is imported; no proxy/reconstruction primitives.
"""
import bpy,json,pathlib,sys
asset=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else None
if not asset: raise SystemExit("missing asset after --")
root=pathlib.Path(__file__).resolve().parents[1]
obj=root/"OBJ"/(asset+".obj")
if not obj.exists():raise SystemExit("missing repaired source "+str(obj))
output=pathlib.Path(__file__).resolve().parent/"BlenderExports"
output.mkdir(exist_ok=True)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=1
bpy.ops.wm.obj_import(filepath=str(obj))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
if not meshes:raise RuntimeError("no imported geometry")
for objmesh in meshes:
 if not objmesh.data.uv_layers:raise RuntimeError("missing UV0 "+objmesh.name)
 for f in objmesh.data.polygons:f.use_smooth=False
if asset=="P16-06":
 empty=bpy.data.objects.new("ROTOR_Y_ANIMATABLE",None)
 bpy.context.collection.objects.link(empty);empty.location=(0,-.20,0)
 bpy.context.view_layer.update()
 for item in meshes:
  if "_ROTOR_" in item.name:
   mat=item.matrix_world.copy()
   item.parent=empty
   item.matrix_world=mat
bpy.context.view_layer.update()
checks=[]
for ob in meshes:
 mesh=ob.data
 edge_use={}
 for f in mesh.polygons:
  ids=list(f.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):
   key=tuple(sorted([a,b]));edge_use[key]=edge_use.get(key,0)+1
 checks.append(dict(name=ob.name,vertices=len(mesh.vertices),edges=len(mesh.edges),faces=len(mesh.polygons),boundary=sum(n==1 for n in edge_use.values()),nonmanifold=sum(n>2 for n in edge_use.values())))
if any(x["boundary"] or x["nonmanifold"] for x in checks):raise RuntimeError("invalid manifold mesh "+str(checks))
bpy.ops.wm.save_as_mainfile(filepath=str(output/(asset+".blend")))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.fbx(filepath=str(output/(asset+".fbx")),use_selection=True,
axis_forward="-Z",axis_up="Y",apply_unit_scale=True,global_scale=1,add_leaf_bones=False)
triangles_before=sum(len(f.vertices)-2 for o in meshes for f in o.data.polygons)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(output/(asset+".fbx")))
triangles_after=sum(len(f.vertices)-2 for o in bpy.context.scene.objects if o.type=="MESH" for f in o.data.polygons)
if triangles_before!=triangles_after:raise RuntimeError("binary FBX roundtrip faces changed")
(output/(asset+"_roundtrip.json")).write_text(json.dumps({"asset":asset,"blender":bpy.app.version_string,"triangles_before":triangles_before,"triangles_after":triangles_after,"topology":checks,"fbx_roundtrip":"PASS"},indent=2))
print("NATIVE_BLENDER_FBX_ROUNDTRIP_PASS",asset)
