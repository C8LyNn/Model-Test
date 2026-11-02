"""C01-15 W20 READ-ONLY independent-intake receipt of existing P15-04..07 native files.
Never exports or saves .blend/.fbx. SHA is measured against current Git LFS pointers.
This is PRODUCER QA, not independent C01-02 certification or Unity Editor.
"""
import bpy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"Assets/C01InteriorProps/P15Wave02"
OUT=ROOT/"C01_PASS20_P15W02_RECEIPT"
OUT.mkdir(parents=True, exist_ok=True)
IDS=("P15-04","P15-05","P15-06","P15-07")
HIST= json.loads((BASE/"QA/file_integrity.json").read_text(encoding="utf-8"))
HIST_BY_NAME={o["relative_path"]:o for o in HIST["files"]}
report={"scope":"EXISTING signed Blender and binary FBX read-only hydration; QA evidence only",
 "owner":"C01-15","ids":list(IDS),"blender_runtime":bpy.app.version_string,
 "source_branch":"c01/props-15-installations-wave02","native_files":{},
 "models":{},"historical_qa_drift":{},"test_failures":[],
 "independent_C01_02":"PENDING","unity6_urp":"NOT_RUN",
 "producer_static":"HOLD","final_approval":"HOLD"}

def must(ok,name,details=None):
 if not ok:report["test_failures"].append({"test":name,"details":details})
 return bool(ok)

def count_mesh_objects():
 objs=[x for x in bpy.data.objects if x.type=="MESH"]
 return {"objects":len(objs),"triangles":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs),
  "uv0":all(o.data.uv_layers.active is not None for o in objs),
  "materials":all(len(o.data.materials)>0 for o in objs),
  "nondegenerate":all(o.data.polygons and all(p.area>1e-12 for p in o.data.polygons) for o in objs),
  "part_names":sorted(o.name for o in objs)}

try:
 for aid in IDS:
  data={}
  for kind in ("blend","fbx"):
   rel= f"Sources/Blender/{aid}.blend" if kind=="blend" else f"Models/FBX/{aid}.fbx"
   f=BASE/rel
   git_path=f.relative_to(ROOT).as_posix()
   ptr=subprocess.run(["git","show",f"HEAD:{git_path}"],cwd=ROOT,
                      capture_output=True,text=True,check=True).stdout
   m=re.search(r"^oid sha256:([0-9a-f]{64})$",ptr,re.M)
   size=re.search(r"^size ([0-9]+)$",ptr,re.M)
   must(bool(m and size),aid+"_"+kind+"_git_pointer")
   b=f.read_bytes() if f.exists() else b""
   digest=hashlib.sha256(b).hexdigest()
   ok_signature=b.startswith(b"BLENDER-") if kind=="blend" else b.startswith(b"Kaydara FBX Binary")
   data[kind]={"path":git_path,"size_bytes":len(b),"sha256":digest,
         "signed_lfs_oid":m.group(1) if m else None,
         "pointer_size":int(size.group(1)) if size else None,
         "exact_lfs_match":bool(m and size and digest==m.group(1) and len(b)==int(size.group(1))),
         "actual_native_magic":ok_signature}
   must(data[kind]["exact_lfs_match"],aid+"_"+kind+"_exact_lfs_match",data[kind])
   must(ok_signature,aid+"_"+kind+"_binary_magic",data[kind])
   historical=HIST_BY_NAME.get(rel,{})
   if historical.get("sha256")!=digest:
    report["historical_qa_drift"][rel]={"old_report_sha256":historical.get("sha256"),
       "current_native_sha256":digest,"historical_report":"QA/file_integrity.json",
       "classification":"STALE_QA_MANIFEST_NOT_SOURCE_MESH_FAIL"}
  report["native_files"][aid]=data
  if len(report["test_failures"])>0:continue
  manifest=json.loads((BASE/"Manifests"/(aid+".json")).read_text(encoding="utf-8"))
  expected_n=manifest["mesh_objects"]
  expected_t=manifest["triangle_count_blender"]
  bpy.ops.wm.open_mainfile(filepath=str(BASE/"Sources/Blender"/(aid+".blend")))
  scene=count_mesh_objects()
  must(scene["objects"]==expected_n and scene["triangles"]==expected_t,
       aid+"_source_part_and_triangles",{"expected_parts":expected_n,"expected_triangles":expected_t,
         "measured_parts":scene["objects"],"measured_triangles":scene["triangles"]})
  must(scene["uv0"] and scene["materials"] and scene["nondegenerate"],aid+"_source_mesh_integrity")
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.ops.import_scene.fbx(filepath=str(BASE/"Models/FBX"/(aid+".fbx")))
  fbx=count_mesh_objects()
  must(fbx["objects"]==scene["objects"] and fbx["triangles"]==scene["triangles"],
       aid+"_real_fbx_reimport_mesh_parity",{"blend":scene["objects"],"fbx":fbx["objects"],
        "blend_tris":scene["triangles"],"fbx_tris":fbx["triangles"]})
  must(fbx["uv0"] and fbx["materials"] and fbx["nondegenerate"],aid+"_fbx_mesh_integrity")
  report["models"][aid]={"blend":scene,"reimport_fbx":fbx,
    "static_producer_result":"PASS" if all([scene["objects"]==expected_n,scene["triangles"]==expected_t,
      fbx["objects"]==scene["objects"],fbx["triangles"]==scene["triangles"],fbx["uv0"],
      fbx["materials"],fbx["nondegenerate"]]) else "HOLD"}
 report["producer_static"]="PASS" if not report["test_failures"] and len(report["models"])==4 else "HOLD"
except Exception as e:
 report["test_failures"].append({"test":"runtime_exception","details":repr(e)})
finally:
 out=OUT/"P15W02_EXISTING_NATIVE_PASS20_RECEIPT.json"
 out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("C01_P15W02_PASS20_RECEIPT",json.dumps({
    "native_ids":len(report["native_files"]),"models_tested":len(report["models"]),
    "source_native_drift_files":len(report["historical_qa_drift"]),
    "qa_failures":report["test_failures"],"producer_static":report["producer_static"],
    "unity":report["unity6_urp"],"independent":report["independent_C01_02"]}))
if report["producer_static"]!="PASS":
 sys.exit(1)
