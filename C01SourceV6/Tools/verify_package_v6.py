"""Verify the exported Unity package against actual project files."""
import hashlib
import json
from pathlib import Path
import tarfile

here=Path(__file__).resolve().parent
project=here/"UnityProject" if (here/"UnityProject/Assets").is_dir() else here.parent.parent
archive_path=project/"C01ShipV6_QA/C01_Ship_Multideck_v6.0.unitypackage"
with tarfile.open(archive_path) as tar:
    contents={m.name:tar.extractfile(m).read() for m in tar if m.isfile()}
paths={v.decode("utf8"):k.rsplit("/",1)[0] for k,v in contents.items() if k.endswith("/pathname")}
checked=0
runtime_checked=0
mismatches=[]
for name,prefix in paths.items():
    path=project/name
    key=prefix+"/asset"
    if not (name.startswith("Assets/C01ShipV6/") or name.startswith("Assets/C01ShipV5/Runtime/")) or not path.is_file() or key not in contents:
        continue
    if name.startswith("Assets/C01ShipV6/"):
        checked+=1
    else:
        runtime_checked+=1
    if path.read_bytes()!=contents[key]:
        mismatches.append(name)
required=["Assets/C01ShipV6/Scenes/C01_Ship_Multideck_v6.unity",
          "Assets/C01ShipV6/Prefabs/C01_SHIP_MULTIDECK_MASTER_V6.prefab",
          "Assets/C01ShipV6/Data/ship_v6.json",
          "Assets/C01ShipV6/Cargo/Runtime/CargoLiftController.cs",
          "Assets/C01ShipV5/Runtime/ShipExplorerV5.cs",
          "Assets/C01ShipV5/Runtime/C01ShipV5.Runtime.asmdef",
          "Assets/C01ShipV5/Runtime/ShipDataV5.cs"]
missing=[name for name in required if name not in paths]
for path in (project/"Assets/C01ShipV6").rglob("*"):
    if path.is_file() and path.suffix!=".meta":
        name=path.relative_to(project).as_posix()
        if name not in paths:
            missing.append(name)
for path in (project/"Assets/C01ShipV5/Runtime").rglob("*"):
    if path.is_file() and path.suffix!=".meta":
        name=path.relative_to(project).as_posix()
        if name not in paths:
            missing.append(name)
model_count=sum(name.startswith("Assets/C01ShipV6/Models/") and name.endswith(".fbx") for name in paths)
if model_count!=394:
    missing.append(f"FBX count: expected 394, found {model_count}")
report=dict(status="PASS" if not mismatches and not missing else "FAIL",
            package_bytes=archive_path.stat().st_size,sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            asset_paths=len(paths),source_files_compared=checked,runtime_files_compared=runtime_checked,fbx_count=model_count,
            mismatches=mismatches,missing_required=missing)
out=project/"C01ShipV6_QA/unitypackage_v6.json"
out.write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(report,indent=2))
raise SystemExit(bool(mismatches or missing))
