"""Apply the Unity bridge layout to the existing editable Blender assembly."""
import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parent.parent
layout=json.loads((root/'Assets/C01ShipV69/Data/bridge_layout.json').read_text(encoding='utf8'))
deck=bpy.data.collections.get('DECK_1')
if deck is None: raise RuntimeError('Missing DECK_1 collection in v6.8 source')

added=0
for placement in layout['placements']:
    obj=bpy.data.objects.get(placement['id'])
    if placement['added']:
        if obj is not None: raise RuntimeError('Duplicate object '+placement['id'])
        template=bpy.data.objects.get(placement['model'])
        if template is None or not template.children: raise RuntimeError('Missing source model '+placement['model'])
        obj=bpy.data.objects.new(placement['id'],None)
        deck.objects.link(obj)
        for source in template.children:
            part=bpy.data.objects.new(source.name,source.data)
            deck.objects.link(part)
            part.parent=obj
        obj['model_id']=placement['model'];obj['zone']='L1_BRIDGE';obj['category']='CoreStations'
        obj['gate_id']='';obj['open_travel']=(0.0,0.0,0.0)
        added+=1
    elif obj is None or obj.get('model_id')!=placement['model']:
        raise RuntimeError('Missing existing bridge object '+placement['id'])
    obj.location=(placement['x'],-placement['z'],placement['y'])
    obj.rotation_euler.z=math.radians(placement['yaw'])

bpy.context.view_layer.update()
for p in layout['placements']:
    obj=bpy.data.objects[p['id']]
    expected=(p['x'],-p['z'],p['y'])
    if any(abs(obj.location[i]-expected[i])>1e-5 for i in range(3)):
        raise RuntimeError('Position mismatch: '+p['id'])
    if not obj.children: raise RuntimeError('Empty model: '+p['id'])
out=root/'C01SourceV69/Source/C01_Ship_Multideck_v69_base.blend'
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
qa=root/'C01ShipV69_QA/blender_layout.json'
qa.parent.mkdir(parents=True,exist_ok=True)
qa.write_text(json.dumps({'status':'PASS','blender':bpy.app.version_string,'placements':len(layout['placements']),
                          'added':added,'source':str(out),'coordinate_check':'PASS'},indent=2),encoding='utf8')
print('C01 V6.9 BLENDER PASS',len(layout['placements']),added)
