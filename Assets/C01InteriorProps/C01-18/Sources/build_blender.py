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
 if name=='P18-03':
  for wid in ('Wheel_LB','Wheel_LF','Wheel_RB','Wheel_RF'):
   wheel=by_name.get(wid)
   if wheel is None:raise RuntimeError(name+' missing movable wheel '+wid)
   for suffix in ('Hub_In','Hub_Out'):
    hub=by_name.get(wid+'_'+suffix)
    if hub is None:raise RuntimeError(name+' missing authored hub '+wid+'_'+suffix)
    world=hub.matrix_world.copy()
    hub.parent=wheel
    hub.matrix_world=world
   bolt=by_name.get(wid+'_CrownBolt')
   crown=by_name.get(wid+'_ForkCrown')
   if bolt is None or crown is None:raise RuntimeError(name+' missing wheel crown/bolt '+wid)
   world=bolt.matrix_world.copy()
   bolt.parent=crown
   bolt.matrix_world=world
   # OBJ source Y-up becomes Blender world Z-up: axle height .105m.
   world_center=wheel.matrix_world.translation
   if abs(world_center.z-0.105)>0.001:
    raise RuntimeError(name+f' wheel axle height differs from .105m: {wid} Z={world_center.z}')
   wheel_ground=min((wheel.matrix_world@v.co).z for v in wheel.data.vertices)
   if abs(wheel_ground)>0.001:
    raise RuntimeError(name+f' wheel not touching ground: {wid} minZ={wheel_ground}')
 if name=='P18-01':
  for hinge in ('RearHinge_L','RearHinge_R'):
   pin=by_name.get(hinge+'_Pin')
   if pin is None:raise RuntimeError(name+' missing original hinge pin '+hinge)
   for suffix in ('Retainer_L','Retainer_R'):
    retainer=by_name.get(hinge+'_'+suffix)
    if retainer is None:raise RuntimeError(name+' missing authored retainer '+hinge+'_'+suffix)
    world=retainer.matrix_world.copy()
    retainer.parent=pin
    retainer.matrix_world=world
 # Reference-driven PASS16: new moving lid keepers inherit lid transform,
 # whereas rear-brace and caster-plate fasteners remain on rigid supports.
 if name=='P18-01':
  lid=by_name.get('Upper_Lid')
  if lid is None:raise RuntimeError('P18-01 missing Upper_Lid')
  for side in ('L','R'):
   child=by_name.get('FrontLatch_'+side+'_UpperKeeper')
   if child is None:raise RuntimeError('P18-01 missing lid keeper '+side)
   world=child.matrix_world.copy()
   child.parent=lid
   child.matrix_world=world
 if name=='P18-02':
  for height in ('0.60','1.48'):
   for side in ('L','R'):
    parent=by_name.get('BackSupport_'+height+'_Gusset_'+side)
    child=by_name.get('BackSupport_'+height+'_GussetFastener_'+side)
    if parent is None or child is None:raise RuntimeError('P18-02 missing rear gusset/fastener '+height+side)
    world=child.matrix_world.copy()
    child.parent=parent
    child.matrix_world=world
 if name=='P18-03':
  for wheel in ('Wheel_LB','Wheel_LF','Wheel_RB','Wheel_RF'):
   parent=by_name.get(wheel+'_Anchor')
   child=by_name.get(wheel+'_AnchorRetainer')
   if parent is None or child is None:raise RuntimeError('P18-03 missing stationary caster mount '+wheel)
   world=child.matrix_world.copy()
   child.parent=parent
   child.matrix_world=world
 expected={'P18-01':(43,868),'P18-02':(55,1172),'P18-03':(61,1724)}
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
