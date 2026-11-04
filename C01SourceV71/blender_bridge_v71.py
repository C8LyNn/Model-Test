"""Apply the v7.1 bridge delta to the editable v7.0 Blender assembly."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
delta = json.loads((ROOT / 'Assets/C01ShipV71/Data/bridge_delta.json').read_text(encoding='utf8'))


def remove(ident):
    obj = bpy.data.objects.get(ident)
    if obj is None:
        raise RuntimeError('Missing module ' + ident)
    for child in list(obj.children):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


def build(p):
    source = bpy.data.objects.get(p['model'])
    if source is None:
        raise RuntimeError('Missing reusable model ' + p['model'])
    col = bpy.data.collections['DECK_' + str(p['deck'])] if p['deck'] >= 0 else bpy.data.collections['GLOBAL_CORES']
    obj = bpy.data.objects.new(p['id'], None)
    col.objects.link(obj)
    obj.location = (p['x'], -p['z'], p['y'])
    obj.rotation_euler.z = math.radians(p['yaw'])
    obj['model_id'] = p['model']
    obj['zone'] = p['zone']
    obj['category'] = p['category']
    obj['gate_id'] = p['gate']
    obj['open_travel'] = (p['travel'][0], -p['travel'][2], p['travel'][1])
    for original in source.children:
        child = original.copy()
        child.data = original.data
        col.objects.link(child)
        child.parent = obj
        child.hide_render = p['category'].lower() in ('ceilings', 'hull') or (p['deck'] >= 0 and p['deck'] != 1)
        child.hide_viewport = child.hide_render
    return obj


for ident in delta['removed']:
    remove(ident)
for p in delta['added']:
    if bpy.data.objects.get(p['id']) is not None:
        raise RuntimeError('Duplicate module ' + p['id'])
    build(p)
for p in delta['changed']:
    if p['parent']:
        continue
    obj = bpy.data.objects.get(p['id'])
    if obj is None:
        raise RuntimeError('Missing changed module ' + p['id'])
    if obj['model_id'] != p['model']:
        remove(p['id'])
        obj = build(p)
    obj.location = (p['x'], -p['z'], p['y'])
    obj.rotation_euler.z = math.radians(p['yaw'])
for lift in delta['lifts']:
    car = bpy.data.objects[lift['id'] + '_CAR']
    car.location.x = lift['x']
    car.location.y = -lift['z']

out = ROOT / 'C01SourceV71/Source/C01_Ship_Multideck_v71_base.blend'
out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('C01 V7.1 Blender source saved:', out)
