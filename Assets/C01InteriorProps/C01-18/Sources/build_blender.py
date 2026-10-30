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
  if o.name in ('Wheel_LB','Wheel_LF','Wheel_RB','Wheel_RF'):
   o['C01_WheelPivot']='local axle center'
 # Wheel hubs are newly added authored meshes. Keep each pair parented to its existing
 # movable wheel while caster brackets, axle and gussets remain static frame geometry.
 bpy.context.view_layer.update()
 by_name={o.name:o for o in objects}
 for wid in ('Wheel_LB','Wheel_LF','Wheel_RB','Wheel_RF'):
  wheel=by_name.get(wid)
  if wheel is None:raise RuntimeError(name+' missing movable wheel '+wid)
  if name=='P18-03':
   for suffix in ('Hub_In','Hub_Out'):
    hub=by_name.get(wid+'_'+suffix)
    if hub is None:raise RuntimeError(name+' missing authored hub '+wid+'_'+suffix)
    world=hub.matrix_world.copy()
    hub.parent=wheel
    hub.matrix_world=world
   if abs(wheel.location.y-0.105)>0.001:raise RuntimeError(name+' wheel axle pivot not at y=.105: '+wid)
 expected={'P18-01':(37,684),'P18-02':(47,1012),'P18-03':(53,1532)}
 assert len(objects)==expected[name][0], f'{name} expected {expected[name][0]} authored mesh parts, got {len(objects)}'
 tri=lambda arr:sum(max(0,len(p.vertices)-2) for o in arr for p in o.data.polygons)
 assert tri(objects)==expected[name][1], f'{name} authored triangles changed: {tri(objects)}'
 assert len({o.name for o in objects})==len(objects), f'{name} duplicate part names'
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
 if len(imported)!=expected[name][0] or tri(imported)!=expected[name][1]:raise RuntimeError(name+f' FBX roundtrip part/tri mismatch: {len(imported)}/{tri(imported)}')
 for o in imported:
  if not o.data.uv_layers:raise RuntimeError(name+" FBX missing UV0: "+o.name)
  if not o.data.polygons:raise RuntimeError(name+" FBX missing polygon normals: "+o.name)
 print('BLENDER_FBX_UV_NORMAL_ROUNDTRIP_PASS',name,len(imported),flush=True)
