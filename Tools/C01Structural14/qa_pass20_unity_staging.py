#!/usr/bin/env python3
"""C01-14 W20: read-only, real 4 native binary SHA + source guard checks.

This is NOT Unity compilation, Editor import, prefab PlayMode, or release QA.
Uses authoring branch LFS hydrated bytes and actual current Unity C# sources.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"Assets/C01StructuralPrototypes/P14"
NEW=BASE/"Editor/C01Structures14Pass19SignedUnityQa.cs"
OLD=BASE/"Editor/C01Structures14PrefabBuilder.cs"

NATIVE={
 "RAI-01": {
  "blend": ("Pass17/Native/C01_14_RAI-01_DETAIL17.blend","715bd015029b6f4cfc4126b4b6e0e944cd03c2719f70ceb719d5912baa3e0e42"),
  "fbx": ("Pass17/Native/C01_14_RAI-01_DETAIL17.fbx","f0c8fd590d7752431c869be2f9807209b7632d87a77ab619049c90f60f0ff1fe"),
  "meshes":20,"triangles":424},
 "RMP-01": {
  "blend": ("Pass03/Sources/C01_14_RMP-01_v002.blend","7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa"),
  "fbx": ("Pass03/FBX/C01_14_RMP-01_v002.fbx","97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443"),
  "meshes":6,"triangles":72},
}

def sha256(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()

def ensure(ok,message):
 if not ok: raise AssertionError(message)

def check():
 newer=NEW.read_text(encoding="utf-8")
 legacy=OLD.read_text(encoding="utf-8")
 checks={
  "legacy_no_v001_fbx": "_v001.fbx" not in legacy,
  "legacy_routes_to_safe_importer": "C01Structures14Pass19SignedUnityQa.RunSignedQaOnly()" in legacy,
  "requires_real_unity_6": 'Application.unityVersion.StartsWith("6000."' in newer,
  "requires_active_urp": "GraphicsSettings.currentRenderPipeline" in newer and "Universal" in newer,
  "no_unapproved_merge": "AssetDatabase" in newer and "NO_MERGE" not in newer,
  "checks_blend_and_binary_fbx_sha": "AssertSigned(x.FbxPath,x.FbxSha" in newer and "AssertSigned(x.BlendPath,x.BlendSha" in newer,
  "checks_stage_sha": "AssertSigned(x.Staged,x.FbxSha" in newer,
  "refuses_fbx_pointer": "Kaydara FBX Binary" in newer and 'magic' in newer and "Sha(disk)!=expected" in newer,
  "refuses_existing_prefab": "QA prefab already exists" in newer and "Refusing to overwrite existing QA prefab" in newer,
  "rollback_both_candidate_prefabs": "PASS20_ATOMIC_ROLLBACK" in newer and "foreach(var x in Inputs)" in newer[newer.index("catch\n"):],
  "rollback_new_stages": "foreach(var path in createdStages)" in newer and "AssetDatabase.DeleteAsset(path);" in newer,
  "rollback_new_materials": "foreach(var path in newMaterials)" in newer,
  "no_prod_prefab_output": 'const string QaRoot = Root + "/Pass19/UnityQA";' in newer and 'const string Prefabs = QaRoot + "/Prefabs";' in newer,
  "actual_part_and_tris_gates": "filters.Length!=candidate.Meshes" in newer and "triangleCount!=candidate.Triangles" in newer,
  "names_suffix_normalized": 'EndsWith("_Mesh"' in newer,
  "rmp_dedicated_collision": 'candidate.Id=="RMP-01" && (collisionCount!=1 || visibleParts!=5)' in newer,
  "rai_structural_colliders_only": 'candidate.Id=="RAI-01" && (collisionCount!=4 || visibleParts!=20)' in newer,
  "pivot_preserved": "instance.transform.SetParent(root.transform,false)" in newer,
  "unapproved_release_not_claimed": "external C01-02 and release still PENDING" in newer,
 }
 for key,good in checks.items(): ensure(good,"C# static guard check failed: "+key)
 evidence=[]
 for model,attrs in NATIVE.items():
  ensure(("\""+model+"\"") in newer,"missing current ID "+model)
  ensure(re.search(r"\b"+str(attrs["meshes"])+r"\s*,\s*"+str(attrs["triangles"])+r"\s*\)",newer) is not None,"mesh/triangle pin missing "+model)
  for kind in ("blend","fbx"):
   relative,expected=attrs[kind]
   path=BASE/relative
   ensure(path.is_file(),"Missing actually hydrated native file: "+str(path))
   with path.open("rb") as f: magic=f.read(32)
   ensure(magic.startswith(b"BLENDER") if kind=="blend" else magic.startswith(b"Kaydara FBX Binary"),"LFS POINTER/STUB or wrong signature "+str(path))
   actual=sha256(path)
   ensure(actual==expected,f"FULL SHA mismatch for {model} {kind}: {actual} != {expected}")
   ensure(expected in newer,"Unity importer SHA not pinned: "+model+"/"+kind)
   evidence.append({"id":model,"kind":kind,"path":path.relative_to(ROOT).as_posix(),"sha256":actual,"bytes":path.stat().st_size,"signature":"native"})
 return {"status":"PASS_STATIC_INPUT_SHA_AND_GUARDS_ONLY",
         "scope":"C01-14 optional legacy, outside 36 P15-P19",
         "physical_native_sha_match":"4/4","source_guard_checks":len(checks),
         "source_checks":checks,"real_native":evidence,
         "unity_editor":"NOT RUN","csharp_compilation":"NOT RUN",
         "prefabs":"NOT RUN","independent_C01_02":"PENDING"}

if __name__=="__main__":
 try:
  result=check()
  print(json.dumps(result,indent=2))
 except Exception as exc:
  print(f"C01-14 W20 FAIL-CLOSED: {type(exc).__name__}: {exc}",file=sys.stderr)
  sys.exit(1)
