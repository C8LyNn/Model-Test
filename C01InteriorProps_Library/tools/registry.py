#!/usr/bin/env python3
"""C01-03 registry: no fabricated file records; SHA-256 check against actual bytes."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "C01InteriorProps_Library" / "catalog.json"
ROLES = {
    "blend": ".blend",
    "fbx": ".fbx",
    "prefab": ".prefab",
    "prefab_meta": ".meta",
    "preview_front": ".png",
    "preview_side": ".png",
    "preview_rear": ".png",
}
STATUSES = {"PLANNED", "IN PRODUCTION", "READY FOR QA", "APPROVED", "REJECTED", "DEPRECATED"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^C01-P(15|16|17|18|19)-0[1-4]$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("path must be a forward-slash repository-relative string")
    sub = Path(relative)
    if sub.is_absolute() or any(x in ("..", ".") for x in relative.split("/")):
        raise ValueError(f"unsafe path: {relative}")
    target = ROOT / sub
    if not target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f"path escapes repository: {relative}")
    return target


def load():
    with CATALOG.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_one_file(entry, errors):
    role, relative = entry.get("role"), entry.get("path")
    if role not in ROLES:
        errors.append(f"unknown file role: {role!r}")
        return
    try:
        path = safe_path(relative)
    except ValueError as exc:
        errors.append(str(exc))
        return
    if path.suffix.lower() != ROLES[role]:
        errors.append(f"{relative}: wrong extension for {role}")
    if not path.is_file():
        errors.append(f"{relative}: referenced file does not exist")
        return
    data = path.read_bytes()
    if not data:
        errors.append(f"{relative}: empty file")
        return
    if data.startswith(b"version https://git-lfs.github.com/spec/"):
        errors.append(f"{relative}: unresolved Git LFS pointer")
        return
    if role == "blend" and not data.startswith(b"BLENDER"):
        errors.append(f"{relative}: not a native Blender file header")
    if role == "fbx" and not (data.startswith(b"Kaydara FBX Binary") or data.lstrip().startswith(b"; FBX")):
        errors.append(f"{relative}: unrecognized FBX header")
    if role.startswith("preview_") and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append(f"{relative}: not a PNG file")
    if role == "prefab" and not data.lstrip().startswith(b"%YAML"):
        errors.append(f"{relative}: not a text Unity prefab")
    h = sha256(path)
    if entry.get("size_bytes") != len(data) or entry.get("sha256") != h:
        errors.append(f"{relative}: size or SHA-256 mismatch")


def audit(data):
    errors, pending = [], []
    assets = data.get("assets")
    if data.get("schema_version") != "1.0.0" or not isinstance(assets, list) or len(assets) != 16:
        errors.append("expected schema 1.0.0 with precisely 16 assets")
        return errors, pending
    seen = set()
    expected = {f"C01-P{n}-{i:02d}" for n, count in [(15, 3), (16, 3), (17, 3), (18, 3), (19, 4)] for i in range(1, count+1)}
    for a in assets:
        aid = a.get("asset_id")
        if aid in seen or aid not in expected or not isinstance(aid, str) or not ID.fullmatch(aid):
            errors.append(f"duplicate or unrecognized asset id: {aid}")
        seen.add(aid)
        group = aid.split("-")[1] if isinstance(aid, str) and "-" in aid else ""
        if a.get("owner_thread") != f"C01-{group[1:]}":
            errors.append(f"{aid}: owner mismatch")
        if a.get("status") not in STATUSES:
            errors.append(f"{aid}: invalid lifecycle status")
        dim = a.get("suggested_dimensions_wdh_m")
        if not isinstance(dim, list) or len(dim) != 3 or any(type(n) not in (int, float) or n <= 0 for n in dim):
            errors.append(f"{aid}: invalid proposed dimensions")
        records = a.get("files")
        if not isinstance(records, list):
            errors.append(f"{aid}: files must be a list")
            continue
        roles = set()
        for entry in records:
            role = entry.get("role")
            if role in roles:
                errors.append(f"{aid}: duplicate role {role}")
            roles.add(role)
            if not isinstance(entry.get("sha256"), str) or not HEX64.fullmatch(entry.get("sha256")):
                errors.append(f"{aid}: invalid SHA-256 in {role}")
            check_one_file(entry, errors)
        missing = sorted(set(ROLES) - roles)
        if missing:
            pending.append(f"{aid}: MISSING {', '.join(missing)}")
        if records and a.get("delivered_version") != a.get("planned_version"):
            errors.append(f"{aid}: delivered version must match planned version for these files")
        if a.get("status") in {"READY FOR QA", "APPROVED"} and missing:
            errors.append(f"{aid}: premature READY FOR QA / APPROVED")
        if a.get("status") == "APPROVED":
            qa = a.get("qa", {})
            fbx = next((entry for entry in records if entry.get("role") == "fbx"), {})
            if qa.get("status") != "PASS" or qa.get("fbx_sha256") != fbx.get("sha256") or not qa.get("report_path"):
                errors.append(f"{aid}: no matching independent QA evidence")
            else:
                try:
                    if not safe_path(qa["report_path"]).is_file():
                        errors.append(f"{aid}: QA report is missing")
                except ValueError as exc:
                    errors.append(f"{aid}: {exc}")
            execution = a.get("execution", {})
            if execution.get("blender") != "PASS" or execution.get("unity") != "PASS":
                errors.append(f"{aid}: Blender/Unity evidence not PASS")
            actual = a.get("measured", {})
            if not isinstance(actual, dict) or any(actual.get(k) is None for k in ("dimensions_wdh_m", "triangles", "pivot_xyz_m", "orientation", "material_slots", "colliders", "mounting_socket")):
                errors.append(f"{aid}: missing measured metadata")
    if seen != expected:
        errors.append(f"asset ID set differs from canonical issues #3–7: {sorted(expected - seen)}")
    return errors, pending


def register(args):
    data = load()
    asset = next((a for a in data["assets"] if a["asset_id"] == args.asset), None)
    if asset is None:
        raise ValueError("asset ID not found")
    if asset["status"] in ("APPROVED", "DEPRECATED"):
        raise ValueError("approved/deprecated version is immutable; create a new version")
    if args.role not in ROLES:
        raise ValueError("unsupported role")
    target = safe_path(args.path)
    if not target.is_file():
        raise ValueError("file does not exist; no placeholder entries allowed")
    if target.suffix.lower() != ROLES[args.role]:
        raise ValueError("wrong file extension")
    if any(f["role"] == args.role for f in asset["files"]):
        raise ValueError("role already registered; no overwrite")
    if any(f["path"] == args.path for a in data["assets"] for f in a["files"]):
        raise ValueError("file path already owned by an asset")
    entry = {"role": args.role, "path": args.path, "size_bytes": target.stat().st_size, "sha256": sha256(target)}
    file_errors = []
    check_one_file(entry, file_errors)
    if file_errors:
        raise ValueError("; ".join(file_errors))
    asset["files"].append(entry)
    asset["delivered_version"] = asset["planned_version"]
    if asset["status"] == "PLANNED":
        asset["status"] = "IN PRODUCTION"
    temporary = CATALOG.with_suffix(".json.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temporary, CATALOG)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps(entry, indent=2))


def main():
    p = argparse.ArgumentParser(description="C01-03 production registry")
    p.add_argument("command", choices=["audit", "release", "register"])
    p.add_argument("--asset")
    p.add_argument("--role", choices=list(ROLES))
    p.add_argument("--path")
    args = p.parse_args()
    if args.command == "register":
        if not all((args.asset, args.role, args.path)):
            p.error("register requires --asset, --role, --path")
        try:
            register(args)
        except ValueError as exc:
            p.error(str(exc))
        return 0
    errors, pending = audit(load())
    for line in errors:
        print("FAIL:", line)
    for line in pending:
        print("PENDING:", line)
    if errors:
        print(f"INVALID CATALOG: {len(errors)} errors")
        return 1
    if args.command == "release" and pending:
        print(f"BLOCKED: {len(pending)} assets missing required files")
        return 2
    if args.command == "release":
        data = load()
        if any(a["status"] != "APPROVED" for a in data["assets"]):
            print("BLOCKED: asset(s) not independently APPROVED")
            return 2
        print("CATALOG RELEASE CANDIDATE PASS: confirm GitHub review and C01-00 signoff separately")
    else:
        print(f"CATALOG METADATA PASS: {16} IDs; {len(pending)} pending deliveries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
