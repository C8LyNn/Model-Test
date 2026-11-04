import bpy
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV75/Data/platforms.json').read_text(encoding='utf8'))
pairs=json.loads((root/'Assets/C01ShipV75/Data/sectors.json').read_text(encoding='utf8'))['mapping']
for p in plan['added']:
    obj=bpy.data.objects.get(p['id'])
    if obj is None or not obj.children or obj.get('model_id')!=p['model']:raise RuntimeError('Missing module '+p['id'])
    owner=next(x['owner'] for x in pairs if p['zone'] in (x['owner'],x['upper']))
    if obj.parent is None or obj.parent.name!='SEKTOR_'+owner:raise RuntimeError('Wrong owner '+p['id'])
    x=p['x']+(p['travel'][0] if p['category']=='GateLeaves' else 0)
    w=obj.matrix_world.translation
    if abs(w.x-x)>.0001 or abs(w.y+p['z'])>.0001 or abs(w.z-p['y'])>.0001:raise RuntimeError('Moved module '+p['id'])
for pair in pairs:
    obj=bpy.data.objects.get('SEKTOR_'+pair['owner'])
    if obj is None or len(obj.children)<100:raise RuntimeError('Missing sector '+pair['owner'])
report={'status':'PASS','blender':bpy.app.version_string,'sectors':len(pairs),'added':len(plan['added'])}
(root/'C01ShipV75_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
