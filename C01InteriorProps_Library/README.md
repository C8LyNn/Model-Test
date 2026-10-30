# C01-03 — Interior Props Asset Library / PASS 01 / WAVE 01

**Source:** [C01 Interior Props #2](https://github.com/C8LyNn/Model-Test/issues/2) · **Responsible thread:** C01-03 · **Ship branch:** `codex/c01-ship-integration`.

This repository folder is a **registry, not an asset fabrication package**. Producer geometry is owned by C01-15–19. This branch does not alter ship levels, rooms, architecture, collisions, original prefabs or source meshes.

## Asset population

16 canonical Wave01 IDs with producer PR candidates marked **IN PRODUCTION**. SHA-256 was verified for 115 candidate files from pinned producer commits in GitHub Actions, but no version is **APPROVED** or imported to the integration branch:
- P15-01–03 technical installations — [#3](https://github.com/C8LyNn/Model-Test/issues/3)
- P16-01–03 lighting/signals — [#4](https://github.com/C8LyNn/Model-Test/issues/4)
- P17-01–03 controls/puzzles — [#5](https://github.com/C8LyNn/Model-Test/issues/5)
- P18-01–03 cargo — [#6](https://github.com/C8LyNn/Model-Test/issues/6)
- P19-01–04 furniture — [#7](https://github.com/C8LyNn/Model-Test/issues/7)

Suggested dimensions are recorded in **meters, W×D×H** exactly as described in the issues. These are not measured dimensions. No missing FBX, .blend or prefab file is represented by a fake path or a fake hash.

**Evidence:** [115-file SHA256 audit](WAVE01_HASH_AUDIT_2026-10-30.md), [GitHub Actions run](https://github.com/C8LyNn/Model-Test/actions/runs/41071526841). Hashes are held under `supplier_evidence.paths`, separate from the release-only local `files` list. Zero model packages are currently complete.

## Workflow and versioning

1. Owner creates real source `.blend`, binary `.fbx`, Unity 6 URP `.prefab` (with `.meta`) and PNG screenshots: front, side and rear/third angle. Commit under an **isolated producer path and branch**. Owners must also provide measured dimensions, pivot, orientation, mounting socket, triangle count, material slots, colliders and clearance evidence.
2. C01-03 checks out a branch with those real files. Run:
   ```bash
   python C01InteriorProps_Library/tools/registry.py audit
   python C01InteriorProps_Library/tools/registry.py register --asset C01-P15-01 --role fbx --path Assets/C01InteriorProps/Models/P15-01/v0.1.0/P15-01.fbx
   python C01InteriorProps_Library/tools/registry.py release
   python -m unittest discover -s C01InteriorProps_Library/tests -v
   ```
   **Example registration path is illustrative only**; it is not a claim of a real file. Use actual producer paths.
3. `register` refuses nonexistent files, empty files, wrong extensions, LFS pointer text, invalid file headers, duplicate roles/paths, or modifications of an APPROVED or DEPRECATED version. On success it records size and SHA-256 and sets `delivered_version`. Existing file records cannot be silently replaced.
4. C01-02 runs independent QA [#8](https://github.com/C8LyNn/Model-Test/issues/8), confirms Blender and Unity imports in the real applications, and provides an independently reviewed QA report bound to the specific FBX SHA-256. C01-10 integrates a *separate* showcase scene [#9](https://github.com/C8LyNn/Model-Test/issues/9). No unauthorized ship geometry/layout edits.
5. For APPROVED, record `qa.status=PASS`, `qa.report_path`, `qa.fbx_sha256` matching the actual export, `execution.blender=PASS` and `execution.unity=PASS` with independent evidence. Populate all measured geometry, mounting and collider fields.
6. `release` is fail-closed: all 16 assets must be complete and APPROVED with evidence. A successful static catalog check **does not certify actual Blender or Unity behavior**. C01-00 signs off the release separately.

**Immutability:** `asset_id` is stable. `planned_version` is not a released version. When changing an approved file, create a new semantic version and its own versioned path rather than replacing an existing export. This initial registry does not implement automated version promotion; C01-03 controls that workflow during review.

## Files

- `catalog.json`: 16 asset records with actual producer branch/commit provenance and 115 byte-hashed candidate file references; no manufactured approval.
- `WAVE01_HASH_AUDIT_2026-10-30.md`: producer file inventory and independent QA blockers.
- `tools/audit_supplier_candidates.py`: Git LFS checkout byte verification and hash receipts.
- `.github/workflows/c01-03-producer-intake.yml`: 5 pinned supplier branches, SHA256 intake artifacts.
- `tools/registry.py`: audit, registration, release gates, SHA-256.
- `tests/test_registry.py`: regression tests for metadata, missing files, approval and overwrite safety.
- `HANDOFF_C01-02_C01-10.md`: explicit QA and integration handoff.
- `.github/workflows/c01-interior-props-registry.yml`: optional GitHub Actions validation.

Status now: **REGISTRY & PRODUCER BYTE INTEGRITY PASS / SOURCE SETS PARTIAL / INDEPENDENT QA 0/16 APPROVED / UNITY INTEGRATION NOT RUN BY C01-03**. Wave02 has a separate stacked PR for its 20 planned model IDs.
