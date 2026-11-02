#!/usr/bin/env python3
"""C01-17 / W21: precise P17-03 rotating PivotAnchorVisual clearance fix.

Modify *existing indexed glTF geometry* only: reduce local Z half-depth
35mm -> 18mm. Preserve pivot, hierarchy, X/Y coordinates, normals, UV0,
faces, and source OBJ parity. Fail closed on unexpected immutable inputs.
"""
import base64
import hashlib
import json
import math
import struct
from pathlib import Path
from pass19_author_clearance import check_parity

ROOT = Path(__file__).resolve().parents[2]
GLTF = ROOT / "Assets/C01InteriorProps/Models/P17-03.gltf"
OBJ = ROOT / "C01InteriorProps_Source/MeshText/P17-03.obj.txt"
SPEC = ROOT / "C01InteriorProps_Source/Specs/P17-03.json"
QA = ROOT / "C01InteriorProps_Source/QA/PASS21/P17-03_SOURCE_ANCHOR_CLEARANCE_QA.json"
EXPECTED = {
    GLTF: "04e2757972469b545ee4973e1ec9a939aca08d599e87aeb3f6757f93e9f30932",
    OBJ: "cfbddf12ce3ec6711c80763935c12e6030b9403272f2b75088b7c9595c9f8394",
    SPEC: "3ee75256f3aec670e9f1f4ab66984feab34ac04ada3712ecd268c6f6d982acd3",
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path, expected in EXPECTED.items():
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"Refusing non-W19 source mutation: {path}: {actual} != {expected}")

g = json.loads(GLTF.read_text())
s = json.loads(SPEC.read_text())
obj = OBJ.read_text()
assert s["id"] == "P17-03" and s["expectedTriangleCount"] == 464
assert len(s["children"]) == 20 and len(g["nodes"]) == 22 and len(g["meshes"]) == 13
nodes = {n["name"]: (i, n) for i, n in enumerate(g["nodes"])}
pivot_id, pivot = nodes["LeverPivot"]
anchor_id, anchor = nodes["PivotAnchorVisual"]
assert pivot["translation"] == [0, .35, -.015]
assert [g["nodes"][i]["name"] for i in pivot["children"]] == ["LeverShaft", "LeverGrip", "PivotAnchorVisual"]
assert anchor["translation"] == [0, 0, 0] and anchor["mesh"] == 9
mesh = g["meshes"][9]
assert mesh["name"] == "PivotAnchorVisual" and len(mesh["primitives"]) == 1
primitive = mesh["primitives"][0]
accessor = g["accessors"][primitive["attributes"]["POSITION"]]
view = g["bufferViews"][accessor["bufferView"]]
blob_index = view["buffer"]
assert accessor["componentType"] == 5126 and accessor["type"] == "VEC3" and accessor["count"] == 24
assert accessor["min"] == [-.0425, -.0125, -.035] and accessor["max"] == [.0425, .0125, .035]
uri = g["buffers"][blob_index]["uri"]
prefix = "data:application/octet-stream;base64,"
assert uri.startswith(prefix)
original_bytes = base64.b64decode(uri[len(prefix):], validate=True)
assert len(original_bytes) == g["buffers"][blob_index]["byteLength"]
raw = bytearray(original_bytes)
start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
stride = view.get("byteStride", 12)
assert stride == 12 and start + 12 * accessor["count"] <= len(raw)
original_vertices, revised_vertices = [], []
for i in range(accessor["count"]):
    offset = start + i * stride
    x, y, z = struct.unpack_from("<fff", raw, offset)
    if not math.isclose(abs(z), .035, abs_tol=1e-6):
        raise RuntimeError(f"Unexpected anchor Z on vertex {i}: {z}")
    new_z = math.copysign(.018, z)
    struct.pack_into("<f", raw, offset + 8, new_z)
    original_vertices.append((x, y, z))
    revised_vertices.append((x, y, new_z))
assert all(old[:2] == new[:2] for old, new in zip(original_vertices, revised_vertices))
assert len({round(v[2], 5) for v in revised_vertices}) == 2
accessor["min"][2] = -.018
accessor["max"][2] = .018
g["buffers"][blob_index]["uri"] = prefix + base64.b64encode(raw).decode("ascii")

# The human-readable OBJ is the same original, source-derived mesh at neutral pose.
# Only its existing PivotAnchorVisual vertex Z coordinates change.
lines = obj.splitlines(keepends=True)
inside = False
updated_obj_vertices = 0
out = []
for line in lines:
    if line.startswith("o "):
        inside = line.strip() == "o PivotAnchorVisual"
    if inside and line.startswith("v "):
        parts = line.rstrip("\n").split()
        assert len(parts) == 4
        z = float(parts[3])
        assert abs(z - (-.05)) < 1e-6 or abs(z - .02) < 1e-6, z
        parts[3] = f"{(-.033 if z < 0 else .003):.6f}"
        line = " ".join(parts) + "\n"
        updated_obj_vertices += 1
    out.append(line)
assert updated_obj_vertices == 24
new_obj = "".join(out)
parity = check_parity(g, new_obj)
assert parity["mismatched_triangles_at_1um"] == 0

part = next(c for c in s["children"] if c["name"] == "PivotAnchorVisual")
assert part["parent"] == "LeverPivot" and part["size"] == [.085, .025, .07]
part["size"] = [.085, .025, .036]
s["version"] = "0.3.1"
s["state"] = "PASS21_SOURCE_ANCHOR_CLEARANCE__NATIVE_QA_PENDING"
s["detailPass21"] = {
    "defect": "C01-02 actual FBX MOTION_FAIL: PivotAnchorVisual intersects fixed Housing at +/-30..45 degrees",
    "fix": "Only existing PivotAnchorVisual mesh local Z half depth 35mm to 18mm; 24 vertex Z values; no new parts",
    "leverPivotUnchanged": [0, .35, -.015],
    "anchorParentUnchanged": "LeverPivot",
    "topCapLeverSocketUnchanged": True,
    "meshParts": 20, "triangles": 464, "UV0NormalsMaterialsUnchanged": True,
    "unity": "NOT RUN",
}
# A source-space swept vertical clearance lower bound, not a substitute for Blender BVH.
housing_top = .213 + .218 / 2
gaps = []
for deg in range(-45, 46, 5):
    theta = math.radians(deg)
    bottom = min(.35 + math.cos(theta)*v[1] - math.sin(theta)*v[2] for v in revised_vertices)
    gaps.append({"degrees": deg, "anchor_min_world_y": bottom, "housing_top_y": housing_top,
                 "separation_m": bottom-housing_top})
assert len(gaps) == 19 and min(x["separation_m"] for x in gaps) > .005
GLTF.write_text(json.dumps(g, separators=(",", ":")) + "\n")
OBJ.write_text(new_obj)
SPEC.write_text(json.dumps(s, indent=2) + "\n")
QA.parent.mkdir(parents=True, exist_ok=True)
report = {"asset":"P17-03", "gate":"SOURCE_ONLY__BLENDER_FBX_NOT_YET_RUN",
          "original_source_SHA256": {str(p.relative_to(ROOT)): h for p, h in EXPECTED.items()},
          "new_source_SHA256": {str(p.relative_to(ROOT)): sha(p) for p in EXPECTED},
          "changes": "Existing PivotAnchorVisual only: 24 local Z changes; 0 X/Y; no indices/normals/UV/materials/pivot/hierarchy changes",
          "triangle_parity": parity, "housing_clearance_19_source_samples": gaps,
          "minimum_source_vertical_clearance_m": min(x["separation_m"] for x in gaps),
          "blender": "NOT RUN", "unity": "NOT RUN", "c01_02_independent": "PENDING"}
QA.write_text(json.dumps(report, indent=2) + "\n")
print("PASS W21 SOURCE", json.dumps({"triangles":464,"min_vertical_gap_m":report["minimum_source_vertical_clearance_m"],
          "source_sha":report["new_source_SHA256"]}), flush=True)
