"""Render real Workbench Before/After from genuine historical and current BLEND binaries.
No proxy meshes, no reexport, no edits to canonical asset meshes.
"""
import bpy, pathlib, hashlib, json
from mathutils import Vector

ROOT=pathlib.Path(__file__).resolve().parents[2]
P14=ROOT/'Assets/C01StructuralPrototypes/P14'
OLD=P14/'Pass03/Sources/C01_14_RMP-01_v002.blend'
NEW=P14/'Pass23/Native/C01_14_RMP-01_PASS23_v003.blend'
FBX=P14/'Pass23/Native/C01_14_RMP-01_PASS23_v003.fbx'
PREV=P14/'Pass26/Previews/Blender'
QA=P14/'Pass26/QA'
PREV.mkdir(parents=True,exist_ok=True)
QA.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(OLD)=='7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa'
assert sha(NEW)=='9c5a262813aeeb3a875a162008f120543c8a722ddda477e7af0f813091ec2e40'
assert sha(FBX)=='3b47d12a5a32c286c9e35a8f7198c0820d7fef5e9325823a2cfabdc12559c417'
assert OLD.read_bytes().startswith(b'BLENDER') and NEW.read_bytes().startswith(b'BLENDER')
assert FBX.read_bytes().startswith(b'Kaydara FBX Binary')

def load(path,expected_meshes,expected_triangles):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 meshes=[o for o in bpy.data.objects if o.type=='MESH']
 count=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
 assert (len(meshes),count)==(expected_meshes,expected_triangles),[path,len(meshes),count]
 assert all(len(o.data.uv_layers)>0 for o in meshes)
 for o in bpy.data.objects:
  if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
 for o in meshes:
  if o.name.startswith('COL_'):o.hide_render=True # only in unsaved render session
 return meshes

def render(stage,mode,view,camera_location,target,scale,meshes):
 scene=bpy.context.scene
 scene.render.engine='BLENDER_WORKBENCH'
 scene.render.resolution_x=1600
 scene.render.resolution_y=1000
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 scene.render.film_transparent=False
 scene.world.color=(0.04,0.045,0.055)
 shading=scene.display.shading
 shading.light='STUDIO'
 shading.color_type='OBJECT'
 shading.background_type='WORLD'
 shading.show_cavity=True
 shading.cavity_type='BOTH'
 # Workbench background render does not expose viewport wireframe overlays.
 # Use Blender's native non-destructive modifier ONLY for exact source mesh edge previews.
 modifiers=[]
 if mode=='WIREFRAME':
  for meshobj in meshes:
   mod=meshobj.modifiers.new(name='C01_PASS26_RENDER_ONLY_WIREFRAME',type='WIREFRAME')
   mod.thickness=0.0025
   mod.use_replace=True
   mod.use_even_offset=True
   modifiers.append((meshobj,mod))
 for obj in meshes:
  n=obj.name.lower()
  if 'antislip' in n:obj.color=(0.97,0.68,0.10,1.0)
  elif n.startswith('col_'):obj.color=(0.08,0.08,0.08,1.0)
  else:obj.color=(0.36,0.43,0.50,1.0)
 cam_data=bpy.data.cameras.new('C01_QA_CAMERA')
 cam=bpy.data.objects.new('C01_QA_CAMERA',cam_data)
 scene.collection.objects.link(cam)
 scene.camera=cam
 cam.location=Vector(camera_location)
 aim=Vector(target)-cam.location
 cam.rotation_euler=aim.to_track_quat('-Z','Y').to_euler()
 cam_data.type='ORTHO';cam_data.ortho_scale=scale
 cam_data.lens=50
 path=PREV/f'RMP-01_PASS26_{stage}_{view}_{mode}_REAL_BLENDER.png'
 scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 for meshobj,mod in modifiers:
  meshobj.modifiers.remove(mod)
 data=path.read_bytes()
 assert data[:8]==b'\x89PNG\r\n\x1a\n' and len(data)>15000,(path,len(data))
 bpy.data.objects.remove(cam,do_unlink=True)
 return dict(name=path.name,sha256=hashlib.sha256(data).hexdigest(),size=len(data),mode=mode,view=view,origin=stage,render_engine=scene.render.engine)

outputs=[]
for stage,path,meshes_count,tris in [('BEFORE',OLD,6,72),('AFTER',NEW,6,72)]:
 objects=load(path,meshes_count,tris)
 for mode in ['SHADED','WIREFRAME']:
  outputs.append(render(stage,mode,'FULL',(5.9,-5.2,3.2),(2.0,-0.5,0.5),5.8,objects))
  outputs.append(render(stage,mode,'STRIP01_SIDE_CLOSEUP',(0.46,-2.6,0.14),(0.46,-0.5,0.118),0.11,objects))
result={
 'status':'REAL_BLENDER_4_WORKBENCH_BEFORE_AFTER_PASS',
 'blender_version':bpy.app.version_string,
 'source_before':str(OLD.relative_to(ROOT)),'source_after':str(NEW.relative_to(ROOT)),
 'native_before_sha256':sha(OLD),'native_after_sha256':sha(NEW),
 'native_fbx_sha256':sha(FBX),
 'expected_before':{'meshes':6,'triangles':72},'expected_after':{'meshes':6,'triangles':72},
 'png_count':len(outputs),'previews':outputs,
 'scope':'C01-14 optional non-door RMP-01 outside canonical 36',
 'original_bottom_gap_m':0.0006,'repaired_bottom_embed_m':0.0004,
 'COL_RampDeck':'temporarily hidden in render only; physical native source untouched',
 'mesh_edits':'NONE; actual BLEND and FBX untouched','materials':'Workbench object display overrides ONLY; no BLEND/FBX source change',
 'unity6':'NOT RUN','independent_C01_02':'PENDING'
}
(QA/'REAL_BLENDER_PASS26_RMP_BEFORE_AFTER.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
assert len(outputs)==8
print('C01-14 PASS26 REAL WORKBENCH BEFORE_AFTER',json.dumps({'count':len(outputs),'after_blend_sha':sha(NEW),'fbx_sha':sha(FBX),'png':[p['name'] for p in outputs]}),flush=True)
