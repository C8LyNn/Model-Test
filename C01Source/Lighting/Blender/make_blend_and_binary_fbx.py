"""Run with Blender: blender -b -t 1 --python make_blend_and_binary_fbx.py"""
import bpy, json, pathlib
BASE=pathlib.Path(__file__).resolve().parent
DATA=json.loads((BASE/'geometry_spec.json').read_text(encoding='utf-8'))
for aid,entry in DATA['assets'].items():
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 for material,rgba in DATA['materials'].items():
  ma=bpy.data.materials.get(material) or bpy.data.materials.new(material)
  ma.diffuse_color=rgba; ma.use_nodes=True
  bs=ma.node_tree.nodes.get('Principled BSDF')
  if bs:
   bs.inputs['Base Color'].default_value=rgba
   if material.startswith('Emission'):
    bs.inputs['Emission Color'].default_value=rgba
    bs.inputs['Emission Strength'].default_value=1.9
 for i,(material,pos,size) in enumerate(entry['parts']):
  bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
  ob=bpy.context.object; ob.name=f'{aid}_{material}_{i:02d}'; ob.dimensions=size
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  ob.data.materials.append(bpy.data.materials[material])
 for ob in bpy.context.scene.objects: ob.select_set(True)
 bpy.context.view_layer.objects.active=next(iter(bpy.context.scene.objects))
 bpy.ops.wm.save_as_mainfile(filepath=str(BASE/f'{aid}.blend'))
 bpy.ops.export_scene.fbx(filepath=str(BASE/f'{aid}.fbx'),use_selection=True,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,global_scale=1,add_leaf_bones=False,bake_space_transform=False)
print('C01-16 native .blend and Blender binary FBX created')
