"""Check the saved Blender file after reopening it in a fresh process."""
import bpy
import json
from pathlib import Path

root=Path(__file__).resolve().parent.parent
layout=json.loads((root/'Assets/C01ShipV69/Data/bridge_layout.json').read_text(encoding='utf8'))
for p in layout['placements']:
    obj=bpy.data.objects.get(p['id'])
    if obj is None or obj.get('model_id')!=p['model']:raise RuntimeError('Missing '+p['id'])
    expected=(p['x'],-p['z'],p['y'])
    if any(abs(obj.location[i]-expected[i])>1e-5 for i in range(3)):raise RuntimeError('Position: '+p['id'])
    source=bpy.data.objects.get(p['model'])
    if source is None or {x.data for x in obj.children}!={x.data for x in source.children}:
        raise RuntimeError('Source mesh differs: '+p['id'])
report={'status':'PASS','blender':bpy.app.version_string,'reopened':True,'positions_checked':len(layout['placements']),
        'shared_model_meshes':'PASS','source_file':Path(bpy.data.filepath).name}
(root/'C01ShipV69_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('C01 V6.9 BLENDER REOPEN PASS')
