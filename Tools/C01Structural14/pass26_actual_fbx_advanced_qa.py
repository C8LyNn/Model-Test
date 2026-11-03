#!/usr/bin/env python3
"""WAVE26 C01-14: READ-ONLY advanced QA of actual SHA-pinned FBX7400.
No automatic weld/remesh/decimate, no source modification, no Claude doors.
Requires numpy and shapely; use genuine hydrated repo LFS, not text pointers.
"""
import collections,hashlib,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Tools/C01Structures14"))
from fbx_raw_pass05 import Reader,children,child,values,audit_fbxf

BASE=ROOT/"Assets/C01StructuralPrototypes/P14"
FILES=[
 ("RAI-01",BASE/"Pass17/Native/C01_14_RAI-01_DETAIL17.fbx",
  "f0c8fd590d7752431c869be2f9807209b7632d87a77ab619049c90f60f0ff1fe",20,424),
 ("RMP-01",BASE/"Pass23/Native/C01_14_RMP-01_PASS23_v003.fbx",
  "3b47d12a5a32c286c9e35a8f7198c0820d7fef5e9325823a2cfabdc12559c417",6,72)
]
def ensure(check,info):
 if not check:raise AssertionError(info)
def mesh_parser(path):
 p=Reader(path.read_bytes());nodes=p.root()
 objs=next(x for x in nodes if x["name"]=="Objects")
 conn=next(x for x in nodes if x["name"]=="Connections")
 models={int(x["props"][0]):x for x in children(objs,"Model")}
 geo_parents={int(c["props"][1]):int(c["props"][2]) for c in children(conn,"C")
              if len(c["props"])>=3 and c["props"][0]=="OO" and int(c["props"][2]) in models}
 output=[]
 for geom in children(objs,"Geometry"):
  if geom["props"][2]!="Mesh":continue
  uid=int(geom["props"][0]);name=geom["props"][1].split("\x00")[0].split("::")[-1]
  name=name[:-5] if name.endswith("_Mesh") else name
  model=models[geo_parents[uid]]
  props=child(model,"Properties70")
  d={n["props"][0]:n["props"][4:7] for n in children(props,"P")}
  angle=d.get("Lcl Rotation",[0,0,0])
  scale=d.get("Lcl Scaling",[100,100,100])
  translation=d.get("Lcl Translation",[0,0,0])
  ensure(max(abs(float(x)) for x in angle[1:])<0.001 and
         all(abs(float(x)-100)<.01 for x in scale) and
         max(abs(float(x)) for x in translation)<.0001,("Unexpected FBX model pivot/axis/scale",name))
  verts=np.array(values(geom,"Vertices"),dtype=np.float64).reshape(-1,3)
  ang=math.radians(float(angle[0])+90.0)
  v=verts.copy();v[:,1]=math.cos(ang)*verts[:,1]-math.sin(ang)*verts[:,2]
  v[:,2]=math.sin(ang)*verts[:,1]+math.cos(ang)*verts[:,2]
  raw=np.array(values(geom,"PolygonVertexIndex"),dtype=np.int64)
  faces=[];tmp=[]
  for k in raw:
   q=int(k);tmp.append(-q-1 if q<0 else q)
   if q<0:faces.append(tmp);tmp=[]
  ensure(not tmp and all(len(f)==3 for f in faces),(name,"not triangulated"))
  output.append((name,v,faces))
 return output

def tjunctions(v,faces):
 # Coordinate equivalence weld exists ONLY in this temporary QA indexed copy.
 ids={};unique=[];new_faces=[]
 for f in faces:
  row=[]
  for orig in f:
   xyz=v[int(orig)]
   k=tuple(np.round(xyz*1000000).astype(np.int64))
   if k not in ids:ids[k]=len(unique);unique.append(xyz)
   row.append(ids[k])
  new_faces.append(row)
 vv=np.array(unique)
 edges=set()
 for f in new_faces:
  for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])):
   edges.add(tuple(sorted((a,b))))
 found=[]
 for a,b in sorted(edges):
  edge=vv[b]-vv[a];length2=float(edge@edge)
  if length2<1e-14:continue
  for idx,point in enumerate(vv):
   if idx==a or idx==b:continue
   t=float((point-vv[a])@edge/length2)
   if t>1e-5 and t<1-1e-5:
    distance=float(np.linalg.norm(point-(vv[a]+t*edge)))
    if distance<2e-6:found.append({"edge":[a,b],"vertex":idx,"distance_m":distance})
 return found,len(unique),len(edges)

def visible_coplanar_overlaps(parts):
 # Do not conflate deliberate unseen COL_RampDeck collision proxy with visible z-fighting.
 tri=[]
 for name,v,faces in parts:
  if name.startswith("COL_"):continue
  for i,f in enumerate(faces):
   xyz=v[np.array(f,dtype=np.int64)]
   normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);n=float(np.linalg.norm(normal))
   if n<1e-13:continue
   normal/=n
   tri.append((name,i,xyz,normal,xyz.min(axis=0),xyz.max(axis=0)))
 out=[]
 for i,(an,ai,a,na,amin,amax) in enumerate(tri):
  for bn,bi,b,nb,bmin,bmax in tri[i+1:]:
   if an==bn:continue
   if np.any(amin>bmax+1e-6) or np.any(bmin>amax+1e-6):continue
   if abs(abs(float(na@nb))-1)>2e-5:continue
   if float(np.max(np.abs((b-a[0])@na)))>3e-6:continue
   main=int(np.argmax(abs(na)))
   dims=[axis for axis in range(3) if axis!=main]
   pa=Polygon(a[:,dims]);pb=Polygon(b[:,dims])
   if pa.is_valid and pb.is_valid:
    area=float(pa.intersection(pb).area)
    if area>1e-10:
     out.append({"pair":[an,bn],"triangles":[ai,bi],"coplanar_area_m2":area})
 return out

def run_asset(name,path,sha,parts_count,tri_count):
 raw=path.read_bytes()
 ensure(raw.startswith(b"Kaydara FBX Binary"),(name,"not real FBX"))
 ensure(hashlib.sha256(raw).hexdigest()==sha,(name,"wrong file SHA"))
 meshes=mesh_parser(path)
 ensure(len(meshes)==parts_count,(name,"part count"))
 ensure(sum(len(f) for _,_,f in meshes)==tri_count,(name,"triangle count"))
 original=audit_fbxf(path)
 errors=["loose_vertices","nonmanifold_edges","inconsistent_edge_winding",
         "duplicate_faces","degenerate_triangles","zero_uv_area_triangles",
         "normal_mismatch_corners"]
 ensure(all(original["totals"][key]==0 for key in errors),(name,"basic static anomalies",original["totals"]))
 out=[]
 for meshname,v,f in meshes:
  j,nv,ne=tjunctions(v,f)
  out.append({"part":meshname,"triangles":len(f),"unique_position_vertices_1um":nv,
              "unique_position_edges_1um":ne,"t_junction_count":len(j),"witnesses":j[:5]})
  ensure(len(j)==0,(name,meshname,"T-junction candidates",j[:3]))
 overlaps=visible_coplanar_overlaps(meshes)
 ensure(len(overlaps)==0,(name,"visible interpart z-fighting",overlaps[:3]))
 mechanics={}
 if name=="RMP-01":
  deck=next(v for n,v,f in meshes if n=="Deck_Main")
  proxy=next(v for n,v,f in meshes if n=="COL_RampDeck")
  ensure(sorted(map(tuple,np.round(deck,6)))==sorted(map(tuple,np.round(proxy,6))),
         "Intentional hidden collision proxy has diverged from actual deck")
  strips=[]
  for n,v,f in meshes:
   if n.startswith("AntiSlipMark_"):
    gaps=sorted(float(z-.25*x) for x,y,z in v)
    ensure(len(gaps)==8 and all(abs(a+.0004)<2e-5 for a in gaps[:4]) and
           all(abs(a-.003)<2e-5 for a in gaps[4:]),(n,"mount defect",gaps))
    strips.append(n)
  ensure(len(strips)==4,("expected existing 4 ramp strips",strips))
  mechanics={"deck_slope_rise_over_run":.25,"embedded_original_strips":strips,
             "bottom_embed_m":.0004,"visible_strip_top_above_deck_m":.003,
             "COL_RampDeck":"Intentional identical hidden collision geometry"}
 else:
  verts=np.concatenate([v for n,v,f in meshes])
  size=verts.max(axis=0)-verts.min(axis=0)
  ensure(np.max(abs(size-np.array([2,.14,1.1])))<2e-5,
         ("RAI original modular envelope changed",size))
  mechanics={"original_envelope_xyz_m":[2,.14,1.1]}
 return {"asset":name,"current_real_fbx_sha256":sha,"mesh_parts":parts_count,
         "triangles":tri_count,"physical_binary_static_errors":{k:original["totals"][k] for k in errors},
         "T_junctions_actual_2um_tolerance":0,"cross_part_visible_coplanar_overlap_count":0,
         "parts":out,"mechanical_and_modular_witness":mechanics,
         "source_file":path.relative_to(ROOT).as_posix()}

if __name__=="__main__":
 result={"scope":"C01-14 W26 own non-door optional structural RAI-01 and RMP-01; outside 36 P15–P19",
         "method":"ACTUAL exact SHA Blender4 FBX7400; 1um weld ONLY in read-only QA memory copy; 2um Tjunction proximity; 3um coplanarity; 1e-10 m2 overlap area",
         "assets":[run_asset(*v) for v in FILES],
         "status":"STATIC_BINARY_MESH_NO_NEW_DEFECT_CONFIRMED",
         "source_mesh_modified":False,"doors_or_gates_touched":False,
         "unity6_editor":"NOT RUN","independent_C01_02_after_this_audit":"PENDING",
         "owner_next":"Reexport only after new independently confirmed defect; C01-10 real licensed Unity test"}
 target=BASE/"Pass26/QA/W26_ACTUAL_NATIVE_FBX_ADVANCED_STATIC.json"
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"result":result["status"],"assets":[{"id":x["asset"],"parts":x["mesh_parts"],"triangles":x["triangles"],"T_junctions":x["T_junctions_actual_2um_tolerance"],"visible_coplanar_overlaps":x["cross_part_visible_coplanar_overlap_count"]} for x in result["assets"]]},indent=2))
