#!/usr/bin/env python3
"""C01-10 PASS09: hydrate eligible real producer FBX snapshots into a disposable Unity QA staging area.

No geometry rewrite, merge or source branch change. This script fetches detached
producer revisions and copies only real, binary FBX files. It does not approve QA.
Requires local git + git-lfs and access to the linked Model-Test GitHub repository.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

BINARY_FBX_MAGIC = b"Kaydara FBX Binary"
VALID_ID = re.compile(r"^P(?:15|16|17|18|19)-0[1-8]$")
OUT_REL = Path("Assets/C01InteriorProps/Pass04Incoming")
REPORT_REL = Path("C01InteriorProps_QA/PASS04/staged_sources.csv")


def git(repo: Path, *args: str, env=None) -> str:
    process = subprocess.run(["git", "-C", str(repo), *args],
                             check=True, capture_output=True, text=True, env=env)
    return process.stdout.strip()


def sha256(file: Path) -> str:
    digest = hashlib.sha256()
    with file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_entry(entry: dict) -> None:
    ident = entry["id"]
    commit = entry["source_commit"]
    source_path = PurePosixPath(entry["fbx_path"])
    if not VALID_ID.fullmatch(ident):
        raise ValueError(f"Unexpected asset ID: {ident}")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError(f"Unpinned producer Git commit for {ident}")
    if source_path.is_absolute() or ".." in source_path.parts or source_path.suffix.lower() != ".fbx":
        raise ValueError(f"Unsafe/non-FBX source path for {ident}")
    if source_path.stem.lower() != ident.lower():
        raise ValueError(f"Source is a moving subpart rather than canonical root FBX: {ident}")
    if entry["independent_qa"] == "APPROVED":
        raise ValueError("The staging manifest cannot assert independent QA approval")
    valid_states = {
        "CANDIDATE_BINARY_FBX_QA_NOT_APPROVED",
        "BLOCKED_P19_EXPORT_TOPOLOGY",
        "BLOCKED_NO_NATIVE_BINARY_FBX",
        "BLOCKED_SOURCE_NEWER_THAN_FBX",
        "BLOCKED_DETAIL_PASS12_NATIVE_EXPORT",
    }
    if entry.get("native_export_sync") not in valid_states:
        raise ValueError(f"Unreviewed export-sync state for {ident}")
    if not entry.get("native_export_blocker"):
        raise ValueError(f"Missing export-sync reason for {ident}")


def validate_real_fbx(file: Path) -> tuple[str, int]:
    size = file.stat().st_size
    with file.open("rb") as handle:
        header = handle.read(max(len(BINARY_FBX_MAGIC), 96))
    if header.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("Git LFS pointer; model binary was not hydrated")
    if not header.startswith(BINARY_FBX_MAGIC):
        raise ValueError("Not a genuine binary Kaydara FBX")
    if size < 200:
        raise ValueError("Binary FBX suspiciously small")
    return sha256(file), size


def stage(manifest: Path, project: Path, apply: bool, selected_ids: set[str]) -> list[dict]:
    root = json.loads(manifest.read_text(encoding="utf-8"))
    if root.get("schema") != "C01-10-PASS09-STAGING-2":
        raise ValueError("Unsupported staging manifest")
    entries = root.get("assets", [])
    if len(entries) != 36 or len({e["id"] for e in entries}) != 36:
        raise ValueError("Exactly 36 unique Wave 01+02 asset entries required")
    for entry in entries:
        validate_entry(entry)
    if not (project / ".git").exists() and not (project / ".git").is_file():
        raise ValueError("--repo must point to a checked-out Git repository")
    if not (project / "Assets").is_dir():
        raise ValueError("--repo must point to a Unity project root with Assets/")
    if selected_ids:
        unknown = selected_ids.difference(e["id"] for e in entries)
        if unknown:
            raise ValueError("Unknown selected IDs: " + ",".join(sorted(unknown)))
        entries = [e for e in entries if e["id"] in selected_ids]
    rows = []
    eligible = []
    for entry in entries:
        state = entry["native_export_sync"]
        if state != "CANDIDATE_BINARY_FBX_QA_NOT_APPROVED":
            rows.append(dict(
                id=entry["id"], state=state, source_commit=entry["source_commit"],
                fbx_sha256="", size_bytes="", detail=entry["native_export_blocker"]
            ))
        else:
            eligible.append(entry)
    by_commit: dict[tuple[str, str], list[dict]] = {}
    for entry in eligible:
        by_commit.setdefault((entry["source_branch"], entry["source_commit"]), []).append(entry)

    if not apply:
        for entry in eligible:
            rows.append(dict(id=entry["id"], state="NOT_RUN_DRY_RUN", source_commit=entry["source_commit"],
                             fbx_sha256="", size_bytes="", detail="Will fetch hydrated producer binary on --apply"))
        return rows

    # A blocked ID cannot be copied into Unity staging merely because its OLD
    # binary FBX and Git LFS pointer still exist in the producer revision.
    with tempfile.TemporaryDirectory(prefix="c01-pass09-fbx-") as folder:
        work_root = Path(folder)
        for group_index, ((source_branch, commit), group) in enumerate(sorted(by_commit.items())):
            worktree = work_root / f"producer_{group_index:02d}"
            try:
                # Fetch branch objects then check out immutable commit (not a movable branch).
                git(project, "fetch", "--no-tags", "origin", source_branch)
                git(project, "cat-file", "-e", f"{commit}^{{commit}}")
                env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
                git(project, "worktree", "add", "--detach", str(worktree), commit, env=env)
                source_names = [e["fbx_path"] for e in group]
                include = ",".join(source_names)
                git(worktree, "lfs", "pull", "--include", include, "--exclude", "")
                for entry in group:
                    ident = entry["id"]
                    origin = worktree.joinpath(*PurePosixPath(entry["fbx_path"]).parts)
                    dest = project / OUT_REL / ident / (ident + ".fbx")
                    record = dict(id=ident, state="BLOCKED", source_commit=commit,
                                  fbx_sha256="", size_bytes="", detail="")
                    try:
                        digest, size = validate_real_fbx(origin)
                        expected = entry.get("final_fbx_sha256")
                        if expected and expected != digest:
                            raise ValueError("FBX SHA differs from pinned final source SHA")
                        if dest.exists() and sha256(dest) != digest:
                            raise ValueError("Different staging FBX already exists; refuse overwrite")
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if not dest.exists():
                            shutil.copy2(origin, dest)
                        record.update(state="STAGED_SOURCE_NOT_QA_APPROVED",
                                      fbx_sha256=digest, size_bytes=str(size),
                                      detail=str(dest.relative_to(project)).replace("\\", "/"))
                    except Exception as ex:
                        record["detail"] = type(ex).__name__ + ": " + str(ex)
                    rows.append(record)
            except Exception as ex:
                for entry in group:
                    rows.append(dict(id=entry["id"], state="BLOCKED",
                                     source_commit=commit, fbx_sha256="", size_bytes="",
                                     detail=type(ex).__name__ + ": " + str(ex)))
            finally:
                # Detached producer worktree is discarded; no branch merge occurs.
                if worktree.exists():
                    try:
                        git(project, "worktree", "remove", "--force", str(worktree))
                    except subprocess.CalledProcessError:
                        print(f"WARNING: temporary worktree removal failed: {worktree}", file=sys.stderr)

    report = project / REPORT_REL
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=["id", "state", "source_commit", "fbx_sha256",
                                                  "size_bytes", "detail"])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda v: v["id"]))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Model-Test Unity project checkout")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("source_stage_36.json"))
    parser.add_argument("--apply", action="store_true", help="actually fetch, hydrate and stage FBX")
    parser.add_argument("--ids", nargs="*", default=[], help="optional IDs to stage first, e.g. P19-05 P19-07")
    args = parser.parse_args()
    try:
        rows = stage(args.manifest.resolve(), args.repo.resolve(), args.apply, set(args.ids))
    except Exception as ex:
        print("C01 PASS04 staging FAIL:", ex, file=sys.stderr)
        return 2
    for row in sorted(rows,key=lambda x:x["id"]):
        print(f"{row['id']:7s}  {row['state']:28s} {row['detail']}")
    success=sum(x["state"]=="STAGED_SOURCE_NOT_QA_APPROVED" for x in rows)
    print(f"Staged original binary sources: {success}/{len(rows)}. Independent QA: NOT APPROVED.")
    return 0 if (not args.apply or success==len(rows)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
