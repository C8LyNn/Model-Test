"""Apply the same wall positions and roof plan to the editable v6.9 Blender assembly."""
import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
wall=json.loads((ROOT/'Assets/C01ShipV70/Data/wall_repair.json').read_text(encoding='utf8'))
roof=json.loads((ROOT/'Assets/C01ShipV70/Data/roof_repair.json').read_text(encoding='utf8'))
panel=bpy.data.materials['PANEL'];metal=bpy.data.materials['METAL'];hull=bpy.data.materials['HULL']
source_collection=bpy.data.collections['SOURCE_MODELS_editable']
def register_variant(variant,sample):
    if bpy.data.objects.get(variant) is not None:return
    parent=bpy.data.objects.new(variant,None);source_collection.objects.link(parent)
    parent['sockets_json']='[]'
    for index,part in enumerate(sorted((p for p in sample.children if p.type=='MESH'),key=lambda p:p.name)):
        child=part.copy();child.data=part.data;child.name=f'{variant}__{index:02d}'
        child.hide_render=False;child.hide_viewport=False;source_collection.objects.link(child);child.parent=parent
for move in wall['moves']:
    obj=bpy.data.objects.get(move['id'])
    if obj is None or abs(obj.location.z-move['fromY'])>1e-5:raise RuntimeError('Incorrect original position '+move['id'])
    obj.location.z=move['toY']
for ident in wall['singleSeamWalls']:
    obj=bpy.data.objects[ident]
    parts=[p for p in obj.children if '__01_METAL' in p.name]
    if len(parts)!=1:raise RuntimeError('Missing upper wall trim '+ident)
    part=parts[0];part.material_slots[0].link='OBJECT';part.material_slots[0].material=panel
    obj['model_id']='W3_H3000_V70_OneSeam';register_variant(obj['model_id'],obj)

def box_mesh(name,lo,hi,top):
    # Each box is expressed in Blender coordinates (Unity z is negated).
    verts=[];faces=[];indices=[]
    for z0,z1,material in ((lo,top,0),(top,hi,1)):
        offset=len(verts);verts += [(.15,.15,z0),(2.85,.15,z0),(2.85,-.15,z0),(.15,-.15,z0),
                                    (.15,.15,z1),(2.85,.15,z1),(2.85,-.15,z1),(.15,-.15,z1)]
        faces += [tuple(offset+i for i in f) for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0))]
        indices += [material]*6
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(panel);mesh.materials.append(metal)
    for p,i in zip(mesh.polygons,indices):p.material_index=i
    mesh.update();return mesh
fascia_mesh=box_mesh('V70_fascia_top_band',0,.4,.34)
for ident in wall['topBandFascias']:
    obj=bpy.data.objects[ident];parts=[p for p in obj.children if p.type=='MESH']
    if len(parts)!=1:raise RuntimeError('Unexpected fascia geometry '+ident)
    parts[0].data=fascia_mesh;obj['model_id']='W3_H400_V70_TopSeam';register_variant(obj['model_id'],obj)

extended={};combined={}
def extend(mesh):
    if mesh not in extended:
        new=mesh.copy();new.name='V70_roof_'+mesh.name
        for vertex in new.vertices:
            if vertex.co.z>-.00001:vertex.co.z+=.4
        new.update();extended[mesh]=new
    return extended[mesh]
def combine(mesh,caps):
    if not caps:return mesh
    key=(mesh.name,tuple(tuple(c['outline']) for c in caps))
    if key in combined:return combined[key]
    vertices=[tuple(v.co) for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
    for cap in caps:
        outline=cap['outline'];poly=list(zip(outline[::2],outline[1::2]));n=len(poly);offset=len(vertices)
        vertices += [(x,-z,y) for y in (.2,.4) for x,z in poly]
        faces += [tuple(offset+i for i in (0,k,k+1)) for k in range(1,n-1)]
        faces += [tuple(offset+i for i in (n,n+k+1,n+k)) for k in range(1,n-1)]
        faces += [tuple(offset+i for i in (k,n+k,n+(k+1)%n,(k+1)%n)) for k in range(n)]
    result=bpy.data.meshes.new('V70_roof_complete');result.from_pydata(vertices,[],faces);result.materials.append(hull);result.update();combined[key]=result;return result

for item in roof['roofs']:
    obj=bpy.data.objects.get(item['id'])
    if obj is None or obj.get('model_id')!=item['model']:raise RuntimeError('Missing roof '+item['id'])
    pieces=sorted((p for p in obj.children if p.type=='MESH'),key=lambda p:p.name)
    if not pieces:raise RuntimeError('Empty roof '+item['id'])
    for i,piece in enumerate(pieces):piece.data=combine(extend(piece.data),item['caps'] if i==0 else [])
    obj['model_id']=item['variant'];register_variant(obj['model_id'],obj)

out=ROOT/'C01SourceV70/Source/C01_Ship_Multideck_v70_base.blend';out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
report={'status':'PASS','blender':bpy.app.version_string,'moves':len(wall['moves']),
        'wallSeams':len(wall['singleSeamWalls']),'roofTiles':len(roof['roofs']),
        'roofCaps':roof['audit']['capPolygons'],'source':out.name}
(ROOT/'C01ShipV70_QA/blender_build.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('C01 V7.0 BLENDER PASS',json.dumps(report))
