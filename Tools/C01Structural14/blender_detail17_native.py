"""C01-14 actual Blender v4 source -> .blend -> binary FBX -> Blender reimport.
Source is a losslessly encoded latest OBJ-derived RAI-01 GLB with 20 actual meshes.
Original four native Blender-v002 meshes/UVs replace their temporary GLB copies.
"""
import bpy, json, pathlib, base64, lzma, hashlib
from mathutils import Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
P14=ROOT/'Assets/C01StructuralPrototypes/P14'
SRC=P14/'Pass17/Source/RAI-01_REAL_SOURCE_GLB.xz.b64'
LEG=P14/'Pass03/Sources/C01_14_RAI-01_v002.blend'
DST=P14/'Pass17/Native'
QA=P14/'Pass17/QA'
DST.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
bin_glb=lzma.decompress(base64.b64decode(SRC.read_text().strip()))
source_sha=hashlib.sha256(bin_glb).hexdigest()
assert source_sha=='cd22f9e879e098fbfa41c9c9a29eedf9e2b99eccc95d72e7a5029e6e478c120e',source_sha
assert bin_glb[:4]==b'glTF'
original_names={'TopRail','MiddleRail','Post_Start','Post_End'}
bpy.ops.wm.open_mainfile(filepath=str(LEG))
old=[o for o in bpy.data.objects if o.type=='MESH']
assert len(old)==4,[(o.name,o.type) for o in old]
assert sum(len(p.vertices)-2 for o in old for p in o.data.polygons)==48
assert all(bool(o.data.uv_layers) for o in old)
for o in old:
 if o.name.endswith('_Mesh'):o.name=o.name[:-5]
assert set(o.name for o in old)==original_names,[o.name for o in old]
tmp=DST/'source-real.glb';tmp.write_bytes(bin_glb)
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(tmp))
imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
assert len(imported)==20,[(o.name,o.type) for o in imported]
assert sum(len(p.vertices)-2 for o in imported for p in o.data.polygons)==424
new=[]
for o in imported:
 if o.name.split('.')[0] in original_names:
  bpy.data.objects.remove(o,do_unlink=True)
 else:new.append(o)
assert len(new)==16,[o.name for o in new]
assert sum(len(p.vertices)-2 for o in new for p in o.data.polygons)==376
# glTF is Y-up, authored OBJ and our original BLEND are Z-up.
# Convert imported GLB world positions back from (x,-z,y) to original (x,y,z).
for o in new:
 o.matrix_world=Matrix.Rotation(-1.5707963267948966,4,'X') @ o.matrix_world
for o in new:
 if not o.data.uv_layers:
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   pts=[o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co for li in p.loop_indices]
   n=(pts[1]-pts[0]).cross(pts[2]-pts[0])
   major=max(range(3),key=lambda k:abs(n[k]))
   axes=[i for i in range(3) if i!=major]
   for li,v in zip(p.loop_indices,pts):
    uv.data[li].uv=(float(v[axes[0]])*2,float(v[axes[1]])*2)
 if not o.data.materials:
  mat=bpy.data.materials.get('M_C01_STEEL' if ('Screw' in o.name or 'Bolt' in o.name) else 'M_C01_DARK')
  if mat is None:mat=bpy.data.materials.new(name='M_C01_STEEL' if ('Screw' in o.name or 'Bolt' in o.name) else 'M_C01_DARK')
  o.data.materials.append(mat)
SOURCE_BOUNDS={"BaseSocket_A":[[0.05,-0.05,0.012],[0.15,0.05,0.132]],"BaseSocket_B":[[1.85,-0.05,0.012],[1.95,0.05,0.132]],"FootBolt_A_L":[[0.025,-0.009,0.01],[0.043,0.009,0.02]],"FootBolt_A_R":[[0.157,-0.009,0.01],[0.175,0.009,0.02]],"FootBolt_B_L":[[1.825,-0.009,0.01],[1.843,0.009,0.02]],"FootBolt_B_R":[[1.957,-0.009,0.01],[1.975,0.009,0.02]],"Footplate_A":[[0.02,-0.07,0.002],[0.18,0.07,0.014]],"Footplate_B":[[1.82,-0.07,0.002],[1.98,0.07,0.014]],"MidJointCollar_A_Far":[[0.036,0.038,0.436],[0.164,0.05,0.522]],"MidJointCollar_A_Near":[[0.036,-0.05,0.436],[0.164,-0.038,0.522]],"MidJointCollar_B_Far":[[1.836,0.038,0.436],[1.964,0.05,0.522]],"MidJointCollar_B_Near":[[1.836,-0.05,0.436],[1.964,-0.038,0.522]],"MiddleRail":[[0,-0.035,0.45],[2,0.035,0.51]],"Post_End":[[1.86,-0.04,0],[1.94,0.04,1.05]],"Post_Start":[[0.06,-0.04,0],[0.14,0.04,1.05]],"SocketSetScrew_A_1":[[0.0925,0.037,0.0495],[0.1075,0.06,0.0645]],"SocketSetScrew_A_2":[[0.0925,0.037,0.0945],[0.1075,0.06,0.1095]],"SocketSetScrew_B_1":[[1.8925,0.037,0.0495],[1.9075,0.06,0.0645]],"SocketSetScrew_B_2":[[1.8925,0.037,0.0945],[1.9075,0.06,0.1095]],"TopRail":[[0,-0.05,1.02],[2,0.05,1.1]]}
def assert_exact_world_bounds(objs,stage):
 seen=set()
 for o in objs:
  seen.add(o.name)
  pts=[o.matrix_world @ v.co for v in o.data.vertices]
  assert pts, (stage,o.name,'empty')
  actual=[[min(float(p[k]) for p in pts) for k in range(3)],[max(float(p[k]) for p in pts) for k in range(3)]]
  expected=SOURCE_BOUNDS[o.name]
  assert all(abs(actual[j][k]-expected[j][k])<=0.00001 for j in range(2) for k in range(3)),(stage,o.name,expected,actual)
 assert seen==set(SOURCE_BOUNDS),(stage,sorted(seen^set(SOURCE_BOUNDS)))

def assert_no_degenerate_uv0(objs,stage):
 bad=[]
 for o in objs:
  assert o.data.uv_layers,(stage,o.name,'NO_UV0')
  layer=o.data.uv_layers.active.data
  for p in o.data.polygons:
   assert len(p.loop_indices)==3,(stage,o.name,'NOT_TRIANGULATED')
   uv=[layer[i].uv for i in p.loop_indices]
   cross=(uv[1][0]-uv[0][0])*(uv[2][1]-uv[0][1])-(uv[1][1]-uv[0][1])*(uv[2][0]-uv[0][0])
   if abs(cross)<1e-10:bad.append((o.name,p.index))
 assert not bad,(stage,'DEGENERATE_UV0_TRIANGLES',bad[:25],len(bad))

meshes=[o for o in bpy.data.objects if o.type=='MESH']
assert len(meshes)==20
assert_exact_world_bounds(meshes,'PRE_EXPORT')
assert_no_degenerate_uv0(meshes,'PRE_EXPORT')
assert sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)==424
assert all(o.data.uv_layers for o in meshes)
assert all(o.data.materials for o in meshes)
blend=DST/'C01_14_RAI-01_DETAIL17.blend'
fbx=DST/'C01_14_RAI-01_DETAIL17.fbx'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},add_leaf_bones=False,mesh_smooth_type='FACE',use_mesh_modifiers=False,axis_forward='-Z',axis_up='Y')
assert blend.read_bytes()[:7]==b'BLENDER'
assert fbx.read_bytes().startswith(b'Kaydara FBX Binary')
expected={o.name:sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(fbx))
re=[o for o in bpy.data.objects if o.type=='MESH']
actual={o.name:sum(len(p.vertices)-2 for p in o.data.polygons) for o in re}
assert_exact_world_bounds(re,'FBX_REIMPORT')
assert_no_degenerate_uv0(re,'FBX_REIMPORT')
assert actual==expected,{'actual':actual,'expected':expected}
assert all(o.data.uv_layers for o in re)
assert all(o.data.materials for o in re)
assert sum(actual.values())==424
q=dict(status='BLENDER_4_REAL_NATIVE_FBX_REIMPORT_PASS',source_origin='latest REAL OBJ-derived RAI-01 GLB; 4 originals from v002 BLEND preserve UV0',source_glb_sha256=source_sha,blender_version=bpy.app.version_string,parts=len(re),triangles=sum(actual.values()),uv_parts=sum(bool(o.data.uv_layers) for o in re),material_parts=sum(bool(o.data.materials) for o in re),original_triangles=48,new_hardware_triangles=376,part_triangle_map=actual,blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),fbx_sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),independent_C01_02='PENDING',unity6='NOT RUN')
(QA/'BLENDER_DETAIL17_REAL_EXPORT_REIMPORT.json').write_text(json.dumps(q,indent=2)+'\n')
print('C01-14 REAL BLENDER PASS17 NATIVE',json.dumps({k:v for k,v in q.items() if k!='part_triangle_map'}),flush=True)
