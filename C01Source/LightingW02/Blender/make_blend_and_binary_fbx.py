import bpy, json, pathlib
HERE=pathlib.Path(__file__).resolve().parent
D=json.loads((HERE/'geometry_spec.json').read_text())
for aid,item in D['assets'].items():
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 for name,values in D['materials'].items():
  mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
  mat.use_nodes=True;rgba=(*values,1);mat.diffuse_color=rgba
  bs=mat.node_tree.nodes.get('Principled BSDF')
  if bs:
   bs.inputs['Base Color'].default_value=rgba
   if name.startswith('Emission'):
    bs.inputs['Emission Color'].default_value=rgba
    bs.inputs['Emission Strength'].default_value=1.9
 for index,(material,center,size) in enumerate(item['parts']):
  bpy.ops.mesh.primitive_cube_add(size=1,location=center)
  ob=bpy.context.object;ob.name=f'{aid}_{material}_{index:02d}';ob.dimensions=size
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  ob.data.materials.append(bpy.data.materials[material])
 if item.get('rotor_parts'):
  p=item['rotor_pivot'];parent=bpy.data.objects.new('ROTOR_Y_ANIMATABLE',None)
  bpy.context.collection.objects.link(parent);parent.location=p
  for index,(material,center,size) in enumerate(item['rotor_parts']):
   loc=[center[k]+p[k] for k in range(3)]
   bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
   ob=bpy.context.object;ob.name=f'{aid}_ROTOR_{material}_{index:02d}';ob.dimensions=size
   bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
   ob.data.materials.append(bpy.data.materials[material])
   ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
 bpy.ops.object.select_all(action='SELECT')
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/f'{aid}.blend'))
 bpy.ops.export_scene.fbx(filepath=str(HERE/f'{aid}.fbx'),use_selection=True,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
print('Native Blender source and binary FBX export complete')
