import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
plan = json.loads((ROOT / 'Assets/C01ShipV72/Data/logistics.json').read_text(encoding='utf8'))
for m in plan['moves']:
    obj = bpy.data.objects.get(m['id'])
    if obj is None or obj.get('model_id') != m['model'] or obj.get('zone') != m['zone']:
        raise RuntimeError('Wrong object ' + m['id'])
    if abs(obj.location.x-m['toX']) > .0001 or abs(obj.location.y+m['toZ']) > .0001 or not obj.children:
        raise RuntimeError('Wrong object position or geometry ' + m['id'])
report = {'status': 'PASS', 'reopened': True, 'blender': bpy.app.version_string,
          'movedItems': len(plan['moves']), 'remappedZones': len(plan['swaps'])}
(ROOT / 'C01ShipV72_QA/blender_reopened.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report))
