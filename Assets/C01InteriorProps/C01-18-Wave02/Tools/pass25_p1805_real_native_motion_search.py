"""W25 read-only factual P18-05 REAL original BLEND + binary FBX:
sweep exact original triangles, lift/swing and release variants without
changing native assets. Analyze before authoring fix. NO Unity/doors.
"""
import bpy, sys, pathlib, json, math, hashlib
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
root=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
sha={"blend":"5f98b9e34f346df3ef133e30243aee5b26dc45032c415d643490d00dbdd22f21",
     "fbx":"58e33516ead13e35e8a48228045c67bd53d6caf8de01883a11625fa2961957e5"}
paths={"blend":root/"Sources"/"P18-05.blend","fbx":root/"Models"/"P18-05.fbx"}
for k,p in paths.items():
 assert hashlib.sha256(p.read_bytes()).hexdigest()==sha[k],("physical SHA mismatch",k)
assert paths["blend"].read_bytes()[:8]==b"BLENDER-"
assert paths["fbx"].read_bytes()[:23].startswith(b"Kaydara FBX Binary")
assert bpy.app.version[0]>=4
ANGLES=list(range(0,111,5))
LID=["Case_Lid","Lid_Accent"]
HANDLE=["Carry_Handle_Rail","Carry_Handle_Stem_L","Carry_Handle_Stem_R"]
LATCH=["Front_Latch_L","Front_Latch_R"]
FOOT=["Rubber_Foot_L","Rubber_Foot_R"]
ALL=LID+HANDLE+LATCH+FOOT+["Case_Bottom"]
def read(k):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if k=="blend":bpy.ops.wm.open_mainfile(filepath=str(paths[k]))
 else:bpy.ops.import_scene.fbx(filepath=str(paths[k]))
 bpy.context.view_layer.update()
 m={x.name:x for x in bpy.context.scene.objects if x.type=='MESH'}
 assert set(m)==set(ALL),(k,list(m))
 hinge=bpy.data.objects.get("Lid_HingePivot")
 assert hinge is not None,(k,"hinge missing")
 assert len(m)==10
 count=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in m.values())
 assert count==120,(k,count)
 sources={}
 for n,o in m.items():
  o.data.calc_loop_triangles()
  sources[n]={"vertices":[o.matrix_world @ v.co for v in o.data.vertices],
              "faces":[tuple(t.vertices) for t in o.data.loop_triangles],
              "matrix":o.matrix_world.copy()}
 return {"verts":sources,"hinge":hinge.matrix_world.translation.copy()}
def bvh(v,t):
 return BVHTree.FromPolygons([tuple(x) for x in v],t,all_triangles=True,epsilon=0)
def inspect(src,group,offset_mm,lift_mm,angle_deg):
 original=src["verts"];h=src["hinge"]
 hinge=M_T(h)@Matrix.Rotation(math.radians(-angle_deg),4,'X')@M_T(-h)
 lift=M_T(Vector((0,0,lift_mm/1000)))
 out=M_T(Vector((0,-offset_mm/1000,0)))
 moving=set(LID+ (HANDLE if group in ("handle","all") else [])+
            (LATCH if group=="all" else []))
 changed={}
 for n,geo in original.items():
  M=hinge@lift if n in moving else (out if n in LATCH and group!="all" else Matrix.Identity(4))
  changed[n]=[M@v for v in geo["vertices"]]
 trees={n:bvh(changed[n],geo["faces"]) for n,geo in original.items()}
 # Exclude moving-relative hardware mates; they travel as one rigid assembly.
 pairs={}
 for a in moving:
  for b in original:
   if b in moving:continue
   if b in LATCH and a in LID and group=="lid" and offset_mm==0 and angle_deg==0:
    pass
   hit=trees[a].overlap(trees[b])
   if hit:pairs[a+"/"+b]=len(hit)
 # Specifically avoid resting intersected latches in LOCKED when both move:
 # count all moving -> fixed, genuine strict surface hits.
 return pairs
def M_T(x):return Matrix.Translation(x)
def sweep(src,group,offset,lift):
 poses=[]
 for i in ANGLES:
  hit=inspect(src,group,offset,lift,i)
  poses.append({"degrees":-i,"triangle_pairs":sum(hit.values()),"witness":hit})
 return poses
# check range no new collisions after lid begins moving. Zero required at ALL
# sampled poses incl 0 except locked baseline (accepted rest but not release).
def score(poses):return sum(x["triangle_pairs"] for x in poses)
report={"model":"P18-05","wave":25,"source_sha":sha,"all_angles_degrees":[-x for x in ANGLES],
        "world_motion":"Original Blender WORLD signed -X hinge, translations in world -Y latch release and +Z lid lift",
        "source_real":{},"fbx_real":{},"candidates":[],"best_zero":[],"mesh_changes":0,"fbx_exports":0,"unity":"NOT_RUN"}
src=read("blend")
for key in ["lid","handle","all"]:
 report["source_real"][key]=sweep(src,key,0,0)
# Candidate count 3 groups x 10 offsets x 12 lifts, prefer no silhouette changes.
candidates=[]
for group in ["handle","all","lid"]:
 for offset in ([0,4,8,12,16,20,25,30,40,60] if group!="all" else [0]):
  for lift in [0,2,4,6,8,10,15,20,30,40,60,80]:
   p=sweep(src,group,offset,lift)
   count=score(p)
   c={"group":group,"latch_retract_mm":offset,"lid_lift_mm":lift,
      "total_intersection_pairs":count,
      "worst_per_pose":max(x["triangle_pairs"] for x in p),
      "first_five":[x["triangle_pairs"] for x in p[:5]]}
   candidates.append(c)
report["candidates"]=sorted(candidates,key=lambda x:(x["total_intersection_pairs"],x["lid_lift_mm"],x["latch_retract_mm"]))[:45]
zero=[c for c in candidates if c["total_intersection_pairs"]==0]
report["best_zero"]=sorted(zero,key=lambda x:(x["lid_lift_mm"]+x["latch_retract_mm"],x["lid_lift_mm"]))[:15]
imp=read("fbx")
for key in ["lid","handle","all"]:
 report["fbx_real"][key]=sweep(imp,key,0,0)
report["baseline_parity"]={key:
 [x["triangle_pairs"] for x in report["source_real"][key]]==
 [x["triangle_pairs"] for x in report["fbx_real"][key]] for key in ["lid","handle","all"]}
for c in report["best_zero"][:10]:
 q=sweep(imp,c["group"],c["latch_retract_mm"],c["lid_lift_mm"])
 c["fbx_real_triangle_pairs"]=score(q)
 c["physical_fbx_pass"]=score(q)==0
 c["fbx_pose_counts"]=[x["triangle_pairs"] for x in q]
path=root/"QA"/"Pass25"/"P18-05_ORIGINAL_NATIVE_BLENDER_FBX_HINGE_RELEASE_SEARCH.json"
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(report,indent=2)+"\n")
print("W25_REAL_NATIVE_PHYSICAL_BLENDER_FBX_SEARCH",json.dumps({
 "baseline_blend":[x["triangle_pairs"] for x in report["source_real"]["lid"][:5]],
 "baseline_fbx":[x["triangle_pairs"] for x in report["fbx_real"]["lid"][:5]],
 "baseline_parity":report["baseline_parity"],
 "top":report["candidates"][:8],
 "zero":report["best_zero"][:8]
}),flush=True)
