# C01-10 — MESH REPAIR PASS05 | EXECUTION AND UNITY INTEGRATION REPORT

**Date:** 2026-10-30. **PR:** #11 (existing Draft). **Issues:** #33 #30 #9 #8. **Role:** source model staging, Unity 6 URP import and prefabs after C01-02 gate. **No ship or producer mesh changes, no merge.**

## 1 — Concrete work in PASS05

- Fixed real C# bug in `Assets/C01InteriorProps/Editor/Pass04SourceImportAudit.cs`: previous discovery scanned the whole `Assets/C01InteriorProps`, causing a genuine staged Pxx-yy FBX to conflict with an older source FBX of the same ID. Discovery now ONLY selects `Assets/C01InteriorProps/Pass04Incoming/<ID>/<ID>.fbx`.
- Added `ValidateStagingReceipt(id, sha)` to the Unity C# importer. It requires an actual staging CSV from the LFS staging script with exact ID, `STAGED_SOURCE_NOT_QA_APPROVED`, SHA-256 of hydrated binary FBX bytes and exact staging path. Missing/duplicated entries and SHA/path mismatches fail source precheck.
- Repinned `source_stage_36.json` to ten then-current producer PR HEAD SHAs (18 asset pin changes) and synchronized all 36 handoff entries. Commit pins are immutable but NOT automatically QA-approved binary hashes.
- Updated `PASS04_36_MODEL_HANDOFF.csv` to C01-02's PASS04 **22/36 real FBX** records (previous C01-10 table was stale at 12/36). Includes five current P19 export FAIL risks and 14 untested models.
- Inspected the actual GitHub LFS **pointer OID** of the five source exports P19-01/02/05/07/08 on the producer branches. All are UNCHANGED versus QA's recorded SHA-256. No newly fixed final binary export is evidenced. The pointer is provenance only: full binary FBX was NOT parsed by C01-10.
- Inspected all seven P16-01..07 actual repository FBX file signatures. Every one is **ASCII FBX 7.4**, not required binary Blender FBX; neither lighting PR #12 nor #28 currently contains native `.blend` files.
- Added `PASS05_ACTUAL_SOURCE_GATES.json`: exact five P19 Git LFS binary OIDs and sizes, seven P16 original Git blob SHAs/signatures, plus precise tool and CI status.

## 2 — Actual source triage

| Model | C01-02 last potential P1 exporter issue | Git LFS expected binary SHA256 | PASS05 source change | Unity |
|---|---:|---|---|---|
| P19-01 | naive-fan degenerate candidates 13 | `47b4d6f2017626b6084584fbf0bad907505eb9e194703032d83af5315c1a4009` | none: same OID | NOT RUN |
| P19-02 | 11 | `a42a57d168164cea335de3c9ee175a3074edca4a48b707a14beadbea16a8b6d8` | none: same OID | NOT RUN |
| P19-05 | 1 | `64156363cb5007831c243aeea50d5e59c862cc98b27cb12dd2f8af5b3c019892` | none: same OID | NOT RUN |
| P19-07 | 19 | `88b32fe2f5ddf981eecdc0469088f4e23e07c4c605a1db7bb9689a0b6011d585` | none: same OID | NOT RUN |
| P19-08 | 7 | `cbbea5435f8326e06fb5f43237986594df044c0e3ff94100fc44f856dce35ae2` | none: same OID | NOT RUN |

These C01-02 P1 FAIL results are compatibility **risk gates** from genuine indexed binary FBX, not proof of Unity using a naive triangle fan. Do not infer an actual Unity degenerate without running the engine. P19-07/08 T-junction candidates still need source-specific adjudication.

**P16-01–07:** 7/7 original checked signatures start with ASCII FBX declarations, 0/7 matching `Kaydara FBX Binary`, 0/7 native `.blend` in the latest inspected producer PR diff. Export and native Blender roundtrip BLOCKED; no attempt to fabricate replacements in C01-10.

## 3 — Independent QA source of truth

C01-02 PASS04 `C01InteriorProps_QA/PASS04/36_MODELS_GATE.csv`: **22/36** real hydrated final-at-tested-SHA FBX independently inspected (P17 7, P18 7, P19 8); **14/36** P15/P16 not yet independently verified. Five potential P1 export FAIL: P19-01/02/05/07/08. **0/36 full QA APPROVED**. Per-model numeric V/E/F/tri and flags carried without invented Blender/Unity values in `PASS04_36_MODEL_HANDOFF.csv`.

## 4 — Testing and CI diagnostics

- **26/26 static GitHub source / provenance / PR-scope checks PASS** after PASS05 modifications. Tested ID completeness, strict SHA+staging receipt gate, source-only mesh import, no primitive reconstruction, diagnostic-only prefab paths, 22 binary QA entries, five P19 risk IDs, seven P16 ASCII records and zero ship/producer file edits. This is NOT C# compilation.
- **GitHub Actions run #41095999644 rerun** (attempt 2) result FAILURE: started 17:28:51 UTC, completed 17:28:53 UTC, `runner_name=""`, `steps=[]`. No Python, no Blender, no Unity step started; treat as **CI_EXECUTION_NOT_RUN / RUNNER_ALLOCATION_BLOCKED**, root cause not proven. Similar failures across unrelated project workflows.
- Repository is PRIVATE; GitHub-hosted Actions can be stopped by budget/billing settings, among other causes. GitHub account Billing & licensing > Budgets and alerts / Actions usage should be checked by account owner. Current official GitHub status does not establish a 30 Oct platform Actions incident; do NOT assert an outage or exhausted quota without evidence.
- Local C01-10 runtime: Git and Python available; Git LFS, Blender 4.x, Unity 6 URP Editor **NOT INSTALLED**, no hydrated original `.fbx` source in the runner. Therefore staged binary SHA execution, real Blender source roundtrip, actual Unity prefab/scene creation, shader/collider/3m clearance and PlayMode **NOT RUN**. No native Unity files generated.

## 5 — Next exact executable task

1. C01-19 executes existing Blender native explicit triangulation scripts on PR #29 and #15, publishes new `.blend`+binary `.fbx` and actual SHA256, same-silhouette topological before/after, real Blender roundtrip. C01-16 produces seven genuine native files and binary FBX.
2. C01-02 independently re-audits final source FBX exact SHA, resolves potential fan/T-junction reports and signs final topology, FBX and Blender gates. C01-03 repins verified AFTER SHA. No source self-acceptance.
3. On an actual Unity 6000.3.14f1 URP workstation, check out Draft PR #11; hydrate sources with `py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo . --apply`; select Editor menu `C01 > Mesh Repair PASS04 > 00 / 01 / 02`. The importer now checks the staged SHA receipt and produces QA-ONLY native prefab instances/inspection scene exclusively from real FBX sources.
4. Run actual Unity geometry, URP shaders, collider/pivot, door/3m corridor, stairs/lifts/PlayMode checks and screenshots on unchanged ship, then C01-02 reviews and C01-00 decides merge.

**FINAL:** `CODE FIX COMMITTED / SOURCE PROVENANCE VERIFIED / STATIC 26 PASS / P19 NEW REPAIR 0/5 / P16 BINARY 0/7 / UNITY NOT RUN / ACTIONS RUNNER BLOCKED / FULL QA 0/36`. No Wave03, no unauthorized merge.
