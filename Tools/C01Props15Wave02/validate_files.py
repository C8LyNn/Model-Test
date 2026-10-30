import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parents[2]/"Assets/C01InteriorProps/P15Wave02"
ids=("P15-04","P15-05","P15-06","P15-07")
files=[]
for aid in ids:
 files.extend((base/"Sources/Blender"/(aid+".blend"),base/"Models/FBX"/(aid+".fbx"),base/"Manifests"/(aid+".json")))
 files.extend(base/"Previews/Blender"/(aid+"_"+v+".png") for v in ("front","iso","side"))
files.append(base/"QA/blender_roundtrip.json")
out=[]
for p in files:
 data=p.read_bytes() if p.is_file() else b""
 ok=(p.suffix==".blend" and data.startswith(b"BLENDER") or
     p.suffix==".fbx" and data.startswith(b"Kaydara FBX Binary") or
     p.suffix==".png" and data.startswith(bytes([137,80,78,71,13,10,26,10])) or
     p.suffix==".json" and len(data)>80)
 # Guard against LFS pointer files in actual local build
 if data.startswith(b"version https://git-lfs.github.com/spec/v1"):ok=False
 out.append({"relative_path":str(p.relative_to(base)),"size_bytes":len(data),
             "sha256":hashlib.sha256(data).hexdigest() if data else None,"status":"PASS" if ok else "FAIL"})
report={"method":"actual Blender / FBX / PNG signatures, file hash, JSON presence (not Unity)","files":out,
        "result":"PASS" if all(x["status"]=="PASS" for x in out) else "FAIL","independentQA":"NOT RUN","unityImport":"NOT RUN"}
(base/"QA/file_integrity.json").write_text(json.dumps(report,indent=2)+"\n")
print("P15 WAVE02 file integrity",report["result"],len(out),"files")
for x in out:
 if x["status"]!="PASS":print("FAIL",x)
if report["result"]!="PASS":raise SystemExit(1)
