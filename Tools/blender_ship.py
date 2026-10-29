"""Actual Blender authoring/export from the identical ship manifest used in Unity."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
PROJECT=ROOT if (ROOT/'Assets').is_dir() else ROOT/'UnityProject'
ship=json.loads((PROJECT/'Assets/C01ShipV3/Data/ship.json').read_text(encoding='utf-8'))
kit=json.loads((PROJECT/'Assets/C01Modular/Data/kit.json').read_text(encoding='utf-8'))
MODELS=PROJECT/'Assets/C01ShipV3/Models';SOURCE=ROOT/('C01Source' if PROJECT==ROOT else 'Source');QA=ROOT/('C01Ship_QA' if PROJECT==ROOT else 'QA')
for p in [MODELS,SOURCE,QA/'Blender']:p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
def B(p):return (p[0],-p[2],p[1])
def collection(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
sources_col=collection('SOURCE_MODULES_editable');groups={c:collection(c) for c in sorted({p['category'] for p in ship['placements']})};mats={}
def material(role,color):
    m=bpy.data.materials.new(role);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.6;bs.inputs['Metallic'].default_value=.25
    if role in ['SCREEN','THRUST']:bs.inputs['Emission Color'].default_value=color;bs.inputs['Emission Strength'].default_value=1.5
    if role=='GLASS':bs.inputs['Alpha'].default_value=color[3];bs.inputs['Transmission Weight'].default_value=.5;bs.inputs['Roughness'].default_value=.2
    return m
for d in kit['materials']+ship['materials']:mats[d['role']]=material(d['role'],d['color'])
tints={z['id']:material('Floor_'+z['id'],z['color']) for z in ship['zones']}
def converted(p):
    if 'outline' in p:return p
    lo,hi=p['lo'],p['hi'];return dict(role=p['role'],outline=[lo[0],lo[2],hi[0],lo[2],hi[0],hi[2],lo[0],hi[2]],y0=lo[1],y1=hi[1])
def geometry(p):
    p=converted(p);poly=list(zip(p['outline'][::2],p['outline'][1::2]));n=len(poly)
    verts=[B([x,y,z]) for y in [p['y0'],p['y1']] for x,z in poly]
    faces=[(0,i,i+1) for i in range(1,n-1)]+[(n,n+i+1,n+i) for i in range(1,n-1)]
    faces += [(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
    return verts,faces
sources={};allmods={m['id']:m for m in kit['modules']+ship['modules']}
for mid,m in allmods.items():
    parent=bpy.data.objects.new(mid,None);sources_col.objects.link(parent);parts=[]
    for i,p in enumerate(m['parts']):
        mesh=bpy.data.meshes.new(f'{mid}_{i}');vs,fs=geometry(p);mesh.from_pydata(vs,[],fs);mesh.update()
        obj=bpy.data.objects.new(f'{mid}__{i:02d}_{p["role"]}',mesh);sources_col.objects.link(obj);obj.parent=parent;mesh.materials.append(mats[p['role']]);parts.append(obj)
    sources[mid]=(parent,parts)
exports=[]
for m in ship['modules']:
    parent,parts=sources[m['id']];bpy.ops.object.select_all(action='DESELECT');parent.select_set(True)
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parent;originals=[]
    for o in parts:
        original=o.data;copy=original.copy();copy.transform(Matrix.Diagonal((-1,1,1,1)));copy.flip_normals();o.data=copy;originals.append((o,original,copy))
    bpy.ops.export_scene.fbx(filepath=str(MODELS/(m['id']+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,mesh_smooth_type='FACE')
    for o,original,copy in originals:o.data=original;bpy.data.meshes.remove(copy)
    bpy.ops.wm.obj_export(filepath=str(MODELS/(m['id']+'.obj')),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True,export_triangulated_mesh=True)
    exports.append(dict(module=m['id'],parts=len(parts),fbx_bytes=(MODELS/(m['id']+'.fbx')).stat().st_size))
def instantiate(mid,pos,yaw,name,coll,zone=''):
    parent=bpy.data.objects.new(name,None);coll.objects.link(parent);parent.location=B(pos);parent.rotation_euler.z=math.radians(yaw);parent['module_id']=mid;parent['zone']=zone
    for i,s in enumerate(sources[mid][1]):
        o=bpy.data.objects.new(s.name,s.data);coll.objects.link(o);o.parent=parent
        if zone and allmods[mid]['parts'][i]['role']=='FLOOR':o.material_slots[0].link='OBJECT';o.material_slots[0].material=tints[zone]
    for child in allmods[mid].get('children',[]):
        c=instantiate(child['module'],[0,0,0],child.get('yaw',0),name+'/'+child['socket'],coll);c.parent=parent;c.location=B(child['position'])
    return parent
for p in ship['placements']:instantiate(p['module'],[p['x'],p['y'],p['z']],p['yaw'],p['id'],groups[p['category']],p['zone'] if p['category']=='Floors' else '')
sources_col.hide_render=True;sources_col.hide_viewport=True;groups['Ceilings'].hide_render=True;groups['Ceilings'].hide_viewport=True
camdata=bpy.data.cameras.new('QA_Camera');cam=bpy.data.objects.new('QA_Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
center_z=(ship['body'][2]+ship['body'][3])/2
cam.location=B([42,65,center_z-65]);cam.rotation_euler=(Vector(B([20,0,center_z]))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=90
world=bpy.data.worlds.new('ShipSpace');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.055,.08,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6
sun_data=bpy.data.lights.new('Sun','SUN');sun=bpy.data.objects.new('Sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-25),math.radians(-25));sun_data.energy=2.2
area_data=bpy.data.lights.new('Fill','AREA');area=bpy.data.objects.new('Fill',area_data);scene.collection.objects.link(area);area.location=B([20,35,5]);area_data.energy=7000;area_data.size=45
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=2200;scene.render.resolution_y=1250;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'C01_Ship_FromPlan.blend'))
scene.render.filepath=str(QA/'Blender/Ship_Cutaway.png');bpy.ops.render.render(write_still=True)
groups['Ceilings'].hide_render=False;groups['Ceilings'].hide_viewport=False;scene.render.filepath=str(QA/'Blender/Ship_Exterior.png');bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for c in groups.values():
    for o in c.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(SOURCE/'C01_Ship_FromPlan.glb'),export_format='GLB',use_selection=True,export_yup=True)
# Round-trip every NEW FBX and every source part, using the documented handedness conversion.
checks=[]
for m in ship['modules']:
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(MODELS/(m['id']+'.fbx')));created=set(bpy.data.objects)-before;meshes=[o for o in created if o.type=='MESH'];errors=[]
    if len(meshes)!=len(m['parts']):errors.append('Part count')
    for i,p in enumerate(m['parts']):
        matches=[o for o in meshes if o.name.startswith(f'{m["id"]}__{i:02d}_')]
        if len(matches)!=1:errors.append(f'Part identity {i}');continue
        actual=[matches[0].matrix_world@v.co for v in matches[0].data.vertices];vs,_=geometry(p);expected=[Vector((-v[0],v[1],v[2])) for v in vs]
        if any(min((a-e).length for e in expected)>2e-5 for a in actual) or any(min((a-e).length for a in actual)>2e-5 for e in expected):errors.append(f'Vertices {i}')
        matches[0].data.calc_loop_triangles();n=len(p['outline'])//2
        if len(matches[0].data.loop_triangles)!=4*n-4:errors.append(f'Faces {i}')
    checks.append(dict(module=m['id'],status='PASS' if not errors else 'FAIL',errors=errors))
    for o in created:bpy.data.objects.remove(o,do_unlink=True)
report=dict(status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',blender=bpy.app.version_string,new_models=len(exports),exports=exports,roundtrips=checks,source='Source/C01_Ship_FromPlan.blend',assembly_glb='Source/C01_Ship_FromPlan.glb',mapping='Source (x,-z,y); FBX export-only X reflection compensates Unity handedness')
(QA/'blender_ship_qa.json').write_text(json.dumps(report,indent=2));print('C01_SHIP_BLENDER',report['status'])
