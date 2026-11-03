#!/usr/bin/env python3
"""C01-03 Wave 02 manifest and dependency validation; never fabricates model evidence."""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # C01InteriorProps_Library parent = repository root
CATALOG = HERE / "catalog.json"
WAVE01 = HERE.parent / "catalog.json"
LIFECYCLE = {"PLANNED", "IN PRODUCTION", "READY FOR QA", "APPROVED", "REJECTED", "DEPRECATED"}
SHA = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
REQ_ROLES = {"blend", "fbx", "prefab", "prefab_meta", "preview_front", "preview_side", "preview_iso"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_file(record, errors, aid):
    path = record.get("path")
    if not isinstance(path, str) or "\\" in path:
        errors.append(f"{aid}: invalid path")
        return
    logical = path.split("/")
    if any(part in ("", ".", "..") for part in logical) or Path(path).is_absolute():
        errors.append(f"{aid}: path traversal")
        return
    file = (ROOT / path).resolve()
    if not file.is_relative_to(ROOT.resolve()):
        errors.append(f"{aid}: path escapes repo")
        return
    if not file.is_file():
        errors.append(f"{aid}: missing physical file {path}")
        return
    blob = file.read_bytes()
    if not blob or blob.startswith(b"version https://git-lfs.github.com/spec/v1"):
        errors.append(f"{aid}: empty or Git LFS pointer: {path}")
        return
    digest = hashlib.sha256(blob).hexdigest()
    if record.get("sha256") != digest or record.get("size_bytes") != len(blob):
        errors.append(f"{aid}: file SHA-256/size mismatch: {path}")


def audit(wave01, wave02):
    errors = []
    assets = wave02.get("assets")
    if wave02.get("wave") != 2 or wave02.get("schema_version") != "1.0.0" or not isinstance(assets, list) or len(assets) != 20:
        return ["Wave02 must contain exactly 20 assets with version 1.0.0"]
    prior = wave01.get("assets", [])
    previous_ids = {item["asset_id"] for item in prior}
    if len(previous_ids) != 16:
        errors.append("Wave01 must have 16 canonical IDs")
    expected = ({f"C01-P{family}-{num:02d}" for family in range(15, 19) for num in range(4, 8)}
                | {f"C01-P19-{num:02d}" for num in range(5, 9)})
    codes = [item.get("asset_id") for item in assets]
    if len(set(codes)) != len(codes) or set(codes) != expected:
        errors.append("Wave02 canonical ID set invalid or duplicated")
    if previous_ids.intersection(codes):
        errors.append("Wave01/Wave02 ID collision")
    all_ids = previous_ids | set(codes)
    graph = {}
    for a in assets:
        aid = a.get("asset_id")
        if not isinstance(aid, str) or aid not in expected:
            errors.append(f"invalid ID: {aid}")
            continue
        if a.get("owner_thread") != "C01-" + aid.split("-")[1][1:]:
            errors.append(f"{aid}: owner mismatch")
        if a.get("status") not in LIFECYCLE:
            errors.append(f"{aid}: bad status")
        ver = a.get("proposed_version")
        if not isinstance(ver, str) or not VERSION.fullmatch(ver):
            errors.append(f"{aid}: invalid version")
        deps = a.get("dependencies")
        if not isinstance(deps, list) or len(set(deps)) != len(deps) or any(d not in all_ids or d == aid for d in deps):
            errors.append(f"{aid}: invalid dependencies")
            graph[aid] = []
        else:
            graph[aid] = [d for d in deps if d in expected]
        files = a.get("files", [])
        if not isinstance(files, list):
            errors.append(f"{aid}: files not a list")
            continue
        roles = []
        for f in files:
            role = f.get("role")
            if role not in REQ_ROLES or role in roles:
                errors.append(f"{aid}: invalid or duplicate file role {role}")
            roles.append(role)
            verify_file(f, errors, aid)
        if a.get("delivered_version") is not None and a["delivered_version"] != ver:
            errors.append(f"{aid}: delivered version mismatch")
        if files and a.get("delivered_version") is None:
            errors.append(f"{aid}: file records without delivered version")
        if a.get("status") in ("READY FOR QA", "APPROVED") and not REQ_ROLES.issubset(roles):
            errors.append(f"{aid}: premature READY FOR QA/APPROVED; missing assets")
        if a.get("status") == "APPROVED":
            fbx = next((f for f in files if f.get("role") == "fbx"), {})
            qa = a.get("qa", {})
            if qa.get("status") != "PASS" or qa.get("verified_fbx_sha256") != fbx.get("sha256") or not qa.get("evidence"):
                errors.append(f"{aid}: missing independent hash-bound QA")
            runtime = a.get("runtime", {})
            if any(runtime.get(x) != "PASS" for x in ("blender", "unity_import", "unity_prefab", "clearance")):
                errors.append(f"{aid}: no complete Blender/Unity verification")
    def visit(node, state):
        if state.get(node) == "active":
            errors.append(f"cyclic dependency at {node}")
            return
        if state.get(node) == "done":
            return
        state[node] = "active"
        for adj in graph.get(node, []):
            visit(adj, state)
        state[node] = "done"
    state = {}
    for node in graph:
        visit(node, state)
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["audit", "release"])
    args = p.parse_args()
    old, new = read_json(WAVE01), read_json(CATALOG)
    errors = audit(old, new)
    for err in errors:
        print("FAIL:", err)
    if errors:
        return 1
    print("Wave02 metadata check PASS: 20 unique planned assets, no dependency cycles")
    if args.command == "release":
        missing = [a["asset_id"] for a in new["assets"] if a["status"] != "APPROVED"]
        if missing:
            print("BLOCKED: not independently approved:", ", ".join(missing))
            return 2
        print("Technical registry gate PASS; formal C01-00 acceptance remains separate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
