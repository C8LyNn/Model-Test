"""C01-18 W20 real P18-03 native BLEND+FBX static+rolling BVH.
Pure virtual rotation of exact WORLD vertices; does not mutate Blender transforms,
avoids local-Euler and parent conversion artifacts. Read-only existing LFS assets.
"""
import bpy,math,pathlib,hashlib,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
SHA={'blend':'ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56',
'fbx':'f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926'}
FILES={'blend':R/'Sources'/'P18-03.blend','fbx':R/'Models'/'P18-03.fbx'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
for k,p in FILES.items():
 assert p.stat().st_size>100000 and sha(p)==SHA[k],('native real LFS SHA drift',k)
assert FILES['blend'].read_bytes().startswith(b'BLENDER-')
assert FILES['fbx'].read_bytes().startswith(b'Kaydara FBX Binary  ')
assert bpy.app.version>=(4,0,0)
WHEELS=('Wheel_LB','Wheel_LF','Wheel_RB','Wheel_RF')
def data(o):
 o.data.calc_loop_triangles()
 return ([tuple(o.matrix_world@v.co) for v in o.data.vertices],
         [tuple(t.vertices) for t in o.data.loop_triangles])
def box(pts):
 return [[min(v[j] for v in pts),max(v[j] for v in pts)] for j in range(3)]
def overlap_aabb(a,b):
 return all(a[j][0]<=b[j][1] and b[j][0]<=a[j][1] for j in range(3))
def bvh(vertices,triangles):
 return BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=0)
def spin(verts,ctr,degrees):
 a=math.radians(degrees);c=math.cos(a);s=math.sin(a)
 return [(v[0],ctr[1]+(v[1]-ctr[1])*c-(v[2]-ctr[2])*s,
             ctr[2]+(v[1]-ctr[1])*s+(v[2]-ctr[2])*c) for v in verts]
def gather(tag):
 m={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
 assert len(m)==63,(tag,'mesh count',len(m))
 assert sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in m.values())==1780
 assert all(o.data.uv_layers for o in m.values())
 per={}
 for wid in WHEELS:
  wheel=m[wid];hubin=m[wid+'_Hub_In'];hubout=m[wid+'_Hub_Out']
  assert hubin.parent==wheel and hubout.parent==wheel,(tag,'hub parenting',wid)
  ctr=tuple(wheel.matrix_world.translation)
  assert abs(ctr[2]-.105)<.001 and abs(abs(ctr[0])-.39)<.001,(tag,ctr)
  names=['Cart_Shelf_0','Cart_Shelf_1']+[n for n in m if n.startswith('Cart_Upright_')]+[wid+'_'+v for v in ('ForkInner','ForkOuter','ForkCrown','Anchor','Gusset','AnchorRetainer','Axle','AxleFastener')]
  assert len(names)==14 and len(set(names))==14
  stat={n:data(m[n]) for n in names}
  sta={n:(box(v),bvh(v,t)) for n,(v,t) in stat.items()}
  bodies={o.name:data(o) for o in (wheel,hubin,hubout)}
  initial=box(bodies[wid][0])
  assert abs(initial[2][0])<1e-4,(tag,wid,'rest ground',initial)
  # Circular rubber envelope radius must be .105m about actual X axle.
  maxrad=max(math.hypot(v[1]-ctr[1],v[2]-ctr[2]) for v in bodies[wid][0])
  assert abs(maxrad-.105)<0.001,(tag,wid,'radius',maxrad)
  rub=[];metal=[];floor=[]
  for degree in range(0,360,5):
   for name,(orig,triangles) in bodies.items():
    world=spin(orig,ctr,degree)
    b=box(world)
    if name==wid: floor.append(b[2][0])
    lazy=None
    for st,(other,other_bvh) in sta.items():
     if not overlap_aabb(b,other): continue
     if lazy is None: lazy=bvh(world,triangles)
     hit=lazy.overlap(other_bvh)
     if not hit:continue
     note={'angle_deg':degree,'moving':name,'static':st,'triangle_pairs':len(hit)}
     if name==wid and not st.endswith(('Axle','AxleFastener')):rub.append(note)
     elif name!=wid: metal.append(note)
  per[wid]={'moving_children':[hubin.name,hubout.name],'angles_tested':72,'rigid_targets':14,
             'axle_world_xyz':[round(x,8) for x in ctr],'rubber_radius_m':maxrad,
             'resting_ground_m':initial[2][0],
             'rolling_min_ground_m':min(floor),'rolling_max_ground_m':max(floor),
             'rubber_nonbearing_contacts':rub,'hub_fixed_contacts':metal,
             'hub_contact_total':len(metal)}
 return {'format':tag,'mesh_parts':63,'triangles':1780,'wheels':per,
         'rubber_contact_count':sum(len(x['rubber_nonbearing_contacts']) for x in per.values()),
         'hub_contact_count':sum(x['hub_contact_total'] for x in per.values()),
         'min_ground_m':min(x['rolling_min_ground_m'] for x in per.values())}
bpy.ops.wm.open_mainfile(filepath=str(FILES['blend']))
a=gather('authentic_blender_native')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(FILES['fbx']))
b=gather('authentic_binary_fbx_reimport')
res={'wave':'W20','model':'P18-03','owner':'C01-18','native_sha256':SHA,
     'method':'Apply an exact rigid X-axis rotation to hydrated REAL WORLD-space vertex arrays of actual Blender4 and FBX imported scene. Source/world hierarchy untouched. 4 wheels × 72 samples × 14 fixed parts and separate rotating hubs. BVH exact triangle broadphase, contact vs bearing distinguished.',
     'source':a,'fbx':b,'blender_fbx_rubber_clear_agreement':(a['rubber_contact_count']==0)==(b['rubber_contact_count']==0),
     'nonbearing_rubber_clear':a['rubber_contact_count']==b['rubber_contact_count']==0,
     'source_fbx_ground_agree':abs(a['min_ground_m']-b['min_ground_m'])<0.0002,
     'no_new_blend_or_fbx':True,'C01_02':'PENDING','Unity6':'NOT_RUN','release':'HOLD',
     'caveats':'Metal hub/bearing contacts not automatically errors. No wheel axle steering or cart translation/ground rolling physics, no Unity simulation.'}
out=R/'QA'/'Pass20'/'P18-03_REAL_NATIVE_WHEEL_HUB_MOTION_QA.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(res,sort_keys=True,indent=2)+'\n')
print('C01_W20_REAL_WHEEL_WORLD_VERTEX_QA',json.dumps({
 'source_rubber':a['rubber_contact_count'],'fbx_rubber':b['rubber_contact_count'],
 'source_min_ground_m':a['min_ground_m'],'fbx_min_ground_m':b['min_ground_m'],
 'hub_contacts_source':a['hub_contact_count'],'hub_contacts_fbx':b['hub_contact_count'],
 'clear':res['nonbearing_rubber_clear']}),flush=True)
assert res['blender_fbx_rubber_clear_agreement'] and res['source_fbx_ground_agree'], 'native and binary frame divergence'
assert a['min_ground_m']>=-0.0002 and b['min_ground_m']>=-0.0002,'wheel falls significantly beneath ground by real spin'
