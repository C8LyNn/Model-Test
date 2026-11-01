"""C01-14 actual Blender v4 source -> .blend -> binary FBX -> Blender reimport.
Source is a losslessly encoded latest OBJ-derived RAI-01 GLB with 20 actual meshes.
Original four native Blender-v002 meshes/UVs replace their temporary GLB copies.
"""
import bpy, json, pathlib, base64, lzma, hashlib
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
for o in new:
 if not o.data.uv_layers:
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   n=p.normal;major=max(range(3),key=lambda k:abs(n[k]))
   axes=[i for i in range(3) if i!=major]
   for li in p.loop_indices:
    v=o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
    uv.data[li].uv=(float(v[axes[0]])*2,float(v[axes[1]])*2)
 if not o.data.materials:
  mat=bpy.data.materials.get('M_C01_STEEL' if ('Screw' in o.name or 'Bolt' in o.name) else 'M_C01_DARK')
  if mat is None:mat=bpy.data.materials.new(name='M_C01_STEEL' if ('Screw' in o.name or 'Bolt' in o.name) else 'M_C01_DARK')
  o.data.materials.append(mat)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
assert len(meshes)==20
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
assert actual==expected,{'actual':actual,'expected':expected}
assert all(o.data.uv_layers for o in re)
assert all(o.data.materials for o in re)
assert sum(actual.values())==424
q=dict(status='BLENDER_4_REAL_NATIVE_FBX_REIMPORT_PASS',source_origin='latest REAL OBJ-derived RAI-01 GLB; 4 originals from v002 BLEND preserve UV0',source_glb_sha256=source_sha,blender_version=bpy.app.version_string,parts=len(re),triangles=sum(actual.values()),uv_parts=sum(bool(o.data.uv_layers) for o in re),material_parts=sum(bool(o.data.materials) for o in re),original_triangles=48,new_hardware_triangles=376,part_triangle_map=actual,blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),fbx_sha256=hashlib.sha256(fbx.read_bytes()).hexdigest(),independent_C01_02='PENDING',unity6='NOT RUN')
(QA/'BLENDER_DETAIL17_REAL_EXPORT_REIMPORT.json').write_text(json.dumps(q,indent=2)+'\n')
print('C01-14 REAL BLENDER PASS17 NATIVE',json.dumps({k:v for k,v in q.items() if k!='part_triangle_map'}),flush=True)
