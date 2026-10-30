"""Run with Blender 4.x: blender -b --python build_blender.py -- /absolute/path/to/C01-18
Imports OBJ polygon meshes, saves .blend and exports binary FBX. NOT RUN in authoring environment.
"""
import bpy,sys,pathlib
root=pathlib.Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else pathlib.Path(__file__).resolve().parents[1]
(root/'Sources').mkdir(parents=True,exist_ok=True)
for name in ('P18-01','P18-02','P18-03'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.scene.unit_settings.system='METRIC'
 bpy.ops.wm.obj_import(filepath=str(root/'Models'/(name+'.obj')))
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in objects:
  bpy.ops.object.select_all(action='DESELECT')
  o.select_set(True)
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
  if o.name.startswith('Wheel_'):o['C01_WheelPivot']='local axle center'
 bpy.ops.wm.save_as_mainfile(filepath=str(root/'Sources'/(name+'.blend')))
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 for o in objects:
  if not o.data.uv_layers:raise RuntimeError(name+" missing imported UV0: "+o.name)
  if not o.data.polygons:raise RuntimeError(name+" missing polygons: "+o.name)
 bpy.ops.export_scene.fbx(filepath=str(root/'Models'/(name+'.fbx')))
 # Actual FBX reimport in Blender, verifying exporter preserved the two P1 streams.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(root/'Models'/(name+'.fbx')))
 imported=[x for x in bpy.context.scene.objects if x.type=='MESH']
 if not imported:raise RuntimeError(name+" exported FBX imported no meshes")
 for o in imported:
  if not o.data.uv_layers:raise RuntimeError(name+" FBX missing UV0: "+o.name)
  if not o.data.polygons:raise RuntimeError(name+" FBX missing polygon normals: "+o.name)
 print('BLENDER_FBX_UV_NORMAL_ROUNDTRIP_PASS',name,len(imported),flush=True)
