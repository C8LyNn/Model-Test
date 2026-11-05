import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV77/Data/two_decks.json').read_text(encoding='utf8'))
source=bpy.data.collections['SOURCE_MODELS_editable']
def B(x,y,z):return (x,-z,y)
for model in plan['models']:
    parent=bpy.data.objects.new(model['id'],None);source.objects.link(parent);parent['sockets_json']='[]'
    for i,part in enumerate(model['parts']):
        points=list(zip(part['outline'][::2],part['outline'][1::2]));n=len(points)
        vertices=[B(x,y,z) for y in (part['y0'],part['y1']) for x,z in points]
        faces=[(0,j,j+1) for j in range(1,n-1)]+[(n,n+j+1,n+j) for j in range(1,n-1)]+[(j,n+j,n+(j+1)%n,(j+1)%n) for j in range(n)]
        mesh=bpy.data.meshes.new(model['id']+'_'+str(i));mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(bpy.data.materials[part['role']])
        child=bpy.data.objects.new(f"{model['id']}__{i:02d}_{part['role']}",mesh);source.objects.link(child);child.parent=parent
moved=set();moved_objects=[]
for m in plan['moves']:
    obj=bpy.data.objects.get(m['oldId'])
    if obj is None or obj.get('model_id')!=m['model']:raise RuntimeError('Missing object '+m['oldId'])
    owner=bpy.data.objects.get('SEKTOR_'+m['zone'])
    if owner is None:raise RuntimeError('Missing sector '+m['zone'])
    obj.parent=owner;obj.name=m['newId'];x,y,z,yaw=m['after'];obj.location=B(x,y,z);obj.rotation_euler.z=math.radians(yaw)
    obj['zone']=m['zone'];moved.add(m['oldId']);moved_objects.append(obj)
    for collection in list(obj.users_collection):
        if collection.name=='DECK_0':collection.objects.unlink(obj);bpy.data.collections['DECK_1'].objects.link(obj)
remove_objects=set()
for ident in plan['removed']:
    if ident in moved:continue
    obj=bpy.data.objects.get(ident)
    if obj is None:raise RuntimeError('Missing removal '+ident)
    remove_objects.add(obj)
# Collect the descendants in one traversal before the batch delete. Reading
# obj.children separately for thousands of modules scans the entire scene.
parents={}
for obj in bpy.data.objects:
    if obj.parent is not None:parents.setdefault(obj.parent,[]).append(obj)
old_collection=bpy.data.collections['DECK_0'];new_collection=bpy.data.collections['DECK_1']
pending=list(moved_objects)
while pending:
    for child in parents.get(pending.pop(),[]):
        if old_collection in child.users_collection:
            old_collection.objects.unlink(child)
            if new_collection not in child.users_collection:new_collection.objects.link(child)
        pending.append(child)
pending=list(remove_objects)
while pending:
    for child in parents.get(pending.pop(),[]):
        if child not in remove_objects:remove_objects.add(child);pending.append(child)
bpy.data.batch_remove(remove_objects)
if len(old_collection.objects):raise RuntimeError('Old deck collection still contains '+str(len(old_collection.objects))+' objects')
bpy.data.collections.remove(old_collection)
for p in plan['added']:
    template=bpy.data.objects.get(p['model'])
    if template is None:raise RuntimeError('Missing model '+p['model'])
    group=bpy.data.collections['DECK_1'];obj=bpy.data.objects.new(p['id'],None);group.objects.link(obj)
    if p['zone']=='L1_CARGO':obj.parent=bpy.data.objects['SEKTOR_L1_CARGO']
    obj.location=B(p['x'],p['y'],p['z']);obj.rotation_euler.z=math.radians(p['yaw'])
    obj['model_id']=p['model'];obj['zone']=p['zone'];obj['category']=p['category'];obj['gate_id']=p['gate'];obj['open_travel']=B(*p['travel'])
    for original in template.children:
        child=original.copy();child.data=original.data;group.objects.link(child);child.parent=obj;child.hide_render=True;child.hide_viewport=True
out=root/'C01SourceV77/Source/C01_Ship_Multideck_v77_base.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('Saved',out)
