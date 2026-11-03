"""Blender 4.x: real P19-05..08 native sources, FBX and renders. Unity X,Y,Z => Blender X,-Z,Y."""
import bpy,json,pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parent.parent
CATALOG=json.loads((ROOT/'Source'/'wave02_parts.json').read_text(encoding='utf8'))
COLORS={'steel':(.39,.47,.52,1),'dark':(.105,.15,.19,1),'fabric':(.30,.38,.43,1),'accent':(.88,.47,.13,1)}
def conv(v):return (v[0],-v[2],v[1])
def look(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for m in CATALOG:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system='METRIC'
    bpy.context.scene.unit_settings.scale_length=1
    materials={}
    for key,col in COLORS.items():
        mat=bpy.data.materials.new('M_C01_'+key.upper())
        mat.diffuse_color=col;mat.use_nodes=True
        bsdf=mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:bsdf.inputs['Base Color'].default_value=col
        materials[key]=mat
    root=bpy.data.objects.new(m['id']+'_ROOT',None);bpy.context.collection.objects.link(root)
    hinge=None
    if m.get('hinge') is not None:
        hinge=bpy.data.objects.new(m['id']+'_HINGE',None)
        bpy.context.collection.objects.link(hinge)
        hinge.parent=root;hinge.location=conv(m['hinge'])
    for p in m['parts']:
        sx,sy,sz=p['size']
        bpy.ops.mesh.primitive_cube_add(size=1,location=conv(p['center']))
        o=bpy.context.object;o.name=p['name']
        o.dimensions=(sx,sz,sy)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(materials[p['material']])
        parent=hinge if hinge is not None and p['moving'] else root
        w=o.matrix_world.copy();o.parent=parent;o.matrix_world=w
        assert len(o.data.uv_layers)>0,'Blender UV0 missing on '+p['name']
    out=ROOT/'Models'/m['id'];out.mkdir(parents=True,exist_ok=True)
    preview=ROOT/'Previews';preview.mkdir(parents=True,exist_ok=True)
    bpy.context.scene.render.engine='BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x=640
    bpy.context.scene.render.resolution_y=480
    bpy.context.scene.render.resolution_percentage=100
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.ops.object.light_add(type='AREA',location=(3,-4,5))
    light=bpy.context.object;light.data.energy=700;light.data.shape='DISK';light.data.size=6
    bpy.ops.object.camera_add(location=(4,-5,3))
    cam=bpy.context.object;cam.data.type='ORTHO'
    cam.data.ortho_scale=max(m['dims_xyz'])*1.9
    target=(0,0,m['dims_xyz'][1]*.3 if m['mount']=='floor' else 0)
    bpy.context.scene.camera=cam
    for suffix,pos in [('iso',(4,-5,3)),('front',(0,-5,1.1)),('side',(5,0,1.1))]:
        cam.location=pos;look(cam,target)
        bpy.context.scene.render.filepath=str(preview/(m['id']+'_'+suffix+'.png'))
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(m['id']+'.blend')))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH','EMPTY'}:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.fbx(filepath=str(out/(m['id']+'.fbx')),
        use_selection=True,global_scale=1,apply_unit_scale=True,
        axis_forward='-Z',axis_up='Y',add_leaf_bones=False,
        bake_anim=False,object_types={'MESH','EMPTY'})
    print('C01-19 W02 GENERATED',m['id'],flush=True)
