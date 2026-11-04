import bpy
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV76/Data/operations.json').read_text(encoding='utf8'))
for move in plan['moves']:
    obj=bpy.data.objects.get(move['id']);x,y,z,yaw=move['after']
    if obj is None or obj.get('zone')!=move['toZone'] or abs(obj.location.x-x)>.0001 or abs(obj.location.y+z)>.0001 or abs(obj.location.z-y)>.0001:raise RuntimeError('Wrong move '+move['id'])
for p in plan['added']:
    obj=bpy.data.objects.get(p['id'])
    if obj is None or not obj.children or obj.get('model_id')!=p['model']:raise RuntimeError('Missing module '+p['id'])
    if abs(obj.location.x-p['x'])>.0001 or abs(obj.location.y+p['z'])>.0001 or abs(obj.location.z-p['y'])>.0001:raise RuntimeError('Moved module '+p['id'])
for ident in plan['removed']:
    if bpy.data.objects.get(ident) is not None:raise RuntimeError('Removed wall remains '+ident)
report={'status':'PASS','blender':bpy.app.version_string,'moved':len(plan['moves']),'added':len(plan['added']),'newModels':len(plan['models'])}
(root/'C01ShipV76_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
