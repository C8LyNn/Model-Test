"""Reopen the saved source and verify wall, roof and bridge assembly data."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
wall=read('Assets/C01ShipV70/Data/wall_repair.json');roof=read('Assets/C01ShipV70/Data/roof_repair.json');bridge=read('Assets/C01ShipV69/Data/bridge_layout.json')
for move in wall['moves']:
    obj=bpy.data.objects.get(move['id'])
    if obj is None or abs(obj.location.z-move['toY'])>1e-5:raise RuntimeError('Wall position '+move['id'])
for ident in wall['singleSeamWalls']:
    obj=bpy.data.objects[ident]
    if obj.get('model_id')!='W3_H3000_V70_OneSeam':raise RuntimeError('Wall variant '+ident)
    parts=[p for p in obj.children if '__01_METAL' in p.name]
    if len(parts)!=1 or parts[0].material_slots[0].material.name!='PANEL':raise RuntimeError('Wall seam '+ident)
for ident in wall['topBandFascias']:
    obj=bpy.data.objects[ident]
    if obj.get('model_id')!='W3_H400_V70_TopSeam':raise RuntimeError('Fascia variant '+ident)
    parts=[p for p in obj.children if p.type=='MESH']
    if len(parts)!=1 or [m.name for m in parts[0].data.materials]!=['PANEL','METAL']:raise RuntimeError('Fascia seam '+ident)
for item in roof['roofs']:
    obj=bpy.data.objects.get(item['id'])
    if obj is None or obj.get('model_id')!=item['variant']:raise RuntimeError('Roof '+item['id'])
    pieces=sorted((p for p in obj.children if p.type=='MESH'),key=lambda p:p.name)
    if any(abs(min(v.co.z for v in p.data.vertices)+.2)>1e-5 or abs(max(v.co.z for v in p.data.vertices)-.4)>1e-5 for p in pieces):raise RuntimeError('Roof height '+item['id'])
    source=bpy.data.objects[item['model']]
    sourceparts=sorted((p for p in source.children if p.type=='MESH'),key=lambda p:p.name)
    expected=len(sourceparts[0].data.vertices)+sum(len(c['outline']) for c in item['caps'])
    if len(pieces[0].data.vertices)!=expected:raise RuntimeError('Roof caps '+item['id'])
    variant=bpy.data.objects.get(item['variant'])
    if variant is None or {x.data for x in variant.children}!={x.data for x in pieces}:raise RuntimeError('Reusable roof '+item['id'])
for p in bridge['placements']:
    obj=bpy.data.objects.get(p['id']);expected=(p['x'],-p['z'],p['y'])
    if obj is None or any(abs(obj.location[i]-expected[i])>1e-5 for i in range(3)):raise RuntimeError('Bridge '+p['id'])
report={'status':'PASS','blender':bpy.app.version_string,'reopened':True,'wallMoves':len(wall['moves']),
        'wallSeams':len(wall['singleSeamWalls']),'fasciaSeams':len(wall['topBandFascias']),
        'roofTiles':len(roof['roofs']),'roofCaps':roof['audit']['capPolygons'],'bridgeItems':len(bridge['placements']),
        'reusableWallVariants':2,'reusableRoofVariants':len({p['variant'] for p in roof['roofs']})}
(ROOT/'C01ShipV70_QA/blender_reopened.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('C01 V7.0 BLENDER REOPEN PASS',json.dumps(report))
