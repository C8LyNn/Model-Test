"""Create editable Blender sources and individual FBX meshes for v6.2 modules.

Run with Blender --background --python blender_export_v62.py. Geometry follows
the same dimensions and wall stripe bands consumed by ShipV62Builder.
"""
import bpy
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = Path(__file__).resolve().parent
output = source / 'Models'
output.mkdir(parents=True, exist_ok=True)
manifest = json.loads((root / 'Assets/C01ShipV62/Data/polish_v62.json').read_text(encoding='utf-8'))
old = json.loads((root / 'Assets/C01ShipV6/Data/ship_v6.json').read_text(encoding='utf-8'))

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
materials = {}
for item in old['materials']:
    m = bpy.data.materials.new(item['role'])
    m.diffuse_color = item['color'][:4]
    materials[item['role']] = m


def coord(v):
    return (v[0], v[2], v[1])


def key(v):
    return str(round(v * 10000))


def box(center, size):
    x,y,z = center; a,b,c = (v/2 for v in size)
    vs = [(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
          (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
    fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return vs, fs


def model(name, parts):
    vertices, faces, indices = [], [], []
    roles = []
    for role, vs, fs in parts:
        if role not in roles: roles.append(role)
        offset = len(vertices)
        vertices.extend(coord(v) for v in vs)
        faces.extend(tuple(offset+i for i in reversed(f)) for f in fs)  # swap Y/Z reverses handedness
        indices.extend([roles.index(role)] * len(fs))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj)
    for role in roles: mesh.materials.append(materials[role])
    for polygon, index in zip(mesh.polygons, indices): polygon.material_index = index
    return obj


models = {}
for lift in manifest['lifts']:
    for p in lift['panels']:
        size = p['size']; name = 'CABIN_'+'_'.join(key(v) for v in size)
        if name not in models:
            vertices, faces = box((0,0,0), size)
            models[name] = model(name, [('PANEL',vertices,faces)])

for wall in manifest['walls']:
    height, y = wall['height'], wall['y']
    phase = round((y % 3) * 10000)
    name = 'wall_'+key(height)+'_'+str(phase)
    if name in models: continue
    cuts = {0.0, height}
    for center in wall['stripeCenters']:
        cuts.add(max(0,min(height,center-y-.06)))
        cuts.add(max(0,min(height,center-y+.06)))
    cuts = sorted(cuts); vertices, faces, roles = [], [], []
    def quad(vs, role):
        offset=len(vertices);vertices.extend(vs);faces.append(tuple(offset+i for i in range(4)));roles.append(role)
    l,r,z=.15,2.85,.15
    for a,b in zip(cuts,cuts[1:]):
        if b-a < .00001: continue
        global_y=y+(a+b)/2
        role='METAL' if any(abs(global_y-c)<.06001 for c in wall['stripeCenters']) else 'PANEL'
        quad([(l,a,z),(r,a,z),(r,b,z),(l,b,z)],role)
        quad([(r,a,-z),(l,a,-z),(l,b,-z),(r,b,-z)],role)
    quad([(l,0,-z),(l,0,z),(l,height,z),(l,height,-z)],'PANEL')
    quad([(r,0,z),(r,0,-z),(r,height,-z),(r,height,z)],'PANEL')
    quad([(l,0,-z),(r,0,-z),(r,0,z),(l,0,z)],'PANEL')
    quad([(l,height,z),(r,height,z),(r,height,-z),(l,height,-z)],'PANEL')
    parts=[]
    for role in ('PANEL','METAL'):
        selected=[f for f,mat in zip(faces,roles) if mat==role]
        if selected: parts.append((role,vertices,selected))
    models[name]=model(name,parts)


def make_bridge(kind):
    parts=[]
    def add(role,center,size):
        vertices,faces=box(center,size);parts.append((role,vertices,faces))
    if kind in ('captain','chair'):
        width=1.35 if kind=='captain' else 1.0
        add('METAL',(0,.25,0),(.55,.5,.55));add('DARK',(0,.62,0),(.95,.24,width))
        add('PANEL',(.4,1.15,0),(.15,.82,width))
        for sign in (-1,1): add('TRIM',(-.075,.82,sign*(width/2-.07)),(.8,.16,.14))
    elif kind=='console':
        add('DARK',(0,.45,0),(.9,.9,1.8));add('SCREEN',(0,.92,0),(.8,.04,1.62));add('TRIM',(.43,1.02,0),(.04,.2,1.8))
    else:
        add('METAL',(0,.18,0),(.35,.36,3));add('SCREEN',(0,1.72,0),(.18,2.72,2.78))
        for sign in (-1,1):add('DARK',(0,1.72,sign*1.445),(.3,2.72,.11))
        add('METAL',(0,3.13,0),(.3,.1,3))
    return model('BRIDGE_'+kind,parts)


for kind in ('captain','chair','console','screen'):
    models['BRIDGE_'+kind] = make_bridge(kind)

for index, (name,obj) in enumerate(sorted(models.items())):
    obj.location = (index % 8 * 5, index // 8 * 5, 0)
bpy.ops.wm.save_as_mainfile(filepath=str(source/'C01_Ship_v62_NewModules.blend'))
for name,obj in sorted(models.items()):
    old_position=obj.location.copy();obj.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(output/(name+'.fbx')),use_selection=True,
                             axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,
                             object_types={'MESH'},use_mesh_modifiers=True)
    obj.location=old_position

report={'status':'PASS','blend':str(source/'C01_Ship_v62_NewModules.blend'),
        'fbx_count':len(models),'models':sorted(models)}
(source/'blender_export_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('C01 V62 BLENDER EXPORT COMPLETE',len(models))
