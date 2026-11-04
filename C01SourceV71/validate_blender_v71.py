import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
delta = json.loads((ROOT / 'Assets/C01ShipV71/Data/bridge_delta.json').read_text(encoding='utf8'))
for ident in delta['removed']:
    if bpy.data.objects.get(ident) is not None:
        raise RuntimeError('Removed module still exists: ' + ident)
for p in delta['added'] + [x for x in delta['changed'] if not x['parent']]:
    obj = bpy.data.objects.get(p['id'])
    if obj is None or obj.get('model_id') != p['model']:
        raise RuntimeError('Wrong module: ' + p['id'])
    expected = (p['x'], -p['z'], p['y'])
    if any(abs(obj.location[i] - expected[i]) > .0001 for i in range(3)):
        raise RuntimeError('Wrong position: ' + p['id'])
    if not obj.children:
        raise RuntimeError('No model geometry: ' + p['id'])
for lift in delta['lifts']:
    car = bpy.data.objects[lift['id'] + '_CAR']
    if abs(car.location.x - lift['x']) > .0001 or abs(car.location.y + lift['z']) > .0001:
        raise RuntimeError('Wrong car position: ' + lift['id'])
result = {'status': 'PASS', 'reopened': True, 'blender': bpy.app.version_string,
          'removed': len(delta['removed']), 'added': len(delta['added']),
          'changed': len(delta['changed']), 'lifts': len(delta['lifts'])}
(ROOT / 'C01ShipV71_QA/blender_reopened.json').write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps(result))
