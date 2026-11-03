#!/usr/bin/env python3
"""C01-03 PASS03: immutable source-byte receipts; no geometry/Unity PASS inferred."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEDGER = BASE / "repair_ledger.json"
P0 = {"P17-04", "P17-05", "P18-04", "P18-05", "P19-07", "P19-08"}
SHA1 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def records():
    return json.loads(LEDGER.read_text(encoding="utf-8"))["assets"]


def validate():
    assets = records()
    if len(assets) != 36 or len({x["asset_id"] for x in assets}) != 36:
        raise ValueError("Expected 36 globally unique assets")
    expected = {f"C01-P{g}-{n:02d}" for g in range(15, 20)
                for n in (range(1, 9) if g == 19 else range(1, 8))}
    if {a["asset_id"] for a in assets} != expected:
        raise ValueError("Canonical IDs mismatch")
    for a in assets:
        code = a["code"]
        if a["asset_id"] != "C01-" + code or (a["priority"] == "P0") != (code in P0):
            raise ValueError(f"{code}: wrong ID or priority")
        if not SHA1.fullmatch(a["baseline"]["commit"]):
            raise ValueError(f"{code}: unpinned producer revision")
        if a["release_status"] == "APPROVED":
            r, qa = a["repair"], a["qa"]
            if not r["release_version"] or not SHA1.fullmatch(r["commit"] or ""):
                raise ValueError(f"{code}: no immutable repair version")
            if not SHA256.fullmatch(r["fbx_sha256"] or "") or not SHA256.fullmatch(r["blend_sha256"] or ""):
                raise ValueError(f"{code}: missing after-export hashes")
            if qa["status"] != "PASS" or qa["signed_fbx_sha256"] != r["fbx_sha256"] or not qa["report_path"]:
                raise ValueError(f"{code}: independent QA missing or mismatched SHA")
            if any(r[k] != "PASS" for k in ("blender_open", "fbx_export", "fbx_roundtrip", "unity_import")):
                raise ValueError(f"{code}: actual engine/export tests incomplete")
    return assets


def inspect(checkout, relative, role):
    result = {"path": relative, "sha256": None, "size_bytes": None, "status": "PATH_UNRESOLVED"}
    if relative is None:
        return result
    if "\\" in relative or any(p in ("", ".", "..") for p in relative.split("/")):
        raise ValueError("Unsafe file path")
    folder = checkout.resolve()
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder):
        raise ValueError("Path escapes checkout")
    result["status"] = "MISSING"
    if not path.is_file():
        return result
    h = hashlib.sha256()
    with path.open("rb") as stream:
        header = stream.read(256)
        stream.seek(0)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    result["size_bytes"] = path.stat().st_size
    if not result["size_bytes"]:
        result["status"] = "INVALID_EMPTY"
    elif header.startswith(b"version https://git-lfs.github.com/spec/v1"):
        result["status"] = "UNRESOLVED_LFS_POINTER"
    elif role == "blend" and not header.startswith(b"BLENDER"):
        result["status"] = "INVALID_BLEND_HEADER"
    elif role == "fbx" and not (header.startswith(b"Kaydara FBX Binary") or header.lstrip().startswith(b"; FBX")):
        result["status"] = "INVALID_FBX_HEADER"
    else:
        result["status"] = "BYTE_SHA256_PASS_NOT_MESH_QA"
        result["sha256"] = h.hexdigest()
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["validate", "capture"])
    p.add_argument("--asset")
    p.add_argument("--checkout", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        assets = validate()
        if args.command == "validate":
            print("PASS: 36 baseline identities, 6 P0; NO mesh QA claimed")
            return 0
        a = next(x for x in assets if x["code"] == args.asset)
        if not args.checkout or not args.output:
            raise ValueError("Must provide --checkout and --output")
        head = subprocess.check_output(["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True).strip()
        if head != a["baseline"]["commit"]:
            raise ValueError("Immutable producer commit mismatch")
        b = a["baseline"]
        receipt = {"asset_id": a["asset_id"], "before_commit": head,
                   "blender": inspect(args.checkout, b["blend_path_observed"], "blend"),
                   "fbx": inspect(args.checkout, b["fbx_path_observed"], "fbx"),
                   "scope": "BYTES_AND_HEADERS_ONLY_NOT_BLENDER_UNITY_OR_TOPOLOGY_QA"}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt))
        return 0 if all(receipt[x]["status"] == "BYTE_SHA256_PASS_NOT_MESH_QA" for x in ("blender", "fbx")) else 2
    except (ValueError, StopIteration) as exc:
        print("BLOCKED:", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
