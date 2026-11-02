"""C01-16 W20: verify immutable git LFS OIDs and exact Blender roundtrip receipts.
This verifies signed pointer/metadata consistency, NOT physical hydrated FBX import
or independent C01-02 approval. Never exports or edits 3D assets.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CURRENT = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
W01 = subprocess.check_output(["git", "rev-parse", "refs/remotes/origin/c01/props-16-lighting"], cwd=ROOT, text=True).strip()
RECEIPT_PATH = "C01Source/LightingW02/MeshRepairPASS17/GENUINE_BLENDER_SHA_AND_QA.json"
PTR = re.compile(r"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?")
SHA = re.compile(r"^[0-9a-f]{64}$")

def git_file(commit, path):
    return subprocess.check_output(["git", "show", commit + ":" + path], cwd=ROOT)

def lfs_record(commit, path):
    raw = git_file(commit, path).decode("utf-8")
    match = PTR.fullmatch(raw)
    if match is None:
        raise AssertionError("Missing real Git LFS pointer: " + path)
    return match.group(1), int(match.group(2))

receipt = json.loads(git_file(CURRENT, RECEIPT_PATH))
models = receipt["models"]
if len(models) != 7 or set(x["id"] for x in models) != {"P16-0"+str(i) for i in range(1,8)}:
    raise AssertionError("Seven unique expected P16 source IDs required")

rows=[]
for asset in sorted(models, key=lambda x:x["id"]):
    aid = asset["id"]
    w01 = int(aid[-2:]) <= 3
    commit = W01 if w01 else CURRENT
    source = "C01Source/Lighting" + ("" if w01 else "W02")
    blend_path = source + "/Blender/" + aid + ".blend"
    fbx_path = source + "/FBX/" + aid + ".fbx"
    report_path = source + "/MeshRepairPASS04/" + aid + "/blender_binary_fbx_roundtrip.json"
    native_blend, blend_bytes = lfs_record(commit, blend_path)
    native_fbx, fbx_bytes = lfs_record(commit, fbx_path)
    report = json.loads(git_file(commit, report_path))
    expected_blend = asset["blend_sha256"]
    expected_fbx = asset["fbx_sha256"]
    if not SHA.fullmatch(expected_blend) or not SHA.fullmatch(expected_fbx):
        raise AssertionError(aid+": truncated or malformed SHA256 receipt")
    if not (native_blend == expected_blend == report["blend_sha256"]):
        raise AssertionError(aid+": native BLEND SHA discordance between LFS, PASS17 and original roundtrip")
    if not (native_fbx == expected_fbx == report["binary_fbx_sha256"]):
        raise AssertionError(aid+": binary FBX SHA discordance between LFS, PASS17 and original roundtrip")
    if report["result"] != "PASS" or report["asset"] != aid or report["blender_version"] != "4.0.2":
        raise AssertionError(aid+": unsupported original Blender exporter receipt")
    if report["fbx_bytes"] != fbx_bytes or asset["fbx_bytes"] != fbx_bytes:
        raise AssertionError(aid+": FBX size drift")
    rows.append({
        "id": aid,
        "source_commit": commit,
        "native_blend_sha256_lfs": native_blend,
        "native_fbx_sha256_lfs": native_fbx,
        "native_blend_bytes_lfs": blend_bytes,
        "native_fbx_bytes_lfs": fbx_bytes,
        "original_roundtrip_result": report["result"],
        "pointer_receipt_consistency": "PASS",
        "c01_02_independent": "PENDING",
        "unity_editor": "NOT_RUN"
    })
out=ROOT/"C01Source/LightingW02/MeshRepairPASS20/W20_SIGNED_POINTER_RECEIPT.json"
out.parent.mkdir(parents=True, exist_ok=True)
output = {
    "gate": "GIT_LFS_POINTER_AND_ORIGINAL_BLENDER_ROUNDTRIP_RECEIPT_RECONCILIATION",
    "result": "PASS_POINTER_METADATA_7_OF_7",
    "w01_producer_commit": W01,
    "w02_producer_commit": CURRENT,
    "original_blender_workflow_w01": 41348140241,
    "original_blender_workflow_w02": 41348144803,
    "warning": "A Git LFS pointer is not a physical hydrated FBX. Original physical binaries and imported Blender QA from prior successful actions. This report is SHA inventory only.",
    "not_reexported": True,
    "independent_c01_02": "PENDING",
    "unity_editor": "NOT_RUN",
    "rows": rows
}
out.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
print("C01_16_W20_SIGNED_LFS_SHA_RECEIPTS_PASS",len(rows),"7/7; NO REEXPORT; NO UNITY CLAIM")
