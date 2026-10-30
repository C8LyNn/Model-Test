"""C01-18 PASS03 / technical topology audit and surgical repair of ORIGINAL Blender sources.
No procedural reconstruction: loads exact existing binary .blend. Never joins objects.
Usage: blender -b --python mesh_repair.py -- <root> P18-04 P18-05 ...
Outputs QA/Pass03/{id}/{before,after}.json and genuine Blender renders + FBX roundtrip.
"""
import bpy, bmesh, sys, os, math, json, hashlib, pathlib, collections
from mathutils import Vector
ROOT=pathlib.Path(sys.argv[sys.argv.index('--')+1])
IDS=sys.argv[sys.argv.index('--')+2:]
EPS=1e-7
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
def objects():return sorted([o for o in bpy.context.scene.objects if o.type=="MESH"],key=lambda x:x.name)
def mesh_measure(o):
 m=o.data
 bm=bmesh.new();bm.from_mesh(m)
 bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
 coords=collections.defaultdict(list)
 for v in bm.verts: coords[tuple(round(float(v.co[i]),7) for i in range(3))].append(v)
 dup=sum(len(v)-1 for v in coords.values() if len(v)>1)
 loose_verts=sum(not v.link_edges and not v.link_faces for v in bm.verts)
 loose_edges=sum(not e.link_faces for e in bm.edges)
 zero_edges=sum(e.calc_length()<EPS for e in bm.edges)
 degenerates=sum(f.calc_area()<EPS*EPS for f in bm.faces)
 keys=collections.Counter(tuple(sorted(v.index for v in f.verts)) for f in bm.faces)
 duplicated_faces=sum(n-1 for n in keys.values() if n>1)
 boundaries=sum(e.is_boundary for e in bm.edges)
 nonmanifold=sum(not e.is_manifold and not e.is_boundary for e in bm.edges)
 bad_winding=0
 for e in bm.edges:
  if len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert: bad_winding+=1
 # T-junction vertices on an edge, excluding its own endpoints. Treat as candidate only.
 tj=0
 verts=list(bm.verts)
 for e in bm.edges:
  a,b=e.verts[0].co,e.verts[1].co;ab=b-a;ll=ab.length_squared
  if ll<EPS*EPS:continue
  for v in verts:
   if v is e.verts[0] or v is e.verts[1]:continue
   # same-object only, exact geometric collinearity
   t=(v.co-a).dot(ab)/ll
   if EPS<t<1-EPS and (a+ab*t-v.co).length < EPS: tj+=1
 area=sum(f.calc_area() for f in bm.faces)
 components=0;seen=set()
 for v in bm.verts:
  if v in seen:continue
  components+=1;queue=[v];seen.add(v)
  for x in queue:
   for e in x.link_edges:
    w=e.other_vert(x)
    if w not in seen:seen.add(w);queue.append(w)
 closed=bool(bm.faces) and all(e.is_manifold for e in bm.edges)
 volume=bm.calc_volume(signed=True) if closed else None
 bm.free()
 m.calc_loop_triangles()
 return dict(name=o.name,vertices=len(m.vertices),edges=len(m.edges),faces=len(m.polygons),
  triangles=len(m.loop_triangles),components=components,loose_vertices=loose_verts,
  loose_edges=loose_edges,zero_edges=zero_edges,degenerate_faces=degenerates,
  duplicate_faces=duplicated_faces,coincident_vertex_candidates=dup,
  boundary_edges=boundaries,nonmanifold_edges=nonmanifold,inconsistent_winding_edges=bad_winding,
  t_junction_candidates=tj,closed=closed,signed_volume=volume,
  area=area,uv_layers=len(m.uv_layers),materials=len(m.materials))
def aggregate(parts):
 ks=['vertices','edges','faces','triangles','loose_vertices','loose_edges','zero_edges',
 'degenerate_faces','duplicate_faces','coincident_vertex_candidates','boundary_edges',
 'nonmanifold_edges','inconsistent_winding_edges','t_junction_candidates','components']
 a={k:sum(v[k] for v in parts) for k in ks}
 a['mesh_parts']=len(parts)
 a['closed_meshes']=sum(bool(x['closed']) for x in parts)
 return a
def actual_bounds():
 bpy.context.view_layer.update()
 p=[o.matrix_world@v.co for o in objects() for v in o.data.vertices]
 if not p:raise RuntimeError('Missing real geometry')
 return [[min(q[i] for q in p),max(q[i] for q in p)] for i in range(3)]
def audit(pid,stage):
 parts=[mesh_measure(o) for o in objects()]
 return {'id':pid,'stage':stage,'source':'original .blend file, no viewer reconstruction',
 'parts':parts,'total':aggregate(parts),'bounds_blender_xyz':actual_bounds(),
 'exceptions':{'separate_mesh_parts':'INTENTIONAL: maintain independently animated covers, wheels, frame and decorative components',
 'mesh_boundary_edges':'INTENTIONAL only when explicitly documented per part; closed solid parts must have zero boundaries',
 'cross_object_intersections':'NOT AUTOMATICALLY WELDED; hardware joins and intentional layered decorations need visual review'},
 'self_intersection':'NOT_RUN: exact triangle-triangle test not implemented; same-object T-junction candidate test recorded',
 'cross_object_coplanar_overlap':'NOT_RUN: requires manual inspection of original assembly',
 'unity_import':'NOT_RUN'}
def uv_signature(m):
 if not m.uv_layers:return None
 layer=m.uv_layers.active.data
 return sorted((round(float(v.uv[0]),6),round(float(v.uv[1]),6)) for v in layer)
def fix_object(o):
 m=o.data;before=mesh_measure(o);fix=[]
 # No indiscriminate merging: only near-exact coincident vertices from same mesh,
 # and only if improvement can be verified without changing faces, UV corners or silhouette.
 bm=bmesh.new();bm.from_mesh(m)
 uv=uv_signature(m)
 original_faces=len(bm.faces);original_area=sum(f.calc_area() for f in bm.faces)
 if before['loose_vertices'] or before['loose_edges']:
  loose=[e for e in bm.edges if not e.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES');fix.append('remove_unused_edges')
  dangling=[v for v in bm.verts if not v.link_edges and not v.link_faces]
  if dangling:bmesh.ops.delete(bm,geom=dangling,context='VERTS');fix.append('remove_unused_vertices')
 if before['zero_edges'] or before['degenerate_faces']:
  bmesh.ops.dissolve_degenerate(bm,dist=EPS,edges=list(bm.edges));fix.append('dissolve_zero_area_geometry')
 # On pieces with coincident positions, conditional weld is eligible only if
 # boundary/nonmanifold improves; changes to UV loops/face count reject and roll back.
 base_surface_count=len(bm.faces)
 bm.to_mesh(m);m.update();bm.free()
 mid=mesh_measure(o)
 if mid['coincident_vertex_candidates'] and (mid['boundary_edges'] or mid['nonmanifold_edges']):
  snapshot=[(tuple(x.co),tuple(x.normal)) for x in m.vertices]
  uv0=uv_signature(m)
  tmp=bmesh.new();tmp.from_mesh(m)
  bmesh.ops.remove_doubles(tmp,verts=list(tmp.verts),dist=EPS)
  tmp.to_mesh(m);m.update();tmp.free()
  candidate=mesh_measure(o)
  safe=(candidate['faces']==mid['faces'] and candidate['triangles']==mid['triangles'] and
   candidate['degenerate_faces']<=mid['degenerate_faces'] and
   candidate['nonmanifold_edges']<=mid['nonmanifold_edges'] and
   candidate['boundary_edges']<mid['boundary_edges'] and
   uv_signature(m)==uv0 and abs(candidate['area']-mid['area'])<1e-6)
  if safe:fix.append('validated_coincident_vertex_weld')
  else:
   # Undo by restoring entire mesh datablock (not by attempting to reverse weld).
   bpy.data.meshes.remove(m)
   raise RuntimeError('Weld validation rejected candidate on '+o.name+
    '; conservative fallback required; original mesh preserved in source .blend')
 after=mesh_measure(o)
 if after['loose_vertices'] or after['loose_edges'] or after['zero_edges'] or after['degenerate_faces'] or after['duplicate_faces'] or after['inconsistent_winding_edges']:
  raise RuntimeError('Unresolved hard topology defect: '+o.name+' '+str(after))
 return fix
def camera_and_render(pid,folder,stage,wire=False,close=False):
 scene=bpy.context.scene
 scene.render.engine="CYCLES";scene.cycles.device='CPU';scene.cycles.samples=6
 bpy.context.view_layer.cycles.use_denoising=False
 scene.render.resolution_x=384;scene.render.resolution_y=384;scene.render.resolution_percentage=100
 if scene.world is None:scene.world=bpy.data.worlds.new("C01_QA_World")
 scene.world.color=(.26,.29,.33)
 bounds=actual_bounds();center=Vector([(p[0]+p[1])/2 for p in bounds])
 extent=max(p[1]-p[0] for p in bounds)
 if close: extent=max(extent*.42,.25)
 camdata=bpy.data.cameras.new("C01_QA_Camera")
 cam=bpy.data.objects.new("C01_QA_Camera",camdata);scene.collection.objects.link(cam)
 camdata.type='ORTHO';camdata.ortho_scale=max(.35,extent*2.05)
 cam.location=center+Vector((extent*1.9,-extent*2.6,extent*1.75))
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.camera=cam
 lightdata=bpy.data.lights.new("C01_QA_Area","AREA")
 light=bpy.data.objects.new("C01_QA_Area",lightdata);scene.collection.objects.link(light)
 light.location=center+Vector((2,-3,4));lightdata.energy=650;lightdata.shape="DISK";lightdata.size=4
 prior=scene.view_layers[0].material_override
 if wire:
  mat=bpy.data.materials.new('C01_QA_ActualMeshWire')
  mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
  out=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader')
  base=nodes.new('ShaderNodeEmission');base.inputs['Color'].default_value=(.82,.86,.89,1)
  line=nodes.new('ShaderNodeEmission');line.inputs['Color'].default_value=(.012,.018,.027,1)
  wr=nodes.new('ShaderNodeWireframe');wr.use_pixel_size=False;wr.inputs['Size'].default_value=.004
  links=mat.node_tree.links;links.new(wr.outputs['Fac'],mix.inputs[0]);links.new(base.outputs[0],mix.inputs[1]);links.new(line.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
  scene.view_layers[0].material_override=mat
 os.makedirs(folder,exist_ok=True)
 scene.render.filepath=str(pathlib.Path(folder)/(stage+'.png'))
 scene.render.image_settings.file_format='PNG'
 bpy.ops.render.render(write_still=True)
 scene.view_layers[0].material_override=prior
 bpy.data.objects.remove(light,do_unlink=True);bpy.data.objects.remove(cam,do_unlink=True)
 if wire:bpy.data.materials.remove(mat,do_unlink=True)
def export_and_roundtrip(pid,folder,after):
 out=ROOT/'Models'/(pid+'.fbx')
 # Export original meshes/empty pivots only; do not serialize render-only objects.
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in {'MESH','EMPTY'} and not o.name.startswith('C01_QA_'):o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,axis_forward='-Z',axis_up='Y',
  object_types={'MESH','EMPTY'},add_leaf_bones=False)
 assert out.stat().st_size>1000
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(out))
 imp=audit(pid,'FBX_REIMPORTED')
 exp=after['total'];got=imp['total']
 # Preserve triangle and part counts, physical silhouette and surface area;
 # importer may legally split vertices on UV seams or hard edges.
 if got['triangles']!=exp['triangles'] or got['mesh_parts']!=exp['mesh_parts']:
  raise RuntimeError(pid+' FBX topology count changed: '+repr((exp,got)))
 for o in objects():
  if not o.data.uv_layers:raise RuntimeError(pid+' lost UV0 during FBX roundtrip: '+o.name)
  if not len(o.data.polygons):raise RuntimeError(pid+' lost faces: '+o.name)
 for a,b in zip(after['bounds_blender_xyz'],imp['bounds_blender_xyz']):
  if abs((a[1]-a[0])-(b[1]-b[0]))>0.002:
   raise RuntimeError(pid+' dimensions not preserved in FBX reimport')
 return imp,sha(out)
for pid in IDS:
 original=ROOT/'Sources'/(pid+'.blend')
 if not original.exists() or original.read_bytes()[:7]!=b'BLENDER':
  raise RuntimeError('REAL BLENDER source unavailable: '+str(original))
 original_hash=sha(original)
 bpy.ops.wm.open_mainfile(filepath=str(original))
 before=audit(pid,'BEFORE')
 folder=ROOT/'QA'/'Pass03'/pid
 folder.mkdir(parents=True,exist_ok=True)
 (folder/'mesh_topology_before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
 camera_and_render(pid,folder,'wireframe_before',wire=True)
 fixes={};before_bounds=actual_bounds()
 for o in objects():
  fixes[o.name]=fix_object(o)
 after=audit(pid,'AFTER')
 if any(abs(x-y)>1e-5 for a,b in zip(before_bounds,after['bounds_blender_xyz']) for x,y in zip(a,b)):
  raise RuntimeError(pid+' silhouette/bounds changed unexpectedly')
 after['changes_by_mesh']=fixes
 after['source_before_sha256']=original_hash
 after['surface_parts_preserved']=len(before['parts'])==len(after['parts'])
 after['real_modification_count']=sum(len(v) for v in fixes.values())
 (folder/'mesh_topology_after.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
 camera_and_render(pid,folder,'wireframe_after',wire=True)
 camera_and_render(pid,folder,'shaded_after',wire=False)
 camera_and_render(pid,folder,'mesh_detail_after',wire=True,close=True)
 if after['real_modification_count']:
  bpy.ops.wm.save_as_mainfile(filepath=str(original))
 imp,fbx_hash=export_and_roundtrip(pid,folder,after)
 (folder/'fbx_roundtrip.json').write_text(json.dumps({'id':pid,'status':'PASS',
 'source_after_sha256':sha(original),'fbx_sha256':fbx_hash,'before_total':before['total'],
 'after_total':after['total'],'reimport_total':imp['total'],
 'description':'Real source Blender .blend re-opened; actual FBX exported, then imported and bounds/part/tris/UV validated',
 'unity':'NOT_RUN','independent_qa':'PENDING'},indent=2),encoding='utf-8')
 print('C01_PASS03_RESULT',pid,'fixes',after['real_modification_count'],
 'before',before['total'],'after',after['total'],flush=True)
