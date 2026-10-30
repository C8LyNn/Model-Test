"""C01-18 PASS03 / actual source part intersection screening, Blender BVH and coplanar overlaps.
Read only .blend; does NOT weld or modify physical assets.
BVH intersections are candidate-level (exclude shared vertex adjacency).
2D overlap uses convex polygon clipping and tests coplanar external part surfaces.
"""
import bpy,bmesh,sys,json,pathlib,hashlib,math,itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=pathlib.Path(sys.argv[sys.argv.index('--')+1]);ids=sys.argv[sys.argv.index('--')+2:]
EPS=1e-5
def signed_area(poly):
 return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))
def clip_polygon(sub,clip):
 if len(sub)<3 or len(clip)<3:return []
 sgn=1 if signed_area(clip)>0 else -1
 def inside(pt,a,b):
  return sgn*((b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0]))>=-EPS
 def intersect(p,q,a,b):
  dx,dy=q[0]-p[0],q[1]-p[1];ax,ay=b[0]-a[0],b[1]-a[1]
  den=dx*ay-dy*ax
  if abs(den)<1e-14:return q
  t=((a[0]-p[0])*ay-(a[1]-p[1])*ax)/den
  return (p[0]+t*dx,p[1]+t*dy)
 result=sub
 for a,b in zip(clip,clip[1:]+clip[:1]):
  inp=result;result=[]
  if not inp:break
  prev=inp[-1];was=inside(prev,a,b)
  for cur in inp:
   now=inside(cur,a,b)
   if now!=was:result.append(intersect(prev,cur,a,b))
   if now:result.append(cur)
   prev=cur;was=now
 return result
def surf(o):
 m=o.data
 B=[o.matrix_world@v.co for v in m.vertices]
 faces=[]
 for p in m.polygons:
  pts=[B[i] for i in p.vertices]
  n=(o.matrix_world.to_3x3()@p.normal).normalized()
  # Only convex face polygons from source primitives are considered by clipping.
  faces.append((pts,n))
 return faces,B
def bbox(B):
 return [(min(x[i] for x in B),max(x[i] for x in B)) for i in range(3)]
def bbox_hit(A,B):
 return all(max(a[0],b[0])<min(a[1],b[1])+EPS for a,b in zip(A,B))
def coplanar_area(face_a,face_b):
 A,na=face_a;B,nb=face_b
 if abs(na.dot(nb))<.99999:return 0
 plane=A[0]
 if any(abs((p-plane).dot(na))>EPS for p in B):return 0
 k=max(range(3),key=lambda i:abs(na[i]))
 axes=[i for i in range(3) if i!=k]
 ap=[(float(p[axes[0]]),float(p[axes[1]])) for p in A]
 bp=[(float(p[axes[0]]),float(p[axes[1]])) for p in B]
 clipped=clip_polygon(ap,bp)
 return abs(signed_area(clipped)) if len(clipped)>=3 else 0
for id in ids:
 path=root/'Sources'/(id+'.blend')
 if not path.exists():raise RuntimeError('Missing original '+str(path))
 bpy.ops.wm.open_mainfile(filepath=str(path))
 objs=sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda x:x.name)
 report=dict(id=id,original_blend_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
  bvh_nonadjacent_candidate_count=0,bvh_candidates=[],cross_object_coplanar_candidate_count=0,
  cross_object_coplanar_candidates=[],inspected_mesh_parts=len(objs),
  warning='Candidates are NOT automatic topology FAIL; intentional independent hardware contacts require explicit review.',
  unity='NOT_RUN')
 bpy.context.view_layer.update()
 surfaces={}
 for o in objs:
  bm=bmesh.new();bm.from_mesh(o.data);bm.faces.index_update()
  bvh=BVHTree.FromBMesh(bm,epsilon=0.0000001)
  found=set()
  for a,b in bvh.overlap(bvh):
   if a==b:continue
   key=tuple(sorted((a,b)))
   if key in found:continue
   found.add(key)
   fa=bm.faces[key[0]];fb=bm.faces[key[1]]
   if set(fa.verts)&set(fb.verts):continue
   report['bvh_nonadjacent_candidate_count']+=1
   if len(report['bvh_candidates'])<32:report['bvh_candidates'].append({'mesh':o.name,'faces':key})
  bm.free()
  S,B=surf(o);surfaces[o.name]=(S,bbox(B))
 for i,o in enumerate(objs):
  A,boxA=surfaces[o.name]
  for p in objs[i+1:]:
   B,boxB=surfaces[p.name]
   if not bbox_hit(boxA,boxB):continue
   for ia,fa in enumerate(A):
    for ib,fb in enumerate(B):
     area=coplanar_area(fa,fb)
     if area>1e-7:
      report['cross_object_coplanar_candidate_count']+=1
      if len(report['cross_object_coplanar_candidates'])<50:
       report['cross_object_coplanar_candidates'].append({'meshA':o.name,'faceA':ia,'meshB':p.name,'faceB':ib,'area_projected_m2':round(area,8)})
 out=root/'QA'/'Pass03'/id/'mesh_overlap_review.json';out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2),encoding='utf8')
 print('C01_PASS03_OVERLAP',id,'BVH nonadjacent',report['bvh_nonadjacent_candidate_count'],'coplanar cross-object',report['cross_object_coplanar_candidate_count'],flush=True)

# PASS03: rerun against checked-in surgically corrected source after first topology repair.
