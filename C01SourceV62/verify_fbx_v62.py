"""Round-trip each v6.2 exported FBX through Blender and compare dimensions."""
import bpy
import json
from pathlib import Path

source=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(source/'C01_Ship_v62_NewModules.blend'))
errors=[]
checked=[]

def dimensions(objects):
    points=[obj.matrix_world @ vertex.co for obj in objects if obj.type=='MESH' for vertex in obj.data.vertices]
    if not points: raise RuntimeError('Imported FBX has no mesh vertices')
    return [max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]

for path in sorted((source/'Models').glob('*.fbx')):
    original=bpy.data.objects.get(path.stem)
    if original is None:
        errors.append(path.name+': missing source');continue
    expected=dimensions([original])
    existing=set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path))
    imported=[obj for obj in bpy.data.objects if obj not in existing]
    actual=dimensions(imported)
    if any(abs(a-b)>.002 for a,b in zip(actual,expected)):
        errors.append(f'{path.name}: expected {expected}, got {actual}')
    checked.append(dict(file=path.name,expected=expected,actual=actual))
    for obj in imported: bpy.data.objects.remove(obj,do_unlink=True)

report={'status':'PASS' if checked and not errors else 'FAIL','checked':len(checked),'errors':errors,'models':checked}
(source/'fbx_roundtrip_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('C01 V62 FBX ROUNDTRIP',report['status'],'count',len(checked),'errors',len(errors))
if errors or not checked: raise SystemExit(1)
