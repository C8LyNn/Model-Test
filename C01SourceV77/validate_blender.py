import bpy
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV77/Data/two_decks.json').read_text(encoding='utf8'))
old=bpy.data.collections.get('DECK_0')
if old is not None and len(old.objects):raise RuntimeError('Deck zero collection is not empty')
for m in plan['moves']:
    obj=bpy.data.objects.get(m['newId']);x,y,z,yaw=m['after']
    if obj is None or obj.get('zone')!=m['zone'] or abs(obj.location.x-x)>.0001 or abs(obj.location.y+z)>.0001 or abs(obj.location.z-y)>.0001:raise RuntimeError('Wrong move '+m['newId'])
for p in plan['added']:
    obj=bpy.data.objects.get(p['id'])
    if obj is None or not obj.children or obj.get('model_id')!=p['model']:raise RuntimeError('Missing '+p['id'])
    if abs(obj.location.x-p['x'])>.0001 or abs(obj.location.y+p['z'])>.0001 or abs(obj.location.z-p['y'])>.0001:raise RuntimeError('Moved '+p['id'])
for ident in plan['removed']:
    if bpy.data.objects.get(ident) is not None:raise RuntimeError('Removed object remains '+ident)
report={'status':'PASS','blender':bpy.app.version_string,'removed':len(plan['removed']),'transferred':len(plan['moves']),'added':len(plan['added'])}
(root/'C01ShipV77_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
