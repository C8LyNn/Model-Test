"""Actual editable Blender source and FBX/OBJ/GLB export from the v5 assembly manifest."""
import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT.parent if (ROOT.parent/'Assets/C01ShipV6').is_dir() else ROOT/'UnityProject'
data=json.loads((PROJECT/'Assets/C01ShipV65/Data/ship_v65.json').read_text(encoding='utf-8'))
MODELS=ROOT/'Models';SOURCE=ROOT/'Source';QA=ROOT/'QA'
for p in [MODELS,SOURCE,QA/'Blender']:p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
def B(p):return (p[0],-p[2],p[1])
def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
source_col=collection('SOURCE_MODELS_editable');groups={n:collection(n) for n in ['DECK_0','DECK_1','DECK_2','GLOBAL_CORES','TRANSPORT']};mats={}
for item in data['materials']:
    role=item['role'];color=item['color'];m=bpy.data.materials.new(role);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.6;bs.inputs['Metallic'].default_value=.25
    if role in ['SCREEN','THRUST']:bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=1.4
    if role=='GLASS':bs.inputs['Alpha'].default_value=color[3];bs.inputs['Transmission Weight'].default_value=.4
    mats[role]=m
def geometry(p):
    poly=list(zip(p['outline'][::2],p['outline'][1::2]));n=len(poly)
    vertices=[B([x,y,z]) for y in [p['y0'],p['y1']] for x,z in poly]
    faces=[(0,i,i+1) for i in range(1,n-1)]+[(n,n+i+1,n+i) for i in range(1,n-1)]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
    return vertices,faces
sources={};exports=[]
for model in data['models']:
    mid=model['id'];parent=bpy.data.objects.new(mid,None);source_col.objects.link(parent);parts=[]
    for index,p in enumerate(model['parts']):
        mesh=bpy.data.meshes.new(mid+'_'+str(index));vs,fs=geometry(p);mesh.from_pydata(vs,[],fs);mesh.update();mesh.materials.append(mats[p['role']])
        o=bpy.data.objects.new(f'{mid}__{index:02d}_{p["role"]}',mesh);source_col.objects.link(o);o.parent=parent;parts.append(o)
    parent['sockets_json']=json.dumps(model.get('sockets',[]));sources[mid]=(parent,parts)
for model in data['models']:
    mid=model['id'];parent,parts=sources[mid];bpy.ops.object.select_all(action='DESELECT');parent.select_set(True)
    if os.environ.get('C01_V6_REUSE_EXPORTS')=='1':
        if not (MODELS/(mid+'.fbx')).is_file() or not (MODELS/(mid+'.obj')).is_file():raise RuntimeError('Missing prior actual export '+mid)
        exports.append(dict(model=mid,parts=len(parts),fbx_bytes=(MODELS/(mid+'.fbx')).stat().st_size));continue
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parent;originals=[]
    for o in parts:
        original=o.data;copy=original.copy();copy.transform(Matrix.Diagonal((-1,1,1,1)));copy.flip_normals();o.data=copy;originals.append((o,original,copy))
    bpy.ops.export_scene.fbx(filepath=str(MODELS/(mid+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=False)
    for o,original,copy in originals:o.data=original;bpy.data.meshes.remove(copy)
    bpy.ops.wm.obj_export(filepath=str(MODELS/(mid+'.obj')),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True,export_triangulated_mesh=True)
    exports.append(dict(model=mid,parts=len(parts),fbx_bytes=(MODELS/(mid+'.fbx')).stat().st_size))
checks=[]
prefixes=('P_Bed_MIRRORZ','P_GalleyCounter','P_MessTable','P_LaundryUnit','G_Leaf_W510','W3_H3000','N_H3000','F_','C_','G_Piece_','G_Leaf_','P_Bed','P_LiftCar','P_CargoLiftTile','P_Rail3','P_Vent_3m','H_BOW_')
check_ids={next(m['id'] for m in data['models'] if m['id'].startswith(prefix)) for prefix in prefixes if any(m['id'].startswith(prefix) for m in data['models'])}
for model in data['models']:
    if model['id'] not in check_ids: continue
    mid=model['id'];before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(MODELS/(mid+'.fbx')));created=set(bpy.data.objects)-before;meshes=[o for o in created if o.type=='MESH'];errors=[]
    if len(meshes)!=len(model['parts']):errors.append('Part count')
    for i,p in enumerate(model['parts']):
        found=[o for o in meshes if o.name.startswith(f'{mid}__{i:02d}_')]
        if len(found)!=1:errors.append('Part identity '+str(i));continue
        actual=[found[0].matrix_world@v.co for v in found[0].data.vertices];vs,_=geometry(p);expected=[Vector((-v[0],v[1],v[2])) for v in vs]
        if any(min((a-e).length for e in expected)>3e-5 for a in actual) or any(min((a-e).length for a in actual)>3e-5 for e in expected):errors.append('Vertices '+str(i))
        found[0].data.calc_loop_triangles();n=len(p['outline'])//2
        if len(found[0].data.loop_triangles)!=4*n-4:errors.append('Faces '+str(i))
    checks.append(dict(model=mid,status='PASS' if not errors else 'FAIL',errors=errors))
    for o in created:bpy.data.objects.remove(o,do_unlink=True)
(QA/'blender_models_v65.json').write_text(json.dumps(dict(status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',models=len(exports),roundtrips=checks),indent=2))
cars={}
for lift in data['lifts']:
    o=bpy.data.objects.new(lift['car'],None);groups['TRANSPORT'].objects.link(o);o.location=B([lift['x'],0,lift['z']]);o['elevations']=lift['elevations'];cars[lift['car']]=(o,lift)
instances=[]
for p in data['placements']:
    group=groups['DECK_'+str(p['deck'])] if p['deck']>=0 else groups['GLOBAL_CORES'];parent=bpy.data.objects.new(p['id'],None);group.objects.link(parent)
    if p['parent']:
        car,lift=cars[p['parent']];parent.parent=car;parent.location=B([p['x']-lift['x'],p['y'],p['z']-lift['z']])
    else:parent.location=B([p['x'],p['y'],p['z']])
    parent.rotation_euler.z=math.radians(p['yaw']);parent['model_id']=p['model'];parent['zone']=p['zone'];parent['category']=p['category'];parent['gate_id']=p['gate'];parent['open_travel']=B(p['travel'])
    children=[]
    for src in sources[p['model']][1]:
        o=bpy.data.objects.new(src.name,src.data);group.objects.link(o);o.parent=parent;children.append(o)
    instances.append((p,parent,children))
source_col.hide_render=True;source_col.hide_viewport=True
def view(deck=None,all_decks=False):
    for p,parent,children in instances:
        hidden=p['category'].lower() in ['ceilings','hull'] or (not all_decks and p['deck']>=0 and p['deck']!=deck)
        for o in children:o.hide_render=hidden;o.hide_viewport=hidden
view(1)
camera_data=bpy.data.cameras.new('QA_Camera');camera=bpy.data.objects.new('QA_Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
camera.location=B([140,200,-130]);camera.rotation_euler=(Vector(B([63,0,45]))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=270
world=bpy.data.worlds.new('ShipSpace');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.055,.08,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
sun_data=bpy.data.lights.new('Sun','SUN');sun=bpy.data.objects.new('Sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(.4,-.45,-.45);sun_data.energy=2.2
area_data=bpy.data.lights.new('Fill','AREA');area=bpy.data.objects.new('Fill',area_data);scene.collection.objects.link(area);area.location=B([30,70,25]);area_data.energy=12000;area_data.size=75
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=2200;scene.render.resolution_y=1250;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'C01_Ship_Multideck_v65_base.blend'))
# Unity screenshots are the visual evidence; Blender supplies editable source.
report=dict(status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',blender=bpy.app.version_string,models=len(exports),placements=len(instances),exports=exports,roundtrips=checks,source='Source/C01_Ship_Multideck_v65_base.blend',assembly_glb=None,roundtrip_checked=len(checks),roundtrip_scope='sampled models')
(QA/'blender_v65.json').write_text(json.dumps(report,indent=2));print('C01_V65_BLENDER',report['status'])
