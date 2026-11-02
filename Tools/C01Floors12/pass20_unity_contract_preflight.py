"""C01-12 W20: real binary FBX ↔ SHA pinned Unity QA-only source contract.
Does NOT start Unity Editor. Checks all actual LFS hydrated bytes and the fail-closed
C# preflight, with results separate from Unity/runtime/material/QA signoff.
"""
import hashlib
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = REPO / "C01StandaloneKits/FloorCeiling/DetailPass17/QA/DETAIL_PASS17_NATIVE_SHA256.json"
EDITOR = REPO / "Assets/C01Floors12Pass18/Editor/RealNativeUnityAudit.cs"
VERSION = REPO / "ProjectSettings/ProjectVersion.txt"
PACKAGES = REPO / "Packages/manifest.json"
OUTPUT = REPO / "C01StandaloneKits/FloorCeiling/DetailPass20/QA/UNITY_EDITOR_INTAKE_PREFLIGHT.json"

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def verify():
    manifest = json.loads(MANIFEST.read_text())
    editor = EDITOR.read_text()
    pkg = json.loads(PACKAGES.read_text())
    ver = VERSION.read_text()
    assert "6000.3.14f1" in ver, "Expected project Unity 6000.3.14f1"
    assert pkg["dependencies"].get("com.unity.render-pipelines.universal") == "17.3.0", "URP version drift"
    assert set(manifest["asset_ids"]) == {"F01", "F02", "C01"}, "C01 legacy kit ID drift"
    assert "PreflightAllThreeImmutableInputs();" in editor
    assert editor.index("PreflightAllThreeImmutableInputs();") < editor.index('EnsureAssetDir(Output+"/Models")')
    assert editor.index('File.Exists(alreadyStaged)') < editor.index('PreflightAllThreeImmutableInputs();')
    assert 'Require(SHA256File(alreadyStaged)==m.fbxHash' in editor
    assert 'Require(SHA256File(src)==m.fbxHash' in editor
    assert 'file.Length>1000' in editor
    assert 'AssetDatabase.ImportAsset(' in editor
    assert 'PrefabUtility.SaveAsPrefabAsset(' in editor
    assert 'new GameObject("PASS18_QA_"' in editor
    assert 'Directory.CreateDirectory(Path.GetDirectoryName(output));' in editor
    assert "PENDING" in editor and "NOT_RUN" in editor
    assert editor.count('new Model("') == 3, "Not a three-only historical QA cohort"
    assert "Assets/C01Floors12Pass18/Generated" in editor
    assert 'UNITY_LICENSE' not in editor and 'UNITY_PASSWORD' not in editor

    rows = []
    for name in ("F01", "F02", "C01"):
        row = manifest["asset_ids"][name]
        source = row["native"]["fbx"]
        native_path = REPO / source["path"]
        raw = native_path.read_bytes()
        assert raw.startswith(b"Kaydara FBX Binary  " + bytes((0, 26, 0))), (name, "not hydrated binary FBX")
        assert len(raw) == source["bytes"], (name, "native bytes not matching manifest")
        digest = sha256(raw)
        assert digest == source["sha256"], (name, "real native SHA mismatch")
        needle = f'new Model("{name}","{pathlib.Path(source["path"]).stem[:-5]}","{digest}"'
        assert needle in editor, (name, "Unity C# pin not current source SHA or ID")
        rows.append({
            "asset_id": name,
            "fbx_path": source["path"],
            "binary_bytes": len(raw),
            "physical_binary_sha256": digest,
            "source_to_unity_editor_sha_pin": "MATCH",
            "binary_magic": "Kaydara FBX Binary v7400",
            "independent_c01_02_final": "PENDING",
            "unity_editor": "NOT_RUN",
        })
    return {
        "owner": "C01-12",
        "wave": "DETAIL PASS20",
        "scope": "3 LEGACY F01/F02/C01 OUTSIDE 36 P15-P19",
        "unity_project_version": "6000.3.14f1",
        "urp_version": "17.3.0",
        "actual_lfs_hydrated_fbx": "PASS_3_OF_3",
        "three_input_preflight_before_any_staging": "SOURCE_CODE_ORDER_VERIFIED_NOT_UNITY_EXECUTED",
        "shader_material_visual": "NOT_RUN",
        "editmode_playmode": "NOT_RUN",
        "unity_compile": "NOT_RUN",
        "independent_c01_02_approval": "PENDING",
        "ship_geometry_changed": False,
        "merge": "NO",
        "models": rows,
    }

if __name__ == "__main__":
    result = verify()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("C01-12 W20 THREE REAL FBX SOURCE SHA + UNITY C# PRESTAGING CONTRACT PASS", flush=True)
    print(json.dumps({"result": result["actual_lfs_hydrated_fbx"],
                      "verified": [(x["asset_id"], x["physical_binary_sha256"]) for x in result["models"]],
                      "unity": result["unity_editor"]}, indent=2))
