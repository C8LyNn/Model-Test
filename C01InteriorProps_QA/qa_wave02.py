#!/usr/bin/env python3
"""C01-02: fail-closed source-inventory gate for 36 interior props.

Input JSON: owner -> [{path, size, blob_sha}] from pinned producer Git trees.
File presence or Git LFS pointers NEVER count as Blender/Unity QA PASS.
"""
import argparse
import csv
import json
from pathlib import Path

FAMILIES = {"P15": ("C01-15", 7), "P16": ("C01-16", 7),
            "P17": ("C01-17", 7), "P18": ("C01-18", 7),
            "P19": ("C01-19", 8)}

def expected_ids():
    return [(f"{family}-{n:02d}", owner, "W01" if n <= (4 if family == "P19" else 3) else "W02")
            for family, (owner, limit) in FAMILIES.items() for n in range(1, limit + 1)]

def inventory(snapshot):
    branches = snapshot.get("branches", {})
    rows = []
    for asset_id, owner, wave in expected_ids():
        files = [x for x in branches.get(owner, []) if isinstance(x, dict)
                 and asset_id.lower() in x.get("path", "").lower()]
        ext = {"blend": [], "fbx": [], "prefab": [], "preview": []}
        for x in files:
            path = x["path"].lower()
            for typ, ending in (("blend", ".blend"), ("fbx", ".fbx"), ("prefab", ".prefab")):
                if path.endswith(ending):
                    ext[typ].append(x)
            if path.endswith((".png", ".jpg", ".jpeg", ".webp")):
                ext["preview"].append(x)
        summary = {}
        for typ, found in ext.items():
            if not found:
                summary[typ] = "MISSING"
            elif typ in ("blend", "fbx", "preview") and all(x.get("size", 0) <= 160 for x in found):
                summary[typ] = "LFS_POINTER_ONLY"
            else:
                summary[typ] = "PRESENT_UNVALIDATED"
        rows.append({"asset_id": asset_id, "owner": owner, "wave": wave, "status": "BLOCKED",
                     "blend": summary["blend"], "fbx": summary["fbx"],
                     "prefab": summary["prefab"], "preview": summary["preview"],
                     "geometry": "NOT RUN", "uv_normals": "NOT RUN",
                     "unity_import": "NOT RUN", "playmode_clearance": "NOT RUN"})
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    snapshot = json.loads(a.snapshot.read_text(encoding="utf8"))
    rows = inventory(snapshot)
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "inventory.json").write_text(json.dumps(rows, indent=2), encoding="utf8")
    with (a.output / "inventory.csv").open("w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"C01-02: {len(rows)} IDs; 0 approved; 36 BLOCKED pending engine QA and native artifacts")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
