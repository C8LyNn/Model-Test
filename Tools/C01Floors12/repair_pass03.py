"""C01-12 PASS03: audit originals from v002 .blend and repair only confirmed UV defects.
All previews are Blender renders of the actual loaded mesh/edges; no procedural rebuild.
"""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'C01StandaloneKits'/'FloorCeiling'
OUT=ROOT/'RepairPass03'
for sub in ('Blend','FBX','QA','Previews'):(OUT/sub).mkdir(parents=True,exist_ok=True)
STEMS={'F01':'C01_SHI_F01_FLOOR_BASIC','F02':'C01_SHI_F02_FLOOR_MARKED','C01':'C01_SHI_C01_CEILING_BASIC'}
EPS=1e-8

def uv_area(coords):
 return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:]+coords[:1])))/2.

def topology(mesh):
 mesh.calc_loop_triangles()
 verts=[v.co.copy() for v in mesh.vertices]
 faces=[list(p.vertices) for p in mesh.polygons]
 edges=[tuple(e.vertices) for e in mesh.edges]
 incidence={tuple(sorted(e)):[] for e in edges}
 used=[0]*len(verts)
 for e in edges:
  for i in e: used[i]+=1
 for fi,face in enumerate(faces):
  for i in range(len(face)):
   incidence.setdefault(tuple(sorted((face[i],face[(i+1)%len(face)]))),[]).append(fi)
 seen={};duplicate_verts=[]
 for i,v in enumerate(verts):
  key=tuple(round(float(x),8) for x in v)
  if key in seen: duplicate_verts.append([seen[key],i])
  else: seen[key]=i
 seenfaces={}; duplicate_faces=[]
 for fi,face in enumerate(faces):
  key=tuple(sorted(face))
  if key in seenfaces:duplicate_faces.append([seenfaces[key],fi])
  else:seenfaces[key]=fi
 winding=[]
 for e,neighbors in incidence.items():
  if len(neighbors)!=2:continue
  dirs=[]
  for fi in neighbors:
   face=faces[fi]
   pairs=[(face[i],face[(i+1)%len(face)]) for i in range(len(face))]
   dirs.extend([pair for pair in pairs if set(pair)==set(e)])
  if len(dirs)==2 and dirs[0]==dirs[1]:winding.append(list(e))
 tj=[]
 for vi,point in enumerate(verts):
  for ei,(a,b) in enumerate(edges):
   if vi in (a,b):continue
   direction=verts[b]-verts[a]
   l2=direction.length_squared
   if l2<1e-16:continue
   t=(point-verts[a]).dot(direction)/l2
   if 1e-7<t<1-1e-7 and (verts[a]+t*direction-point).length<EPS:tj.append([vi,ei])
 uv=mesh.uv_layers.active
 collapsed=[]
 if uv is not None:
  for p in mesh.polygons:
   points=[tuple(uv.data[i].uv) for i in p.loop_indices]
   if uv_area(points)<EPS:collapsed.append(p.index)
 bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False,epsilon=0)
 pairs=set()
 if bvh is not None:
  for a,b in bvh.overlap(bvh):
   if a<b and not set(faces[a]).intersection(faces[b]):pairs.add((a,b))
 volume=sum(verts[t.vertices[0]].dot(verts[t.vertices[1]].cross(verts[t.vertices[2]]))/6 for t in mesh.loop_triangles)
 return {'vertices':len(verts),'edges':len(edges),'faces':len(faces),'triangles':sum(len(f)-2 for f in faces),
  'loose_vertices':[i for i,val in enumerate(used) if val==0],
  'loose_edges':[list(e) for e,n in incidence.items() if not n],
  'duplicate_vertex_positions':duplicate_verts,
  'zero_length_edges':[i for i,(a,b) in enumerate(edges) if (verts[a]-verts[b]).length<EPS],
  'degenerate_faces':[p.index for p in mesh.polygons if p.area<EPS],
  'duplicate_faces':duplicate_faces,
  'boundary_edges':[list(e) for e,n in incidence.items() if len(n)==1],
  'nonmanifold_edges':[list(e) for e,n in incidence.items() if len(n)>2],
  'same_direction_shared_edges':winding,'t_junction_candidates':tj,
  'bvh_nonadjacent_overlap_candidates':[list(x) for x in sorted(pairs)],
  'collapsed_uv_faces':collapsed,'missing_uv0':uv is None,
  'signed_volume_m3':volume,
  'bounds_blender_xyz':[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]]}

def validate(a,model,phase):
 mandatory_zero=['loose_vertices','loose_edges','duplicate_vertex_positions','zero_length_edges','degenerate_faces',
 'duplicate_faces','boundary_edges','nonmanifold_edges','same_direction_shared_edges','t_junction_candidates','bvh_nonadjacent_overlap_candidates']
 defects={k:a[k] for k in mandatory_zero if a[k]}
 assert not defects,(model,phase,defects)
 assert not a['missing_uv0'],(model,phase,'UV missing')
 assert (a['vertices'],a['edges'],a['faces'],a['triangles'])==(16,28,14,28),(model,phase,a)
 assert abs(a['signed_volume_m3']-0.2)<1e-6,(model,phase,'volume',a['signed_volume_m3'])

def screenshot(obj,id,mode,wire=False,zoom=False):
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
 scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT'
 scene.display.shading.show_shadows=True
 z=3.1 if id=='C01' else -.1
 target=Vector((0,-.5,z)) if zoom else Vector((.5,-.5,z))
 camera=bpy.data.objects.new('QA_TEMP_CAMERA',bpy.data.cameras.new('QA_TEMP_CAMERA'))
 scene.collection.objects.link(camera);scene.camera=camera
 camera.location=target+Vector((-1.8,-1.5,.8) if zoom else (1.8,-2.8,2.2))
 camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.data.type='ORTHO';camera.data.ortho_scale=.82 if zoom else 2.45
 # Edges originate from the real existing mesh, not reconstructed geometry.
 curves=bpy.data.curves.new('QA_TRUE_EDGES','CURVE');curves.dimensions='3D'
 curves.bevel_depth=.003 if zoom else .0025
 for e in obj.data.edges:
  poly=curves.splines.new('POLY');poly.points.add(1)
  for j,vertex_index in enumerate(e.vertices):
   v=obj.data.vertices[vertex_index].co
   poly.points[j].co=(v.x,v.y,v.z,1)
 overlay=bpy.data.objects.new('QA_TRUE_EDGES',curves)
 scene.collection.objects.link(overlay)
 overlay.color=(.96,.55,.12,1) if wire else (.06,.06,.06,1)
 origcolor=tuple(obj.color);obj.color=(.42,.48,.54,1)
 obj.hide_render=wire
 filename=OUT/'Previews'/f'{id}_{mode}.png'
 scene.render.filepath=str(filename)
 bpy.ops.render.render(write_still=True)
 obj.hide_render=False;obj.color=origcolor
 bpy.data.objects.remove(overlay,do_unlink=True)
 bpy.data.objects.remove(camera,do_unlink=True)
 return str(filename.relative_to(OUT))

def one(id,stem):
 original=ROOT/'Blend'/f'{stem}_v002.blend'
 assert original.is_file(),original
 bpy.ops.wm.open_mainfile(filepath=str(original))
 objects=[o for o in bpy.data.objects if o.type=='MESH']
 assert len(objects)==1,(id,len(objects))
 obj=objects[0];mesh=obj.data
 assert tuple(round(float(x),8) for x in obj.location)==(0,0,0)
 assert tuple(round(float(x),8) for x in obj.scale)==(1,1,1)
 before=topology(mesh);validate(before,id,'before')
 endcaps=[p.index for p in mesh.polygons if abs(p.normal.x)>.9]
 assert sorted(endcaps)==sorted(before['collapsed_uv_faces']) and len(endcaps)==2,(id,endcaps,before['collapsed_uv_faces'])
 previews={'wireframe_before':screenshot(obj,id,'BEFORE_WIREFRAME',wire=True)}
 uv=mesh.uv_layers.active
 for i in endcaps:
  for li in mesh.polygons[i].loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(p.y,p.z) # local YZ projection of the X-normal end caps
 after=topology(mesh);validate(after,id,'after')
 assert not after['collapsed_uv_faces'],(id,after['collapsed_uv_faces'])
 for key in ('vertices','edges','faces','triangles','signed_volume_m3','bounds_blender_xyz'):
  assert before[key]==after[key],(id,key)
 previews['wireframe_after']=screenshot(obj,id,'AFTER_WIREFRAME',wire=True)
 previews['shaded_after']=screenshot(obj,id,'AFTER_SHADED')
 previews['endcap_closeup_after']=screenshot(obj,id,'ENDCAP_CLOSEUP',zoom=True)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 blend=OUT/'Blend'/f'{stem}_v003.blend';fbx=OUT/'FBX'/f'{stem}_v003.fbx'
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},
  global_scale=1,apply_unit_scale=True,axis_forward='-Z',axis_up='Y',
  add_leaf_bones=False,bake_anim=False,use_mesh_modifiers=False)
 assert blend.read_bytes().startswith(b'BLENDER')
 assert fbx.read_bytes().startswith(b'Kaydara FBX Binary  '+bytes([0,26,0]))
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(fbx))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert len(objs)==1,(id,'FBX parts',len(objs))
 imported=topology(objs[0].data);validate(imported,id,'reimport')
 assert not imported['collapsed_uv_faces'],(id,imported['collapsed_uv_faces'])
 assert len(objs[0].data.materials)==3,(id,'FBX material slots',len(objs[0].data.materials))
 diff=max(abs(after['bounds_blender_xyz'][i][j]-imported['bounds_blender_xyz'][i][j]) for i in range(2) for j in range(3))
 assert diff<1e-4,(id,'FBX bounds deviation',diff)
 result={'id':id,'original':str(original.relative_to(REPO)),
  'before_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
  'repaired_blend':str(blend.relative_to(REPO)),'repaired_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
  'repaired_fbx':str(fbx.relative_to(REPO)),'repaired_fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),
  'mesh_topology_before':before,'mesh_topology_after':after,'fbx_roundtrip_topology':imported,
  'edits':[{'face_index':i,'defect':'COLLAPSED_UV0_ON_ENDCAP','fix':'PROJECT_YZ','geometry_changed':False} for i in endcaps],
  'previews':previews,'blender_open':'PASS','blender_fbx_roundtrip':'PASS',
  'unity_6_urp':'NOT_RUN','independent_qa':'PENDING'}
 for phase in ('before','after'):
  (OUT/'QA'/f'{id}_mesh_topology_{phase}.json').write_text(json.dumps(result['mesh_topology_'+phase],indent=2)+'\n')
 return result

if __name__=='__main__':
 reports={}
 for id,stem in STEMS.items():
  reports[id]=one(id,stem)
  print('C01-12 PASS03 Blender source and FBX roundtrip PASS:',id,flush=True)
 (OUT/'QA'/'C01_12_PASS03_REPORT.json').write_text(json.dumps(reports,indent=2)+'\n')
 print('C01-12 PASS03 COMPLETED',flush=True)
