#!/usr/bin/env python3
"""PASS17 quarantined file identity checks. Not actual Blender roundtrip/Unity."""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "QA_Candidates" / "PASS17_SourceRecovery"
REPORT = P / "QA" / "blender_static_report.json"
expected = {"W01": 12, "W02": 572, "W03": 20, "W04": 28}

if not REPORT.is_file():
    raise FileNotFoundError("PASS17 NEW Blender report missing: " + str(REPORT))
report = json.loads(REPORT.read_text(encoding="utf-8"))
assert len(report) == 4 and {r["id"] for r in report} == set(expected)
manifest = []
for row in report:
    mid = row["id"]
    assert row["status"] == "BLENDER_STATIC_PASS"
    if row["triangles"] != expected[mid]:
        raise ValueError(mid + ": stale geometry triangle count " +
                         str(row["triangles"]) + " != " + str(expected[mid]))
    blends = list((P / "Blender").glob(mid + "_*.blend"))
    fbx = list((P / "FBX").glob(mid + "_*.fbx"))
    assert len(blends) == len(fbx) == 1, mid
    assert blends[0].read_bytes()[:7] == b"BLENDER", mid
    assert fbx[0].read_bytes()[:20] == b"Kaydara FBX Binary  ", mid
    for view in ("iso", "front", "side"):
        path = P / "Previews" / (mid + "_" + view + ".png")
        assert path.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a"), path
    for path in (blends[0], fbx[0]):
        manifest.append({"id": mid, "path": str(path.relative_to(ROOT)),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

(P / "QA" / "PASS17_SHA256_HEADERS_ONLY.json").write_text(
    json.dumps({"status": "HEADER_ONLY_PASS_NOT_NATIVE_ROUNDTRIP",
                "artifacts": manifest, "blender_reimport": "NOT RUN",
                "unity": "NOT RUN", "independent_qa": "PENDING"}, indent=2) + "\n")
print("C01-11 PASS17 quarantined 4 BLEND + 4 FBX + 12 PNG header checks PASS")
print("Blender reimport, independent C01-02 QA and Unity6 still NOT RUN.")
