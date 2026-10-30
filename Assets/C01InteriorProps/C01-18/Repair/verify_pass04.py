"""C01-18 PASS04 — verify 7 ORIGINAL hydrated BLEND/FBX assets, never reconstruct models.
run: blender -b --python verify_pass04.py -- ROOT P18-XX [P18-YY...]
Reads only model sources; creates JSON reports under QA/Pass04; never edits geometry.
"""
import bpy,bmesh,sys,math,json,hashlib,pathlib,collections
from mathutils import Vector
ROOT=pathlib.Path(sys.argv[sys.argv.index('--')+1])
IDS=sys.argv[sys.argv.index('--')+2:]
OUT=ROOT/'QA'/'Pass04'
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def vertices(o):
 return [o.matrix_world @ v.co for v in o.data.vertices]
def coords(o):
 return set(tuple(round(float(x),5) for x in p) for p in vertices(o))
def bounds(objs):
 vv=[p for o in objs for p in vertices(o)]
 return [ [min(float(v[i]) for v in vv),max(float(v[i]) for v in vv)] for i in range(3)]
def uvset(mesh):
 # Linked corner UVs, not vertex UVs; quantization tolerates FBX float noise.
 if not mesh.uv_layers:return []
 return sorted(tuple(round(float(c),5) for c in uv.uv) for uv in mesh.uv_layers.active.data)
def audit_obj(o):
 m=o.data;m.calc_loop_triangles()
 bm=bmesh.new();bm.from_mesh(m)
 edges=list(bm.edges);faces=list(bm.faces)
 zeroedge=sum(e.calc_length()<=1e-8 for e in edges)
 deg=sum(f.calc_area()<=1e-12 for f in faces)
 boundary=sum(e.is_boundary for e in edges)
 nonmanifold=sum(not e.is_manifold and not e.is_boundary for e in edges)
 doubles=collections.Counter(tuple(sorted(round(float(v.co[i]),7) for i in range(3))) for v in bm.verts)
 coincident=sum(c-1 for c in doubles.values() if c>1)
 dup=collections.Counter(tuple(sorted(v.index for v in f.verts)) for f in faces)
 dupfaces=sum(c-1 for c in dup.values() if c>1)
 loose_v=sum(not v.link_edges and not v.link_faces for v in bm.verts)
 loose_e=sum(not e.link_faces for e in edges)
 badwinding=sum(len(e.link_loops)==2 and e.link_loops[0].vert==e.link_loops[1].vert for e in edges)
 hasuv=bool(m.uv_layers) and len(m.uv_layers.active.data)==len(m.loops)
 invaliduv=sum(not math.isfinite(float(c)) for d in m.uv_layers for uv in d.data for c in uv.uv)
 invalidnormal=sum(not math.isfinite(float(c)) for v in m.vertices for c in v.normal)
 tris=[ [o.matrix_world@m.vertices[i].co for i in tri.vertices] for tri in m.loop_triangles]
 area=[((t[1]-t[0]).cross(t[2]-t[0])).length/2 for t in tris]
 tri_deg=sum(a<=1e-12 for a in area)
 totalarea=sum(area)
 v=len(bm.verts);e=len(bm.edges);f=len(bm.faces)
 # Positive volume for intentionally closed, consistently outward parts.
 volume=bm.calc_volume(signed=True) if all(x.is_manifold for x in bm.edges) else None
 bm.free()
 return {'name':o.name,'V':v,'E':e,'F':f,'tris':len(tris),
 'loose_vertices':loose_v,'loose_edges':loose_e,'zero_length_edges':zeroedge,
 'degenerate_faces':deg,'duplicate_faces':dupfaces,'coincident_vertex_candidates':coincident,
 'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'bad_winding':badwinding,
 'triangulated_zero_area':tri_deg,'triangle_area_m2':round(totalarea,9),
 'positive_volume':volume is not None and volume>1e-12,'signed_volume':volume,
 'uv0_present':hasuv,'invalid_uv_values':invaliduv,'invalid_normal_values':invalidnormal,
 'material_count':len(m.materials)}
def snap():
 mesh=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name)
 empties=sorted((o for o in bpy.context.scene.objects if o.type=='EMPTY'),key=lambda o:o.name)
 bpy.context.view_layer.update()
 parts={o.name:audit_obj(o) for o in mesh}
 return mesh,empties,parts,bounds(mesh),{o.name:coords(o) for o in mesh},{o.name:uvset(o.data) for o in mesh}
def sumfields(parts):
 names=list(parts)
 keys=['V','E','F','tris','loose_vertices','loose_edges','zero_length_edges','degenerate_faces',
 'duplicate_faces','coincident_vertex_candidates','boundary_edges','nonmanifold_edges',
 'bad_winding','triangulated_zero_area','invalid_uv_values','invalid_normal_values']
 return {'mesh_parts':len(names),**{k:sum(parts[n][k] for n in names) for k in keys}}
for pid in IDS:
 src=ROOT/'Sources'/(pid+'.blend');fbx=ROOT/'Models'/(pid+'.fbx')
 assert src.exists() and src.read_bytes()[:7]==b'BLENDER',f'not real .blend: {src}'
 assert fbx.exists() and fbx.read_bytes()[:20].startswith(b'Kaydara FBX Binary'),f'not binary FBX: {fbx}'
 source_hash=sha(src);fbx_hash=sha(fbx)
 bpy.ops.wm.open_mainfile(filepath=str(src))
 srcmesh,srcempties,sparts,sbounds,spos,suv=snap()
 if not srcmesh:raise RuntimeError(pid+' source has no actual meshes')
 fails=[]
 for p in sparts.values():
  for key in ('loose_vertices','loose_edges','zero_length_edges','degenerate_faces',
     'duplicate_faces','boundary_edges','nonmanifold_edges','bad_winding','triangulated_zero_area',
     'invalid_uv_values','invalid_normal_values'):
   if p[key]:fails.append(f"{p['name']}: source {key}={p[key]}")
  if not p['uv0_present']:fails.append(p['name']+' no source UV0')
  if not p['positive_volume']:fails.append(p['name']+' source signed volume invalid')
  if not p['material_count']:fails.append(p['name']+' missing source material')
 source_movement={o.name:tuple(round(float(c),5) for c in o.matrix_world.translation) for o in srcempties}
 # Roundtrip exactly the final binary FBX stored in this producer PR; no fake regeneration.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(fbx),use_custom_normals=True)
 mesh,empties,parts,bb,pos,uv=snap()
 # Some importers rename an object with suffix; report hard fail for missing IDs.
 if set(parts)!=set(sparts):fails.append('part names changed '+repr((sorted(sparts),sorted(parts))))
 common=sorted(set(parts)&set(sparts))
 for n in common:
  for k in ('F','tris'):
   if parts[n][k]!=sparts[n][k]:fails.append(f'{n}: {k} source={sparts[n][k]} FBX={parts[n][k]}')
  if pos[n]!=spos[n]:fails.append(f'{n}: world-space vertex position sets changed source={len(spos[n])} FBX={len(pos[n])}')
  if not parts[n]['uv0_present']:fails.append(n+' FBX missing UV0')
  if uv[n]!=suv[n]:fails.append(n+' FBX changed per-loop UV0 values')
  for k in ('loose_vertices','loose_edges','zero_length_edges','degenerate_faces','duplicate_faces',
            'boundary_edges','nonmanifold_edges','bad_winding','triangulated_zero_area',
            'invalid_uv_values','invalid_normal_values'):
   if parts[n][k]:fails.append(f'{n}: FBX {k}={parts[n][k]}')
 for i,(a,b) in enumerate(zip(sbounds,bb)):
  if abs((a[1]-a[0])-(b[1]-b[0]))>0.001:fails.append('FBX envelope axis '+str(i)+' mismatched')
 if pid in ('P18-05','P18-07'):
  pivot='Lid_HingePivot' if pid=='P18-05' else 'Toolbox_LidHinge'
  if pivot not in source_movement:fails.append('missing source hinge '+pivot)
  if not any(o.name==pivot for o in empties):fails.append('FBX missing hinge '+pivot)
 if pid=='P18-03':
  wheels=[n for n in parts if n.startswith('Wheel_')]
  if len(wheels)!=4:fails.append('missing wheel part(s): '+repr(wheels))
 report={'model_id':pid,'source_git_ref':'CI checkout PR head, see workflow run SHA',
 'source_blend_sha256':source_hash,'binary_fbx_sha256':fbx_hash,
 'source':sumfields(sparts),'fbx_reimport':sumfields(parts),
 'source_parts':sparts,'imported_parts':parts,
 'source_empty_pivots':source_movement,'imported_empty_pivots':{o.name:list(o.matrix_world.translation) for o in empties},
 'bounds_blender_source':sbounds,'bounds_blender_fbx_reimport':bb,
 'uv0_per_loop_identical':all(suv[n]==uv[n] for n in common),
 'world_vertex_sets_identical':all(spos[n]==pos[n] for n in common),
 'failures':fails,'status':'PASS' if not fails else 'FAIL','unity':'NOT_RUN','independent_qa':'NOT_RUN'}
 outfile=OUT/(pid+'_native_fbx_audit.json')
 outfile.write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('C01_PASS04_NATIVE',pid,report['status'], 'blend',source_hash,'fbx',fbx_hash,'V/E/F/tris',sumfields(parts),flush=True)
 for fail in fails:print('C01_PASS04_FAIL',pid,fail,flush=True)
 if fails:raise RuntimeError('Native audit fails; see '+str(outfile))
