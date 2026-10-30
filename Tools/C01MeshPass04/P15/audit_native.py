# C01-15 PASS04: non-destructive, actual native Blender/FBX mesh integrity re-audit
# Does not create new mesh objects or modify the original native source/FBX.
import bpy,bmesh,json,hashlib,math,os,sys
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

WAVE=os.environ.get("C01_P15_WAVE","W01").upper()
R=Path(__file__).resolve().parents[3]
BASE=R/"Assets/C01InteriorProps"/("P15Wave02" if WAVE=="W02" else "P15")
IDS=[f"P15-{n:02d}" for n in (range(4,8) if WAVE=="W02" else range(1,4))]
QA=BASE/"QA/Pass04";QA.mkdir(parents=True,exist_ok=True)
EXPECTED=json.loads((BASE/"QA/Pass03/PASS03_SUMMARY.json").read_text())["models"]

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as fp:
  for data in iter(lambda:fp.read(1<<18),b""):h.update(data)
 return h.hexdigest()
def mesh_objs():
 return sorted((o for o in bpy.data.objects if o.type=="MESH"),key=lambda o:o.name)
def aabb_world(objs):
 v=[o.matrix_world@p.co for o in objs for p in o.data.vertices]
 if not v:return None
 return [[min(x[k] for x in v),max(x[k] for x in v)] for k in range(3)]
def tjunctions(mesh):
 verts=mesh.vertices
 if not verts:return []
 kd=KDTree(len(verts))
 for v in verts:kd.insert(v.co,v.index)
 kd.balance()
 findings=[]
 for e in mesh.edges:
  a=verts[e.vertices[0]].co;b=verts[e.vertices[1]].co
  d=b-a;length=d.length
  if length<1e-8:continue
  for pos,idx,dist in kd.find_range((a+b)*.5,length*.5+1e-6):
   if idx in e.vertices:continue
   t=(pos-a).dot(d)/(length*length)
   if 1e-6<t<1-1e-6 and (pos-a-t*d).length<1e-6:
    findings.append((e.index,idx))
 return findings
def collision_candidate_pairs(mesh):
 # Blender's REAL source tessellation, not surrogate geometry.
 mesh.calc_loop_triangles()
 triangles=[tuple(tr.vertices) for tr in mesh.loop_triangles]
 if len(triangles)<2:return 0,[]
 bv=BVHTree.FromPolygons([v.co for v in mesh.vertices],triangles,all_triangles=True,epsilon=1e-8)
 examples=[];found=set()
 for i,j in bv.overlap(bv):
  if i>=j or (i,j) in found:continue
  if set(triangles[i]) & set(triangles[j]):continue
  found.add((i,j))
  if len(examples)<8:examples.append((i,j))
 return len(found),examples
def metrics(o):
 mesh=o.data;mesh.calc_loop_triangles()
 bm=bmesh.new();bm.from_mesh(mesh)
 bm.verts.ensure_lookup_table();bm.verts.index_update()
 bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
 polygon_count=Counter(tuple(sorted(v.index for v in f.verts)) for f in bm.faces)
 src_tri=[tuple(lt.vertices) for lt in mesh.loop_triangles]
 degenerate_tri=sum(((mesh.vertices[t[1]].co-mesh.vertices[t[0]].co).cross(mesh.vertices[t[2]].co-mesh.vertices[t[0]].co)).length<1e-10 for t in src_tri)
 source_area=sum(p.area for p in mesh.polygons)
 tri_area=sum(.5*((mesh.vertices[t[1]].co-mesh.vertices[t[0]].co).cross(mesh.vertices[t[2]].co-mesh.vertices[t[0]].co)).length for t in src_tri)
 uv=mesh.uv_layers.active
 uv_finite=uv is not None and all(math.isfinite(x) for d in uv.data for x in d.uv)
 smooth=sum(p.use_smooth for p in mesh.polygons)
 boundaries=sum(e.is_boundary for e in bm.edges)
 overfull=sum(len(e.link_faces)>2 for e in bm.edges)
 zero_edges=sum(e.calc_length()<1e-9 for e in bm.edges)
 loose_verts=sum(not v.link_edges and not v.link_faces for v in bm.verts)
 duplicate_faces=sum(c-1 for c in polygon_count.values() if c>1)
 winding=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
 volume=bm.calc_volume(signed=True) if bm.faces and all(e.is_manifold for e in bm.edges) else None
 bad_poly=sum(f.calc_area()<1e-12 for f in bm.faces)
 bm.free()
 tj=tjunctions(mesh)
 selfcount,selfexamples=collision_candidate_pairs(mesh)
 return {"vertices":len(mesh.vertices),"edges":len(mesh.edges),"faces":len(mesh.polygons),
  "triangles":len(src_tri),"triangulation_degenerate":degenerate_tri,
  "ngons_over_4":sum(len(p.vertices)>4 for p in mesh.polygons),
  "triangulation_area_error_m2":abs(source_area-tri_area),
  "source_area_m2":source_area,
  "zero_area_faces":bad_poly,"zero_length_edges":zero_edges,"loose_vertices":loose_verts,
  "duplicate_index_faces":duplicate_faces,"boundary_edges":boundaries,"nonmanifold_over_2":overfull,
  "inconsistent_winding":winding,"signed_volume_m3":volume,
  "t_junctions_local_count":len(tj),"t_junctions_first":tj[:12],
  "bvh_self_intersection_nonadjacent_candidates":selfcount,
  "bvh_self_intersection_examples":selfexamples,
  "UV0_present_and_finite":uv_finite,
  "material_slots":len(mesh.materials),"smooth_polygons":smooth,
  "local_scale":list(o.scale),"parent":o.parent.name if o.parent else None}
def tri_key(pts):
 return tuple(sorted(tuple(round(float(q),6) for q in p) for p in pts))
def coplanar_duplicate_between_parts(objs):
 bucket=defaultdict(set)
 for o in objs:
  o.data.calc_loop_triangles()
  for tr in o.data.loop_triangles:
   tri=[o.matrix_world@o.data.vertices[i].co for i in tr.vertices]
   bucket[tri_key(tri)].add(o.name)
 pairs=Counter()
 for names in bucket.values():
  if len(names)>1:
   names=sorted(names)
   for i in range(len(names)):
    for j in range(i+1,len(names)):
     pairs[(names[i],names[j])]+=1
 return [{"mesh_a":p[0],"mesh_b":p[1],"shared_exact_triangles":n} for p,n in pairs.most_common(40)]
def fail_hard(part_metrics,aid):
 issues=[]
 for n,m in part_metrics.items():
  for field in ("triangulation_degenerate","zero_area_faces","zero_length_edges","loose_vertices","duplicate_index_faces","nonmanifold_over_2","inconsistent_winding","t_junctions_local_count"):
   if m[field]:issues.append(n+":"+field+"="+str(m[field]))
  if m["triangulation_area_error_m2"]>max(1e-7,m["source_area_m2"]*1e-5):issues.append(n+":triangulation_area")
  if not m["UV0_present_and_finite"]:issues.append(n+":UV0")
  if m["material_slots"]<1:issues.append(n+":missing_material")
  if m["signed_volume_m3"] is not None and m["signed_volume_m3"] < -1e-8:
   issues.append(n+":inward_closed_volume")
  if any(abs(v-1)>1e-6 for v in m["local_scale"]):issues.append(n+":non_unit_scale")
  if m["boundary_edges"] and not (aid=="P15-07" and n in ("Gauge_Face_0","Gauge_Face_1") and m["boundary_edges"]==24):
   issues.append(n+":unexpected_open_boundary")
 return issues
def inspect_fbx(aid,origin,bounds):
 path=BASE/"Models/FBX"/(aid+".fbx")
 signature=path.open("rb").read(24).startswith(b"Kaydara FBX Binary")
 if not signature:return {"result":"FAIL","error":"not binary FBX"}
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 imported=mesh_objs()
 imported_metrics={o.name:metrics(o) for o in imported}
 source_tris=sum(m["triangles"] for m in origin.values())
 imported_tris=sum(m["triangles"] for m in imported_metrics.values())
 source_permesh={n:m["triangles"] for n,m in origin.items()}
 imported_permesh={n:m["triangles"] for n,m in imported_metrics.items()}
 same_names=set(source_permesh)==set(imported_permesh)
 comparable={"source_parts":len(source_permesh),"fbx_import_parts":len(imported_permesh),
 "source_tris":source_tris,"fbx_import_tris":imported_tris,"same_mesh_names":same_names,
 "triangle_count_per_mesh_equal":same_names and source_permesh==imported_permesh,
 "UV0_all":all(m["UV0_present_and_finite"] for m in imported_metrics.values()),
 "materials_all":all(m["material_slots"]>0 for m in imported_metrics.values()),
 "degenerate_triangles":sum(m["triangulation_degenerate"] for m in imported_metrics.values()),
 "unexpected_boundaries":sum(m["boundary_edges"] for n,m in imported_metrics.items() if not(aid=="P15-07" and n in ("Gauge_Face_0","Gauge_Face_1"))),
 "source_bounding_box":bounds,
 "import_bounding_box":aabb_world(imported)}
 comparable["bbox_delta_max_m"]=max(abs(comparable["source_bounding_box"][k][i]-comparable["import_bounding_box"][k][i]) for k in range(3) for i in range(2)) if comparable["import_bounding_box"] and comparable["source_bounding_box"] else None
 result="PASS" if (signature and comparable["triangle_count_per_mesh_equal"] and comparable["UV0_all"] and comparable["materials_all"] and comparable["degenerate_triangles"]==0 and comparable["unexpected_boundaries"]==0 and (comparable["bbox_delta_max_m"] is not None and comparable["bbox_delta_max_m"]<.005)) else "FAIL"
 return {"result":result,"fbx_sha256":sha(path),"checks":comparable}
allreports={}
for aid in IDS:
 src=BASE/"Sources/Blender"/(aid+".blend")
 if src.open("rb").read(8)!=b"BLENDER-":raise RuntimeError("Native .blend missing or Git LFS pointer: "+str(src))
 bpy.ops.wm.open_mainfile(filepath=str(src))
 objs=mesh_objs()
 bounds=aabb_world(objs)
 byname={o.name:metrics(o) for o in objs}
 exceptions={"P15-07":{"Gauge_Face_0":24,"Gauge_Face_1":24}}.get(aid,{})
 actual={n:m["boundary_edges"] for n,m in byname.items() if m["boundary_edges"]}
 checks=fail_hard(byname,aid)
 if actual!=exceptions:checks.append("boundary_exception_map_mismatch")
 overlays=coplanar_duplicate_between_parts(objs)
 totals={k:sum(m[k] for m in byname.values()) for k in ("vertices","edges","faces","triangles","boundary_edges","triangulation_degenerate","t_junctions_local_count","bvh_self_intersection_nonadjacent_candidates")}
 base=EXPECTED[aid]["after"]["total"]
 for k in ("vertices","edges","faces","triangles"):
  if base[k]!=totals[k]:checks.append("PASS03_approved_source_mismatch:"+k)
 import_result=inspect_fbx(aid,byname,bounds)
 if import_result["result"]!="PASS":checks.append("FBX_roundtrip_mismatch")
 doc={"id":aid,"scope":"C01-15 PASS04 native BLEND source and genuine binary FBX reimport; no surrogate geometry",
  "blender":bpy.app.version_string,"source_sha256":sha(src),
  "pass03_expected":{k:base[k] for k in ("vertices","edges","faces","triangles")},
  "source_actual":totals,"parts":byname,"intentional_open_boundary_parts":exceptions,
  "exact_cross_mesh_coplanar_triangle_pairs":overlays,
  "self_intersection_status":"BVH_TRIANGLE_CANDIDATES_ONLY_NOT_CERTIFIED",
  "cross_mesh_overlap_status":"EXACT_COPLANAR_TRIANGLE_CANDIDATES_ONLY_REVIEW_REQUIRED",
  "t_junction_status":"EXACT_SAME_MESH_VERTEX_ON_NONINCIDENT_EDGE_TESTED",
  "source_defects_blocking":checks,"fbx":import_result,"native_topology":"PASS" if not checks else "FAIL",
  "unity":"NOT RUN","independent_qa":"NOT RUN"}
 allreports[aid]=doc
 (QA/(aid+"_native_audit.json")).write_text(json.dumps(doc,indent=2)+"\n")
 print("PASS04",aid,doc["native_topology"],"tris",totals["triangles"],"errors",checks,"cross_coplanar",len(overlays),flush=True)
summary={"wave":WAVE,"blender":bpy.app.version_string,"scope":"current native sources and exact FBX in producer branch",
 "models":{id:{"source_sha256":d["source_sha256"],"fbx_sha256":d["fbx"].get("fbx_sha256"),
 "V_E_F_T":[d["source_actual"][n] for n in ("vertices","edges","faces","triangles")],
 "native":d["native_topology"],"fbx":d["fbx"]["result"],
 "same_mesh_T_junctions":d["source_actual"]["t_junctions_local_count"],
 "self_overlap_candidate_count":d["source_actual"]["bvh_self_intersection_nonadjacent_candidates"],
 "exact_cross_mesh_duplicate_triangle_pair_groups":len(d["exact_cross_mesh_coplanar_triangle_pairs"]),
 "issues":d["source_defects_blocking"]} for id,d in allreports.items()},
 "unity":"NOT RUN","independent_qa":"NOT RUN"}
summary["status"]="PASS" if all(x["native"]=="PASS" and x["fbx"]=="PASS" for x in summary["models"].values()) else "FAIL"
(QA/"PASS04_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print("PASS04_SUMMARY",summary["status"],len(IDS),"models",flush=True)
if summary["status"]!="PASS":sys.exit(1)
