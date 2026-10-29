import bpy, json, math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2]
BASE=R/'Assets/C01InteriorProps/P15'
S=json.loads((BASE/'Sources/geometry_spec.json').read_text(encoding='utf-8'))
BL=BASE/'Sources/Blender';FBX=BASE/'Models/FBX';PRE=BASE/'Previews/Blender'
for p in (BL,FBX,PRE):p.mkdir(parents=True,exist_ok=True)
def to_b(v):return (v[0],-v[2],v[1])
def select(items):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
def export(path,items):
    select(items)
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,global_scale=1,
        apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,
        bake_anim=False,object_types={'EMPTY','MESH'},path_mode='AUTO')
def material(name,color):
    m=bpy.data.materials.new('C01_P15_'+name);m.diffuse_color=tuple(color);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Base Color'].default_value=tuple(color);bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.42
    return m
def primitive(p,m):
    if p['shape']=='box':
        bpy.ops.mesh.primitive_cube_add(size=1)
        o=bpy.context.object;o.dimensions=(p['size'][0],p['size'][2],p['size'][1])
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=p.get('sides',16),radius=p['radius'],depth=p['depth'])
        o=bpy.context.object
        if p['axis']=='X':o.rotation_euler[1]=math.pi/2
        if p['axis']=='Z':o.rotation_euler[0]=math.pi/2
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.name=p['name'];o.location=to_b(p['center']);o.data.materials.append(m)
    return o
def snapshot(center,size,view,path):
    data=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',data);bpy.context.scene.collection.objects.link(cam)
    cx,cy,cz=center
    u={'front':(0,.10,3.2),'iso':(2.4,1.6,2.8),'side':(3.3,.10,0)}[view]
    cam.location=to_b((cx+u[0]*size,cy+u[1]*size,cz+u[2]*size))
    cam.rotation_euler=(Vector(to_b(center))-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=size*1.65
    sc=bpy.context.scene;sc.camera=cam;sc.render.engine='BLENDER_WORKBENCH'
    sc.display.shading.light='STUDIO';sc.display.shading.color_type='MATERIAL'
    sc.render.resolution_x=900;sc.render.resolution_y=700;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
for asset,meta in S['assets'].items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    mats={k:material(k,v) for k,v in S['materials'].items()}
    roots={};parts={'Body':[],'Door':[]}
    for comp in ('Body','Door'):
        if not any(p['asset']==asset and p['component']==comp for p in S['parts']):continue
        root=bpy.data.objects.new(asset+'_'+comp+'_ROOT',None);bpy.context.collection.objects.link(root)
        root.location=to_b(meta.get('hinge',[0,0,0])) if comp=='Door' else (0,0,0)
        roots[comp]=root
    for p in S['parts']:
        if p['asset']!=asset:continue
        o=primitive(p,mats[p['material']]);o.parent=roots[p['component']]
        parts[p['component']].append(o)
    bpy.ops.wm.save_as_mainfile(filepath=str(BL/(asset+'.blend')),compress=True)
    full=sum(([root]+parts[c] for c,root in roots.items()),[])
    export(FBX/(asset+'.fbx'),full)
    if asset=='P15-03':
        export(FBX/'P15-03_Body.fbx',[roots['Body']]+parts['Body'])
        hinge=roots['Door'];old=hinge.location.copy();hinge.location=(0,0,0);bpy.context.view_layer.update()
        export(FBX/'P15-03_Door.fbx',[hinge]+parts['Door'])
        hinge.location=old;bpy.context.view_layer.update()
    center={'P15-01':(.5,0,.07),'P15-02':(0,0,.04),'P15-03':(0,.9,0)}[asset]
    for view in ('front','iso','side'):
        snapshot(center,max(meta['size_wdh']),view,PRE/(asset+'_'+view+'.png'))
print('C01-15: BLENDER SOURCE / FBX / PREVIEW EXPORT COMPLETE')
