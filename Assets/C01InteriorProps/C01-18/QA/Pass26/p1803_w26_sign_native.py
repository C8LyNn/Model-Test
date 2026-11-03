"""Update only P18-03 current-producer signed SHA after real native Blender QA.
Do not overwrite historical QA receipts or assert Unity/independent PASS.
"""
import hashlib, pathlib, json, re, sys
root=pathlib.Path(sys.argv[1])
p=root/"Assets/C01InteriorProps/C01-18"
qa=p/"QA/Pass26"
report=json.loads((qa/"P18-03_W26_REAL_BLENDER_FBX_QA.json").read_text())
assert report["classification"]=="PRODUCER_NATIVE_CLEARANCE_PASS__INDEPENDENT_AND_UNITY_HOLD"
obj=p/"Models/P18-03.obj";blend=p/"Sources/P18-03.blend";fbx=p/"Models/P18-03.fbx"
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
values={"source_obj_sha256":sha(obj),"native_blend_sha256":sha(blend),"native_fbx_sha256":sha(fbx)}
assert all(values[{"source_obj_sha256":"source_obj_sha256","native_blend_sha256":"source_blend_sha256","native_fbx_sha256":"exported_fbx_sha256"}[k]]==v for k,v in values.items()) if False else True
assert report["input_binary_provenance"]["source_obj_sha256"]==values["source_obj_sha256"]
assert report["input_binary_provenance"]["source_blend_sha256"]==values["native_blend_sha256"]
assert report["input_binary_provenance"]["exported_fbx_sha256"]==values["native_fbx_sha256"]
assert blend.read_bytes().startswith(b"BLENDER-")
assert fbx.read_bytes().startswith(b"Kaydara FBX Binary")
editor=p/"Editor/BuildWave01CargoPrefabs.cs"
source=editor.read_text()
source,n=re.subn(r'(const string SignedP1803FbxSha256 = ")[0-9a-f]{64}(";) ',
                 lambda m:m.group(1)+values["native_fbx_sha256"]+m.group(2)+" ",source)
if n==0:
 source,n=re.subn(r'(const string SignedP1803FbxSha256 = ")[0-9a-f]{64}(";)',
                  lambda m:m.group(1)+values["native_fbx_sha256"]+m.group(2),source)
assert n==1,"expected exactly one P18-03 signed digest guard"
source,n=re.subn(r'const int signedLength=\d+;',f"const int signedLength={fbx.stat().st_size};",source)
assert n==1,"expected exactly one P18-03 signed length guard"
editor.write_text(source)
manifest_path=p/"Manifests/manifest.json"
manifest=json.loads(manifest_path.read_text())
matches=[i for i in manifest["assets"] if i["id"]=="P18-03"]
assert len(matches)==1
asset=matches[0]
previous={k:asset[k] for k in values}
asset.update(values)
asset["independent_QA"]="W26 newly generated signed native FBX; C01-02 independent exact-SHA retest PENDING"
asset["blender_fbx_roundtrip"]="W26 actual Blender 4 native FBX roundtrip and 8/8 hub/fork 2mm clearance PASS"
asset["fbx_unity_import"]="NOT RUN"
asset["prefab_unity_import"]="NOT RUN"
manifest["wave26"]={
 "owner":"C01-18","model":"P18-03","scope":"original eight hub mesh vertex X positions only",
 "baseline_native":previous,"new_native":values,"new_binary_fbx_size":fbx.stat().st_size,
 "sha_guard":"BuildWave01CargoPrefabs.cs updated to exact new real FBX byte SHA and length",
 "producer_actual_blender_fbx":"PASS see Assets/C01InteriorProps/C01-18/QA/Pass26/P18-03_W26_REAL_BLENDER_FBX_QA.json",
 "independent_C01_02":"PENDING","real_Unity_6_URP":"NOT_RUN","doors":"EXTERNAL_CLAUDE_FREEZE",
 "original_P18_01_P18_02":"UNMODIFIED","release":"DRAFT_HOLD","merge":"NONE"}
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"current_P18_03_native":values,"file_bytes":fbx.stat().st_size,
                  "old_signed":previous,"independent":"PENDING","Unity":"NOT_RUN"},indent=2))
