#!/usr/bin/env python3
"""Verify actual native file signatures. Does NOT test Unity import."""
import json
from pathlib import Path
P = Path(__file__).resolve().parents[1]
report = json.loads((P/"QA"/"blender_static_report.json").read_text())
assert len(report) == 4 and {r["id"] for r in report} == {"W01","W02","W03","W04"}
for item in report:
    assert item["status"] == "BLENDER_STATIC_PASS"
    mid = item["id"]
    blends=list((P/"Blender").glob(mid+"_*.blend"))
    fbx=list((P/"FBX").glob(mid+"_*.fbx"))
    assert len(blends)==len(fbx)==1,mid
    assert blends[0].read_bytes()[:7] == b"BLENDER",mid
    assert fbx[0].read_bytes()[:20] == b"Kaydara FBX Binary  ",mid
    assert fbx[0].stat().st_size > 100, mid
    for view in ("iso","front","side"):
        assert (P/"Previews"/(mid+"_"+view+".png")).read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")
print("C01-11: 4 BLEND + 4 FBX + 12 PNG header checks PASS")
