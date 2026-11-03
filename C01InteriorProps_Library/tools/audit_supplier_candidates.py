#!/usr/bin/env python3
"""C01-03: scan real checked-out producer bytes without approving assets.
Input is the PR-pinned catalog. Missing source files are reported, not invented.
"""
import argparse
import hashlib
import json
from pathlib import Path

EXTENSIONS = {
    "blend": ".blend", "fbx": ".fbx", "prefab": ".prefab",
    "prefab_meta": ".meta", "preview": (".png", ".svg"),
    "obj": ".obj", "gltf": ".gltf"
}


def inspect(checkout, candidate):
    role = candidate["role"]
    logical = candidate["path"]
    if role not in EXTENSIONS or not isinstance(logical, str):
        raise ValueError("invalid candidate role or path")
    parts = logical.split("/")
    if not parts or any(not p or p in (".", "..") for p in parts) or "\\" in logical:
        raise ValueError(f"unsafe candidate path: {logical!r}")
    root = checkout.resolve()
    target = (root / logical).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"path escapes checkout: {logical}")
    allowed = EXTENSIONS[role]
    if isinstance(allowed, str):
        allowed = (allowed,)
    if target.suffix.lower() not in allowed:
        raise ValueError(f"extension mismatch {role}: {logical}")
    result = {"role": role, "path": logical, "sha256": None, "bytes": 0, "result": "MISSING"}
    if not target.is_file():
        return result
    data = target.read_bytes()
    if not data:
        result["result"] = "INVALID_EMPTY"
        return result
    if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
        result["result"] = "UNRESOLVED_LFS_POINTER"
        return result
    if role == "blend" and not data.startswith(b"BLENDER"):
        result["result"] = "INVALID_HEADER"
        return result
    if role == "fbx" and not (data.startswith(b"Kaydara FBX Binary") or data.lstrip().startswith(b"; FBX")):
        result["result"] = "INVALID_HEADER"
        return result
    if role == "preview":
        if target.suffix.lower() == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            result["result"] = "INVALID_HEADER"
            return result
        if target.suffix.lower() == ".svg" and b"<svg" not in data[:4096]:
            result["result"] = "INVALID_HEADER"
            return result
    if role == "prefab" and not data.lstrip().startswith(b"%YAML"):
        result["result"] = "INVALID_HEADER"
        return result
    if role == "gltf":
        try:
            json.loads(data)
        except (ValueError, UnicodeError):
            result["result"] = "INVALID_JSON"
            return result
    if role == "obj" and not (b"\nv " in b"\n" + data[:8192] or data.startswith(b"v ")):
        result["result"] = "INVALID_OBJ_STREAM"
        return result
    result.update({"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "result": "BYTES_HASHED_UNTESTED_IMPORT"})
    return result


def scan(catalog, producer, checkout):
    records = []
    for asset in catalog["assets"]:
        if asset["owner_thread"] != producer:
            continue
        items = [inspect(checkout, p) for p in asset["supplier_evidence"]["paths"]]
        by_role = {r: sum(f["result"] == "BYTES_HASHED_UNTESTED_IMPORT" and f["role"] == r for f in items)
                   for r in ("blend", "fbx", "prefab", "prefab_meta", "preview")}
        records.append({
            "asset_id": asset["asset_id"],
            "producer_head_sha": asset["supplier_evidence"]["head_sha"],
            "observed": items,
            "role_counts": by_role,
            "candidate_complete": all(by_role[r] >= n for r, n in
                                      {"blend": 1, "fbx": 1, "prefab": 1, "prefab_meta": 1, "preview": 3}.items()),
            "approval": "NOT_APPROVED"
        })
    if not records:
        raise ValueError(f"producer not found: {producer}")
    return {
        "catalog_schema": catalog["schema_version"],
        "producer": producer,
        "scope": "BYTE_SIGNATURE_SHA256_ONLY_NOT_BLENDER_OR_UNITY_QA",
        "assets": records,
        "asset_count": len(records)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--producer", choices=[f"C01-{i}" for i in range(15, 20)], required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cat = json.loads(args.catalog.read_text(encoding="utf-8"))
    r = scan(cat, args.producer, args.checkout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    for asset in r["assets"]:
        print(asset["asset_id"], json.dumps(asset["role_counts"], sort_keys=True),
              "COMPLETE_CANDIDATE" if asset["candidate_complete"] else "INCOMPLETE")
        for record in asset["observed"]:
            print(" ", record["result"], record["role"], record["path"],
                  "sha256=" + str(record["sha256"]))
    print("BYTE_AUDIT_FINISHED; no QA or Unity PASS inferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
