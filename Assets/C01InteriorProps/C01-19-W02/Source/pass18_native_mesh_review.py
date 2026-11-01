"""PASS18 true Blender4 P19-07 QA-only. NEVER modifies producer model."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
MID='P19-07';src=ROOT/'Models'/MID/(MID+'.blend');fbx=ROOT/'Models'/MID/(MID+'.fbx')
out=ROOT/'QA'/'PASS18'/MID;out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert src.read_bytes().startswith(b'BLENDER-v400')
assert fbx.read_bytes().startswith(b'Kaydara FBX Binary  \x00\x1a\x00')
bpy.ops.wm.open_mainfile(filepath=str(src))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objs)==6
parts=[];tj=[]
for o in objs:
 bm=bmesh.new();bm.from_mesh(o.data)
 boundary=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-14 for f in bm.faces)
 near=sum(1e-14<=f.calc_area()<1e-10 for f in bm.faces)
 assert boundary==0 and zero==0 and o.data.uv_layers,(o.name,boundary,zero)
 world=[o.matrix_world@v.co for v in o.data.vertices]
 for e in o.data.edges:
  a=world[e.vertices[0]];d=world[e.vertices[1]]-a;dd=d.length_squared
  if dd<1e-14:continue
  for i,p in enumerate(world):
   if i in e.vertices:continue
   t=(p-a).dot(d)/dd
   if 1e-5<t<1-1e-5:
    dist=(p-a-t*d).length
    if dist<2e-7:tj.append({'mesh':o.name,'edge':list(e.vertices),'vertex':i,'fraction':round(t,8),'distance_m':dist,'world_xyz':[round(float(x),7) for x in p]})
 parts.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'manifold_bad_edges':boundary,'zero_area_faces':zero,'micro_slivers':near,'uv0':True})
 bm.free()
assert sum(p['triangles'] for p in parts)==252
def shot(filename,wire=False,close=False):
 sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH'
 sc.render.resolution_x=1050;sc.render.resolution_y=780;sc.render.resolution_percentage=100
 old=sc.camera;states=[(o,o.show_wire,o.show_all_edges) for o in objs]
 for o in objs:o.show_wire=wire;o.show_all_edges=wire
 xyz=[o.matrix_world@v.co for o in objs for v in o.data.vertices]
 lo=Vector([min(v[i] for v in xyz) for i in range(3)]);hi=Vector([max(v[i] for v in xyz) for i in range(3)])
 mid=(lo+hi)*.5;span=max((hi-lo).length,.5)
 if close and tj:mid=Vector(tj[0]['world_xyz']);span=.32
 cd=bpy.data.cameras.new('PASS18_TEST_CAM');cam=bpy.data.objects.new('PASS18_TEST_CAM',cd)
 bpy.context.collection.objects.link(cam)
 cam.location=mid+Vector((span*1.4,-span*1.6,span*1.2))
 cam.rotation_euler=(mid-cam.location).to_track_quat('-Z','Y').to_euler()
 cd.type='ORTHO';cd.ortho_scale=span*1.75;sc.camera=cam
 sc.render.filepath=str(out/filename);sc.render.image_settings.file_format='PNG'
 try:bpy.ops.render.render(write_still=True)
 finally:
  sc.camera=old;bpy.data.objects.remove(cam,do_unlink=True)
  for o,w,e in states:o.show_wire=w;o.show_all_edges=e
shot('P19-07_PASS18_REAL_SHADED.png')
shot('P19-07_PASS18_REAL_WIREFRAME.png',wire=True)
shot('P19-07_PASS18_REAL_TJ_CLOSEUP.png',wire=True,close=True)
original=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(fbx))
new=[o for o in bpy.context.scene.objects if o not in original]
models=[o for o in new if o.type=='MESH']
rt={'objects':len(models),'triangles':sum(max(0,len(p.vertices)-2) for o in models for p in o.data.polygons),'uv0_parts':sum(bool(o.data.uv_layers) for o in models)}
assert rt=={'objects':6,'triangles':252,'uv0_parts':6},rt
for o in new:bpy.data.objects.remove(o,do_unlink=True)
data={'id':MID,'Blender_version':bpy.app.version_string,'blend_sha256':sha(src),'fbx_sha256':sha(fbx),'parts':parts,'tj_candidates':tj,'tj_count':len(tj),'FBX_4x_reimport':rt,'screenshots':['P19-07_PASS18_REAL_SHADED.png','P19-07_PASS18_REAL_WIREFRAME.png','P19-07_PASS18_REAL_TJ_CLOSEUP.png'],'interpretation':'Vertex-on-edge proximity is NOT by itself a proven z-fight or a reason to weld. HOLD final geometry approval until independent C01-02 validates.','source_geometry_modified':False,'C01_02':'PENDING','Unity_6_URP':'NOT_RUN'}
(out/'P19-07_PASS18_REAL_BLENDER_REVIEW.json').write_text(json.dumps(data,indent=2))
print('PASS18_REAL_BLENDER_QA_SUCCESS',len(tj),sha(src),sha(fbx),flush=True)
