import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
plan=json.loads((ROOT/'Assets/C01ShipV74/Data/pursuit.json').read_text(encoding='utf8'))
for ident in plan['removed']:
    if bpy.data.objects.get(ident) is not None:raise RuntimeError('Removed wall remains '+ident)
for p in plan['added']:
    obj=bpy.data.objects.get(p['id']);x=p['x']+(p['travel'][0] if p['category']=='GateLeaves' else 0)
    if obj is None or obj.get('model_id')!=p['model'] or not obj.children:raise RuntimeError('Missing module '+p['id'])
    if abs(obj.location.x-x)>.0001 or abs(obj.location.y+p['z'])>.0001 or abs(obj.location.z-p['y'])>.0001:
        raise RuntimeError('Wrong module position '+p['id'])
for m in plan['models']:
    obj=bpy.data.objects.get(m['id'])
    if obj is None or len(obj.children)!=len(m['parts']):raise RuntimeError('Missing reusable model '+m['id'])
report={'status':'PASS','reopened':True,'blender':bpy.app.version_string,'removed':len(plan['removed']),
        'added':len(plan['added']),'gates':len(plan['gates']),'newModels':len(plan['models'])}
(ROOT/'C01ShipV74_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
