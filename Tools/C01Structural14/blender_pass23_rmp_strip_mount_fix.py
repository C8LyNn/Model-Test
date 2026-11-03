"""W23 C01-14 — real native RMP-01 strip/contact correction, no proxy geometry.

Only edits bottom four existing vertices of each four existing AntiSlipMark
meshes on the actual signed v002 BLEND source. No new parts, no doors/gates.
Exact measured source gap before repair 0.0006m to real 25% deck face.
Keep visible top silhouette +0.0030m, embed bottom to -0.0004m.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Assets/C01StructuralPrototypes/P14'
OLD=BASE/'Pass03/Sources/C01_14_RMP-01_v002.blend'
OUT=BASE/'Pass23/Native'
QA=BASE/'Pass23/QA'
OUT.mkdir(parents=True,exist_ok=True)
QA.mkdir(parents=True,exist_ok=True)
BLEND=OUT/'C01_14_RMP-01_PASS23_v003.blend'
FBX=OUT/'C01_14_RMP-01_PASS23_v003.fbx'
OLD_SHA='7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa'
assert hashlib.sha256(OLD.read_bytes()).hexdigest()==OLD_SHA,'Wrong original RMP native source SHA'
assert OLD.read_bytes().startswith(b'BLENDER')
assert not BLEND.exists() and not FBX.exists(),'Never overwrite an already exported native candidate'

bpy.ops.wm.open_mainfile(filepath=str(OLD))
meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
EXPECTED={'Deck_Main','COL_RampDeck','AntiSlipMark_01','AntiSlipMark_02','AntiSlipMark_03','AntiSlipMark_04'}
assert set(meshes)==EXPECTED,sorted(meshes)
for o in meshes.values():
 assert o.data.uv_layers and o.data.materials,(o.name,'UV0/MATERIAL')
 assert len(o.data.vertices)==8 and sum(len(p.vertices)-2 for p in o.data.polygons)==12,(o.name,'SOURCE_TOPOLOGY')
assert sum(len(p.vertices)-2 for o in meshes.values() for p in o.data.polygons)==72
before={name:{
 'coordinates':[(float((o.matrix_world @ v.co)[i])) for v in o.data.vertices for i in range(3)],
 'uv':[(float(d.uv[0]),float(d.uv[1])) for d in o.data.uv_layers.active.data],
 'materials':[m.name for m in o.data.materials if m],
 'matrix':tuple(tuple(float(x) for x in row) for row in o.matrix_world)
 } for name,o in meshes.items()}
# Each original deck top surface is exactly Z=X/4 across X 0..4.
deck=meshes['Deck_Main']
dv=[deck.matrix_world @ v.co for v in deck.data.vertices]
assert abs(max(float(p.x) for p in dv)-4)<1e-5 and abs(min(float(p.x) for p in dv))<1e-5
assert abs(max(float(p.y) for p in dv)-0)<1e-5 and abs(min(float(p.y) for p in dv)+1)<1e-5
assert sorted(round(float(p.z-p.x*.25),5) for p in dv)==[-.2]*4+[0.0]*4
proxy=meshes['COL_RampDeck']
assert sorted(tuple(round(float(x),7) for x in proxy.matrix_world @ v.co) for v in proxy.data.vertices)==sorted(tuple(round(float(x),7) for x in dv)
# Directly change only the 16 real *bottom* strip vertices. No top vertices moved.
witness=[]
for i in range(1,5):
 name=f'AntiSlipMark_{i:02d}'
 o=meshes[name];invm=o.matrix_world.inverted()
 changes=0;pre=[]
 for v in o.data.vertices:
  original=o.matrix_world @ v.co
  gap=float(original.z-original.x*.25)
  pre.append(gap)
  if abs(gap-.0006)<2e-5:
   world=original+Vector((0,0,-.0010))
   v.co=invm @ world
   changes+=1
  else:
   assert abs(gap-.0030)<2e-5,(name,'unexpected top silhouette',gap)
 assert changes==4,(name,'expected 4 bottom and 4 top')
 o.data.update()
 after_gaps=sorted(float((o.matrix_world @ v.co).z-(o.matrix_world @ v.co).x*.25) for v in o.data.vertices)
 assert all(abs(x-(-.0004 if k<4 else .003))<2e-5 for k,x in enumerate(after_gaps)),(name,after_gaps)
 assert [(float(d.uv[0]),float(d.uv[1])) for d in o.data.uv_layers.active.data]==before[name]['uv']
 assert [m.name for m in o.data.materials if m]==before[name]['materials']
 assert tuple(tuple(float(x) for x in row) for row in o.matrix_world)==before[name]['matrix']
 witness.append({'name':name,'original_gap_m':.0006,'bottom_embed_after_m':.0004,
                 'top_above_deck_unchanged_m':.003,'exact_vertices_changed':changes})
assert sum(v['exact_vertices_changed'] for v in witness)==16

for name in ['Deck_Main','COL_RampDeck']:
 o=meshes[name]
 assert [(float((o.matrix_world @ v.co)[i])) for v in o.data.vertices for i in range(3)]==before[name]['coordinates'],'Deck/collider modified'
 assert [(float(d.uv[0]),float(d.uv[1])) for d in o.data.uv_layers.active.data]==before[name]['uv']
 assert [m.name for m in o.data.materials if m]==before[name]['materials']
 assert tuple(tuple(float(x) for x in row) for row in o.matrix_world)==before[name]['matrix']

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.object.select_all(action='DESELECT')
for o in meshes.values():o.select_set(True)
bpy.context.view_layer.objects.active=deck
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'MESH'},
                         add_leaf_bones=False,mesh_smooth_type='FACE',use_mesh_modifiers=False,
                         axis_forward='-Z',axis_up='Y')
assert BLEND.read_bytes()[:7]==b'BLENDER'
assert FBX.read_bytes().startswith(b'Kaydara FBX Binary')

def space(o):return sorted(tuple(round(float(w),5) for w in o.matrix_world @ v.co) for v in o.data.vertices)
actual_before={name:space(o) for name,o in meshes.items()}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FBX))
imported={o.name[:-5] if o.name.endswith('_Mesh') else o.name:o for o in bpy.data.objects if o.type=='MESH'}
assert set(imported)==EXPECTED,sorted(imported)
assert sum(len(p.vertices)-2 for o in imported.values() for p in o.data.polygons)==72
assert all(o.data.uv_layers and o.data.materials for o in imported.values())
for name,o in imported.items():
 assert space(o)==actual_before[name],(name,'FBX world vertex parity')
 if name.startswith('AntiSlipMark_'):
  residual=sorted(float((o.matrix_world @ v.co).z-(o.matrix_world @ v.co).x*.25) for v in o.data.vertices)
  assert all(abs(x-(-.0004 if k<4 else .003))<2e-5 for k,x in enumerate(residual)),(name,residual)
report={
 'status':'REAL_NATIVE_RMP23_BLENDER_SAVE_EXPORT_REIMPORT_PASS',
 'owner':'C01-14','asset':'existing RMP-01 only, optional outside 36','doors_untouched':True,
 'blender_version':bpy.app.version_string,'input_sha256':OLD_SHA,
 'input_static_defect':'four real antislip strips floating 0.0006m above deck; 0 contact',
 'change':'exactly 16 existing bottom vertex positions -0.001m Z; no top/silhouette, deck/proxy, UV, materials or pivot changes',
 'parts':len(imported),'triangles':72,'strip_contact_count':4,
 'bottom_embed_m':.0004,'top_protrusion_m':.003,
 'witnesses':witness,
 'blend_sha256':hashlib.sha256(BLEND.read_bytes()).hexdigest(),
 'fbx_sha256':hashlib.sha256(FBX.read_bytes()).hexdigest(),
 'native_reimport_mesh_vertex_parity_at_1e-5m':'PASS',
 'independent_C01_02':'PENDING','unity6':'NOT RUN','release':'HOLD'}
(QA/'RMP-01_PASS23_NATIVE_CONTACT_QA.json').write_text(json.dumps(report,indent=2)+'\n')
print('C01-14 REAL W23 RMP-01 SOURCE NATIVE',json.dumps(report),flush=True)
