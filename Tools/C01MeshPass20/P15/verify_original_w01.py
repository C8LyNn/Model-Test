"""C01-15 W20 existing P15-01/02 full-native hydration and FBX import receipt. NO exports."""
import bpy
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"Assets/C01InteriorProps/P15"
OUT=ROOT/"C01_PASS20_P15W01_RECEIPT"
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((BASE/"QA/blender_export_validation.json").read_text())
old={x["path"]:x for x in manifest["files"]}
spec=json.loads((BASE/"Sources/geometry_spec.json").read_text())
report={"scope":"C01-15 existing exact native P15-01 P15-02 only; no re-export",
 "owner":"C01-15","blender":bpy.app.version_string,"models":{},"files":{},
 "failures":[],"independent_C01_02":"PENDING","unity":"NOT_RUN",
 "final":"HOLD"}
def chk(cond,name,details=None):
 if not cond:report["failures"].append({"test":name,"details":details})
def metadata():
 meshes=[o for o in bpy.data.objects if o.type=="MESH"]
 return dict(meshes=len(meshes),
   triangles=sum(sum(len(poly.vertices)-2 for poly in o.data.polygons) for o in meshes),
   uv0=all(o.data.uv_layers.active is not None for o in meshes),
   material=all(len(o.data.materials)>0 for o in meshes),
   normals=all(o.data.polygons and all(p.area>1e-12 for p in o.data.polygons) for o in meshes))
try:
 for aid in ["P15-01","P15-02"]:
  for kind in ["blend","fbx"]:
   rel=f"Sources/Blender/{aid}.blend" if kind=="blend" else f"Models/FBX/{aid}.fbx"
   p=BASE/rel
   git_path=p.relative_to(ROOT).as_posix()
   pointer=subprocess.run(["git","show","HEAD:"+git_path],cwd=ROOT,capture_output=True,text=True,check=True).stdout
   m=re.search(r"^oid sha256:([0-9a-f]{64})$",pointer,re.M)
   s=re.search(r"^size ([0-9]+)$",pointer,re.M)
   b=p.read_bytes() if p.exists() else b""
   sha=hashlib.sha256(b).hexdigest()
   sig=b.startswith(b"BLENDER-") if kind=="blend" else b.startswith(b"Kaydara FBX Binary")
   exact=bool(m and s and m.group(1)==sha and int(s.group(1))==len(b))
   old_info=old.get(git_path,{})
   report["files"][git_path]={"sha256":sha,"bytes":len(b),"signed_oid":m.group(1) if m else None,
    "exact_lfs_match":exact,"binary_signature":sig,
    "historical_manifest_sha_match":old_info.get("sha256")==sha}
   chk(exact and sig and old_info.get("sha256")==sha,aid+"_"+kind+"_physical_sha")
  if report["failures"]:continue
  expected_parts=sum(1 for p in spec["parts"] if p["asset"]==aid)
  bpy.ops.wm.open_mainfile(filepath=str(BASE/"Sources/Blender"/(aid+".blend")))
  src=metadata()
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.ops.import_scene.fbx(filepath=str(BASE/"Models/FBX"/(aid+".fbx")))
  fbx=metadata()
  chk(src["meshes"]==expected_parts and fbx["meshes"]==expected_parts and
    src["triangles"]==fbx["triangles"] and all([src["uv0"],src["material"],src["normals"],
    fbx["uv0"],fbx["material"],fbx["normals"]]),aid+"_real_blender_and_fbx_part_tri_uv_material",
    {"expected_parts":expected_parts,"source":src,"fbx":fbx})
  report["models"][aid]={"source":src,"fbx":fbx,"expected_parts":expected_parts}
except Exception as e:
 report["failures"].append({"test":"exception","details":repr(e)})
finally:
 report["producer_native_static"]="PASS" if not report["failures"] and len(report["models"])==2 else "HOLD"
 (OUT/"P15W01_EXISTING_NATIVE_PASS20_RECEIPT.json").write_text(json.dumps(report,indent=2)+"\n")
 print("C01_P15W01_W20_RECEIPT",json.dumps({"models":len(report["models"]),"files":len(report["files"]),
  "failures":report["failures"],"producer_static":report["producer_native_static"]}))
if report["producer_native_static"]!="PASS":sys.exit(1)
