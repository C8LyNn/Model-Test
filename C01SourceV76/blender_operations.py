import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parent.parent
plan=json.loads((root/'Assets/C01ShipV76/Data/operations.json').read_text(encoding='utf8'))
source=bpy.data.collections['SOURCE_MODELS_editable']
def B(x,y,z):return (x,-z,y)
for model in plan['models']:
    parent=bpy.data.objects.new(model['id'],None);source.objects.link(parent);parent['sockets_json']='[]'
    for i,part in enumerate(model['parts']):
        points=list(zip(part['outline'][::2],part['outline'][1::2]));n=len(points)
        vertices=[B(x,y,z) for y in (part['y0'],part['y1']) for x,z in points]
        faces=[(0,j,j+1) for j in range(1,n-1)]+[(n,n+j+1,n+j) for j in range(1,n-1)]+[(j,n+j,n+(j+1)%n,(j+1)%n) for j in range(n)]
        mesh=bpy.data.meshes.new(model['id']+'_'+str(i));mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(bpy.data.materials[part['role']])
        child=bpy.data.objects.new(f"{model['id']}__{i:02d}_{part['role']}",mesh);source.objects.link(child);child.parent=parent
for move in plan['moves']:
    obj=bpy.data.objects.get(move['id'])
    if obj is None or obj.get('model_id')!=move['model'] or obj.get('zone')!=move['fromZone']:raise RuntimeError('Unexpected item '+move['id'])
    x,y,z,yaw=move['after'];obj.location=B(x,y,z);obj.rotation_euler.z=math.radians(yaw);obj['zone']=move['toZone']
for ident in plan['removed']:
    obj=bpy.data.objects.get(ident)
    if obj is None:raise RuntimeError('Missing wall '+ident)
    for child in list(obj.children):bpy.data.objects.remove(child,do_unlink=True)
    bpy.data.objects.remove(obj,do_unlink=True)
for p in plan['added']:
    template=bpy.data.objects.get(p['model'])
    if template is None:raise RuntimeError('Missing model '+p['model'])
    group=bpy.data.collections['DECK_0'];obj=bpy.data.objects.new(p['id'],None);group.objects.link(obj)
    obj.location=B(p['x'],p['y'],p['z']);obj.rotation_euler.z=math.radians(p['yaw'])
    obj['model_id']=p['model'];obj['zone']=p['zone'];obj['category']=p['category'];obj['gate_id']=p['gate'];obj['open_travel']=B(*p['travel'])
    for original in template.children:
        child=original.copy();child.data=original.data;group.objects.link(child);child.parent=obj;child.hide_render=True;child.hide_viewport=True
out=root/'C01SourceV76/Source/C01_Ship_Multideck_v76_base.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('Saved',out)
