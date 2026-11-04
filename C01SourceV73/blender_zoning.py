"""Apply the same sector and equipment changes to the Blender assembly."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
plan=json.loads((ROOT/'Assets/C01ShipV73/Data/zoning.json').read_text(encoding='utf8'))
swaps={s['original']:s['replacement'] for s in plan['swaps']};moves={m['id']:m for m in plan['moves']};seen=set()
for obj in bpy.data.objects:
    if obj.name in moves:
        move=moves[obj.name]
        if obj.get('model_id')!=move['model'] or abs(obj.location.x-move['fromX'])>.0001:
            raise RuntimeError('Unexpected module '+obj.name)
        obj.location.x=move['toX'];seen.add(obj.name)
    elif obj.get('zone') in swaps:obj['zone']=swaps[obj['zone']]
if len(seen)!=len(moves):raise RuntimeError('Missing modules '+str(set(moves)-seen))
out=ROOT/'C01SourceV73/Source/C01_Ship_Multideck_v73_base.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('Saved',out)
