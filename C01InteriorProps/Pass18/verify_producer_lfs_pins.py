#!/usr/bin/env python3
"""PASS18: read-only 36-ID producer Git commit / LFS pointer provenance gate.

Checks that 24 current producer .blend and FBX POINTERS at exact commit SHA
match the signed integrator manifest. Does not download Git LFS objects,
open Blender or run Unity. This is NOT independent full-byte QA.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "C01InteriorProps/Pass04/source_stage_36.json"
RECEIPT = ROOT / "C01InteriorProps_QA/PASS18/PRODUCER_LFS_POINTER_AUDIT.json"
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
POINTER = re.compile(
    rb"version https://git-lfs.github.com/spec/v1\n"
    rb"oid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?\Z"
)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.PIPE)


def verify() -> dict:
    source = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = source["assets"]
    if len(entries) != 36 or len({x["id"] for x in entries}) != 36:
        raise ValueError("Expected 36 unique source asset IDs")
    if any(x["independent_qa"] != "NOT_APPROVED" for x in entries):
        raise ValueError("Integrator cannot self-approve independent QA")

    signed = [x for x in entries if SHA64.fullmatch(x.get("native_blend_sha256") or "")
              and SHA64.fullmatch(x.get("final_fbx_sha256") or "")]
    if len(signed) != 24:
        raise ValueError(f"Expected 24 immutable native source pairs, found {len(signed)}")
    branches: dict[str, str] = {}
    for e in signed:
        branch, commit = e["source_branch"], e["source_commit"]
        if not SHA40.fullmatch(commit):
            raise ValueError(f"Invalid producer Git commit {e['id']}")
        if branch in branches and branches[branch] != commit:
            raise ValueError(f"Mixed HEAD pins on producer branch {branch}")
        branches[branch] = commit

    fetched = {}
    for branch, commit in sorted(branches.items()):
        # No checkout, no LFS smudge/hydration and NO source-branch write.
        git("fetch", "--no-tags", "--depth=1", "origin", branch)
        real = git("rev-parse", "FETCH_HEAD").decode("ascii").strip()
        if real != commit:
            raise ValueError(f"Producer HEAD moved: {branch} pinned {commit} actual {real}")
        fetched[branch] = real

    checked = []
    for e in signed:
        for ext, path_key, sha_key in [
            (".blend", "native_blend_path", "native_blend_sha256"),
            (".fbx", "fbx_path", "final_fbx_sha256"),
        ]:
            path = e.get(path_key, "")
            parts = pathlib.PurePosixPath(path)
            if (not path or parts.is_absolute() or ".." in parts.parts
                    or parts.stem != e["id"] or parts.suffix.lower() != ext):
                raise ValueError(f"Unsafe or wrong {ext} locator for {e['id']}: {path}")
            # 'git show' returns the actual Git-stored LFS pointer, not the binary.
            raw = git("show", f"{e['source_commit']}:{path}")
            match = POINTER.fullmatch(raw)
            if match is None:
                raise ValueError(f"Not a canonical LFS pointer: {e['id']} {path}")
            digest, size = match.group(1).decode("ascii"), int(match.group(2))
            if digest != e[sha_key] or size < (1000 if ext == ".blend" else 200):
                raise ValueError(f"Native source pointer mismatch: {e['id']} {path}")
            checked.append(dict(id=e["id"], kind=ext, path=path,
                                lfs_oid_sha256=digest, lfs_size_bytes=size,
                                producer_git_commit=e["source_commit"]))

    if len(checked) != 48:
        raise ValueError("Expected exactly 48 real LFS pointers")
    return dict(schema="C01-10-PASS18-LFS-METADATA-ONLY",result="PASS",
                pairs=24,pointers=len(checked),branch_count=len(fetched),
                source_ids=len(entries),independent_c01_02="NOT_RUN",
                unity6_urp="NOT_RUN",full_binary_hydration="NOT_RUN",
                no_final_release=True,checked=checked)


def main() -> int:
    try:
        report = verify()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print("C01 PASS18 SIGNED LFS POINTER AUDIT FAILED: " + str(exc), file=sys.stderr)
        return 2
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"C01 PASS18 PRODUCER GIT/LFS POINTER AUDIT PASS "
          f"{report['pairs']}/24 asset pairs, {report['pointers']}/48 pointers. "
          "Hydrated binaries/Unity/C01-02 final QA NOT RUN.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
