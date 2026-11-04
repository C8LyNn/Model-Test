"""Apply the same equipment and sector mapping to the editable Blender assembly."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
plan = json.loads((ROOT / 'Assets/C01ShipV72/Data/logistics.json').read_text(encoding='utf8'))
swaps = {s['original']: s['replacement'] for s in plan['swaps']}
moves = {m['id']: m for m in plan['moves']}
seen = set()
for obj in bpy.data.objects:
    if obj.name in moves:
        m = moves[obj.name]
        if obj.get('model_id') != m['model'] or abs(obj.location.x - m['fromX']) > .0001:
            raise RuntimeError('Unexpected object ' + obj.name)
        obj.location.x = m['toX']
        seen.add(obj.name)
    elif obj.get('zone') in swaps:
        obj['zone'] = swaps[obj['zone']]
if len(seen) != len(moves):
    raise RuntimeError('Missing moved objects: ' + str(set(moves) - seen))
out = ROOT / 'C01SourceV72/Source/C01_Ship_Multideck_v72_base.blend'
out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('C01 V7.2 Blender source saved:', out)
