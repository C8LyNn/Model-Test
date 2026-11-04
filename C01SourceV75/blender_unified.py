"""Add the new galleries and group both deck modules under six sector owners."""
import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV75/Data/platforms.json').read_text(encoding='utf8'))
pairs=json.loads((root/'Assets/C01ShipV75/Data/sectors.json').read_text(encoding='utf8'))['mapping']
def B(x,y,z):return (x,-z,y)
for ident in plan['removed']:
    obj=bpy.data.objects.get(ident)
    if obj is None:raise RuntimeError('Missing wall '+ident)
    for child in list(obj.children):bpy.data.objects.remove(child,do_unlink=True)
    bpy.data.objects.remove(obj,do_unlink=True)
for p in plan['added']:
    template=bpy.data.objects.get(p['model'])
    if template is None:raise RuntimeError('Missing model '+p['model'])
    group=bpy.data.collections['DECK_2'];obj=bpy.data.objects.new(p['id'],None);group.objects.link(obj)
    x=p['x']+(p['travel'][0] if p['category']=='GateLeaves' else 0)
    obj.location=B(x,p['y'],p['z']);obj.rotation_euler.z=math.radians(p['yaw'])
    obj['model_id']=p['model'];obj['zone']=p['zone'];obj['category']=p['category'];obj['gate_id']=p['gate'];obj['open_travel']=B(*p['travel'])
    for original in template.children:
        child=original.copy();child.data=original.data;group.objects.link(child);child.parent=obj;child.hide_render=True;child.hide_viewport=True
collection=bpy.data.collections.new('V75_SEKTORY_DWA_POZIOMY');bpy.context.scene.collection.children.link(collection)
bpy.context.view_layer.update()
counts={}
for pair in pairs:
    parent=bpy.data.objects.new('SEKTOR_'+pair['owner'],None);collection.objects.link(parent);parent['zone']=pair['owner'];parent['height_m']=6
    items=[o for o in bpy.data.objects if o.get('model_id') and o.get('zone') in (pair['owner'],pair['upper'])]
    for obj in items:
        world=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=world;obj['zone']=pair['owner']
    counts[pair['owner']]=len(items)
    if len(items)<100:raise RuntimeError('Too few modules in '+pair['owner'])
out=root/'C01SourceV75/Source/C01_Ship_Multideck_v75_base.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('Saved',out,'sector modules',counts)
