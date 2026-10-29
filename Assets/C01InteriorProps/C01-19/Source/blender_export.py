"""Execute with Blender 4.x: blender -b -t 1 --python Assets/C01InteriorProps/C01-19/Source/blender_export.py
Creates real .blend and .fbx. Never mark files generated unless this script ran successfully.
"""
import bpy,json,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
models=json.loads((root/'Source'/'parts.json').read_text(encoding='utf8'))
colors={'steel':(.38,.45,.48,1),'dark':(.11,.16,.19,1),'fabric':(.30,.39,.43,1),'accent':(.90,.53,.16,1)}
def b(v):return (v[0],-v[2],v[1]) # Unity X/Y/Z -> Blender X/-Y/Z
for model in models:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mats={}
    for key,color in colors.items():
        mat=bpy.data.materials.new('M_C01_'+key.upper());mat.diffuse_color=color;mat.use_nodes=True
        n=mat.node_tree.nodes.get('Principled BSDF')
        if n:n.inputs['Base Color'].default_value=color
        mats[key]=mat
    origin=bpy.data.objects.new(model['id']+'_ROOT',None);bpy.context.collection.objects.link(origin)
    for part in model['parts']:
        w,h,d=part['size']
        bpy.ops.mesh.primitive_cube_add(size=1,location=b(part['center']))
        mesh=bpy.context.object;mesh.name=part['name'];mesh.dimensions=(w,d,h)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        mesh.data.materials.append(mats[part['material']])
        transform=mesh.matrix_world.copy();mesh.parent=origin;mesh.matrix_world=transform
    if model['id']=='P19-02':
        hinge=bpy.data.objects.new('Door_Hinge_Pivot',None);bpy.context.collection.objects.link(hinge)
        hinge.parent=origin;hinge.location=b([-.305,.9,-.237])
        for name in ('Door_Leaf','Door_Handle','Vent_Upper'):
            mesh=bpy.data.objects.get(name);transform=mesh.matrix_world.copy()
            mesh.parent=hinge;mesh.matrix_world=transform
    out=root/'Models'/model['id'];out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(model['id']+'.blend')))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in ('MESH','EMPTY'):obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(out/(model['id']+'.fbx')),use_selection=True,
          axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,bake_anim=False,
          add_leaf_bones=False,object_types={'MESH','EMPTY'})
    print('C01-19 GENERATED BLEND + FBX:',model['id'])
