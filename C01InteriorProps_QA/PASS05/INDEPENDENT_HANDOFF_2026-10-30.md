# C01-02 — PASS 05 / Independent FBX technical QA
**2026-10-30 · C01-02 · parent #33, #30 · DRAFT PR #13**

## Independently EXECUTED in this pass
- Recomputed indexed-mesh checks from **22 original hydrated GitHub Actions binary FBX files** using local parser on actual bytes, not synthetic models or gallery reconstructions. **9/9 new PASS05 test suite PASS** (signature/version, sha, indexed geometry, absence of duplicate/degenerate native faces, zero bad edges, UV and normal layers, expected P19 preflight risk, all 36 gating statuses).
- **Git LFS identity validated against *current* owner branch**: P17 7/7, P18 7/7, P19 8/8 `oid sha256` EXACTLY equal to SHA-256 of the 22 independently inspected binaries. This resolves the earlier provenance mismatch between prior CI commit SHA and newer producer branch HEAD without claiming any new Blender run.
- P15 7/7 real Git LFS pointers and advertised object sizes read from current PR #16/#25. **Raw binary bytes not available in independent QA sandbox**, so indexed topology, independent source opening, FBX import are **NOT RUN/BLOCKED**.
- P16 7/7 repo FBX files read at current PR #12/#28: all seven are **ASCII text FBX 7.4**, not native Blender binary FBX. All have serialized `LayerElementUV` and `LayerElementNormal`, but this is *not* proof native Blender export/reimport. Required seven binary exports and .blend source **MISSING/BLOCKED** in independently inspected files.

## P0 CI FAILURE — independently reproduced and code defect isolated
- Workflow job data for C01-19 run `41094703040` and C01-16 run `41094504957` showed failed jobs with **0 execution steps** and no assigned runner; execution around 3–5 seconds. Root cause is **unconfirmed** by available GitHub API. No reliable evidence of actual Blender launch.
- Invoked `rerun_failed_workflow_run_jobs` for **41094504957**, accepted by GitHub; attempt #3 **FAIL** in five seconds with zero steps. P19 retry returned 403 while already running; separately verified P19 attempt #2 **FAIL** in five seconds/zero steps. Not a Blender failure.
- **Actual latent C01-16 code bug in both Wave01/Wave02**: `blend_file.read_bytes()[:7] != b"BLENDER-"` compares 7 bytes to 8 and always returns TRUE even for a valid Blender file. Producer must change to `not blend_file.read_bytes().startswith(b"BLENDER-")` or equivalent; otherwise CI will fail after runtime restoration. QA did NOT edit producer scripts.

## P19 priority repair retest
Exact Git LFS SHA on current C01-19 PR branches **unchanged** versus PASS04 for P19-01, P19-02, P19-05, P19-07, P19-08. P19-05/07/08 still have 1/19/7 zero-area **conservative fan stress** candidates; P19-01/02 13/11. Native FBX indexes alone show **no defective original polygons**. Stress-test findings are a FAIL of mandatory safe export-triangulation preflight, **not proof of actual importer failure**. No new successful safe-triangulation source/FBX from Blender for P19 P0, so repairs **NOT CONFIRMED**. In particular do NOT claim P19-07 T-junction candidate is confirmed geometry defect.

## Per-model gate
See [36_MODELS_PASS05.csv](36_MODELS_PASS05.csv) and existing PASS04 full binary SHA records.

**Current 36 model QA outcomes: 0 FULL PASS / 5 FAIL preflight / 31 BLOCKED.**
P17/P18 14/14 **limited indexed topology PASS**, P19 8/8 **limited indexed topology PASS** but 5 export preflight risks, P15 7 binary bytes BLOCKED, P16 7 native binary files BLOCKED.

**Independent Blender 4.x open/export/reimport: NOT RUN. Unity 6 URP import, saved prefab, physical collider and clearance: NOT RUN.**

## Evidence / safe handoff
- Link to downloadable local QA artifact containing **22 original actual binary FBX**, 36 model CSV/JSON, parser and 9 actual-file tests is supplied in C01-02 PASS05 chat. The complete binary ZIP is **not stored in GitHub PR**.
- Owner tasks: C01-19 successfully run source Blender BMesh triangulation of P19-05/07/08 and source check P19-01/02, pin NEW binary SHA and render BEFORE/AFTER; C01-16 correct exporter byte-length bug and supply seven Blender native binaries after resolving runner; C01-15 provide seven hydrated FBX for independent inspection; C01-10 execute Unity6 imported FBX prefab/clearance.
- **No source geometry or ship files edited. No branch merge. PR #13 stays Draft; issues #33/#30 remain open.**
