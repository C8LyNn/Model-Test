# C01-03 — PASS05 / 36-model SHA256 + BEFORE / AFTER release gate

**Owner:** C01-03 (Asset Library & Versioning) · **Issue:** [#33](https://github.com/C8LyNn/Model-Test/issues/33), parent [#30](https://github.com/C8LyNn/Model-Test/issues/30) · **PR:** [#27](https://github.com/C8LyNn/Model-Test/pull/27) (DRAFT).

**Rule:** before/after below is producer-sourced source geometry report metadata, not a new mesh repair performed by C01-03. Current file identity is reconciled to C01-02 independently hydrated FBX SHA where available; an LFS pointer is a reference to source bytes, not evidence C01-03 downloaded/re-tested the binary in Blender/Unity.

## Actual results

- **36/36 assets** have pinned immutable previous revision, candidate producer source commit, producer V/E/F/T BEFORE→AFTER and explicit QA gates.
- **22/22 P17–P19** source FBX Git-LFS SHA256 OIDs equal SHA256 of the **actual hydrated binary FBX independently inspected by C01-02 in PASS04**. They identify exactly the same export bytes; *not* a new 22-model re-audit in PASS05.
- **P15-01–07:** both source `.blend` and FBX expected SHA256 from actual LFS pointers recorded, but C01-02 has **NOT hydrated independently** these seven latest native FBX. Pending.
- **P16-01–07:** producer static OBJ + ASCII FBX Git object SHA crosschecked 7/7; sources `.blend` absent, binary Blender-origin `.fbx` absent, Blender roundtrip NOT RUN.
- **P19-01/02/05/07/08:** same actual FBX SHA as C01-02's P1 risky fan/concave triangulation records. FIVE unresolved QA FAIL; no demonstrated Unity importer crash.
- **14/14** source registry and policy checks PASS (GitHub connector JS; full result `Pass05/VALIDATION_RESULT.json`). NO Blender executable or Unity executable in C01-03 tool host.
- **GitHub Actions run 41095968082** re-run attempt 2 FAILED: **10 jobs**, every `runner_id=0`, `runner_name=''`, `steps=[]`, billable Ubuntu duration **0ms**. This is pre-runner/assignment failure; root cause still unknown. This is **not** a pipeline Blender/mesh test failure.
- **0/36 release QA approved, 5 static export FAIL, 31 BLOCKED, 0 producer geometries repaired by C01-03**.

## 36-model matrix

V/E/F/T = vertices / edges / faces / nominal triangles as declared by producer's real source reports; errors are **local reported counts only**, not universal non-manifold/T-junction/overlap error totals. Any P19 FBX triangulation risk overrides the producer's local zero-defect count.

| Model | Family | V/E/F/T BEFORE | V/E/F/T AFTER (producer) | Local errors BEFORE→AFTER | SHA evidence | QA triangulation | Full QA |
|---|---|---|---|---|---|---|---|
| P15-01 | C01-15 | 288/432/178/508 | 288/432/178/508 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-02 | C01-15 | 176/264/120/288 | 176/264/120/288 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-03 | C01-15 | 192/288/144/288 | 192/288/144/288 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-04 | C01-15 | 918/1722/852/1740 | 918/1722/852/1740 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-05 | C01-15 | 2274/4494/2238/4512 | 2274/4494/2238/4512 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-06 | C01-15 | 3744/7308/3630/7356 | 3744/7308/3630/7356 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P15-07 | C01-15 | 2794/5400/2646/5460 | 2770/5376/2642/5420 | 0→0 | LFS expected only | NOT RUN | BLOCKED |
| P16-01 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-02 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-03 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-04 | C01-16 | 168/210/84/84 | 56/126/84/84 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-05 | C01-16 | 168/210/84/84 | 56/126/84/84 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-06 | C01-16 | 216/270/108/108 | 72/162/108/108 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P16-07 | C01-16 | 120/150/60/60 | 40/90/60/60 | 0→0 | OBJ + ASCII (no Blender/FBX) | NOT RUN | BLOCKED |
| P17-01 | C01-17 | 408/510/204/204 | 136/306/204/204 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-02 | C01-17 | 480/600/240/240 | 160/360/240/240 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-03 | C01-17 | 456/540/208/208 | 128/312/208/208 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-04 | C01-17 | 696/870/348/348 | 232/522/348/348 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-05 | C01-17 | 480/600/240/240 | 160/360/240/240 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-06 | C01-17 | 312/390/156/156 | 104/234/156/156 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P17-07 | C01-17 | 456/570/228/228 | 152/342/228/228 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-01 | C01-18 | 120/270/180/180 | 120/270/180/180 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-02 | C01-18 | 136/306/204/204 | 136/306/204/204 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-03 | C01-18 | 208/522/348/348 | 208/522/348/348 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-04 | C01-18 | 192/288/114/348 | 192/288/114/348 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-05 | C01-18 | 80/120/60/120 | 80/120/60/120 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-06 | C01-18 | 88/132/66/132 | 88/132/66/132 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P18-07 | C01-18 | 80/120/60/120 | 80/120/60/120 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P19-01 | C01-19 | 88/132/66/132 | 133/205/78/254 | 0→0 | C01-02 hydrated = current LFS | FAIL P1 | BLOCKED |
| P19-02 | C01-19 | 72/108/54/108 | 118/194/86/216 | 0→0 | C01-02 hydrated = current LFS | FAIL P1 | BLOCKED |
| P19-03 | C01-19 | 64/96/48/96 | 72/112/48/128 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P19-04 | C01-19 | 72/108/54/108 | 72/108/54/108 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P19-05 | C01-19 | 88/132/66/132 | 88/140/66/148 | 0→0 | C01-02 hydrated = current LFS | FAIL P1 | BLOCKED |
| P19-06 | C01-19 | 56/84/42/84 | 56/84/42/84 | 0→0 | C01-02 hydrated = current LFS | PASS (static only) | BLOCKED |
| P19-07 | C01-19 | 104/156/78/156 | 136/204/78/252 | 0→0 | C01-02 hydrated = current LFS | FAIL P1 | BLOCKED |
| P19-08 | C01-19 | 96/144/72/144 | 149/241/100/282 | 0→0 | C01-02 hydrated = current LFS | FAIL P1 | BLOCKED |

## Five independent unresolved export risks at unchanged exact binary SHA

| Asset | Current binary SHA256 (audited by C01-02) | Naive fan degenerate candidates | >2-use fan edge candidates |
|---|---|---:|---:|
| P19-01 | `47b4d6f2017626b6084584fbf0bad907505eb9e194703032d83af5315c1a4009` | 13 | 0 |
| P19-02 | `a42a57d168164cea335de3c9ee175a3074edca4a48b707a14beadbea16a8b6d8` | 11 | 5 |
| P19-05 | `64156363cb5007831c243aeea50d5e59c862cc98b27cb12dd2f8af5b3c019892` | 1 | 1 |
| P19-07 | `88b32fe2f5ddf981eecdc0469088f4e23e07c4c605a1db7bb9689a0b6011d585` | 19 | 2 |
| P19-08 | `cbbea5435f8326e06fb5f43237986594df044c0e3ff94100fc44f856dce35ae2` | 7 | 3 |

## Evidence and version rules

- Complete machine-readable source version lock: `Pass05/repair_ledger.json`; family ownership references: `Pass05/provenance_P15.json` through `provenance_P19.json`.
- Source independent QA: `C01InteriorProps_QA/PASS04/36_MODELS_GATE.csv` and `HYDRATED_BINARY_FBX_SHA256.csv` in QA PR #13.
- Original SHA256 before repair preserved from `Pass04/repair_ledger.json` / `Pass03/repair_ledger.json`; all candidate AFTER versions unapproved. No overwrite of an accepted revision.
- Every future changed FBX invalidates any prior approval tied to the old SHA; a new independent C01-02 run must confirm actual hydrated binary at exact final sha, plus Blender roundtrip and Unity import if required for release.
- Release gate does **not** auto-promote a validated manifest, green producer CI, successful model LFS pointer, source claims or standalone Python checks.
- **Blender reimport by C01-03:** NOT RUN. **Unity 6 URP:** NOT RUN. **Full self-intersection/coplanar screen for all 36:** NOT RUN.

## Required next actions (owner handoff)

1. **Runner owner / C01-00:** inspect billing/actions runners settings and resolve why jobs fail prior to allocation; evidence in `Pass05/CI_RUNNER_DIAGNOSIS.md`.
2. **C01-19:** explicitly triangulate P19-05/07/08, then P19-01/02, reexport in real Blender; provide changed `.blend`, binary `.fbx`, true SHA256, native FBX export→import, topology before/after and true renders. **Do not weld T-junction candidates indiscriminately.**
3. **C01-16:** execute native 7-model Blender generator, commit true `.blend` and binary FBX with version and real roundtrip evidence; preserve rotor separated.
4. **C01-15:** enable independent access to 7 actual binary FBX (not only LFS pointers), then QA per SHA.
5. **C01-02:** audit all final 36 real hydrated binary FBX; mark export/topology/Blender/Unity separately, sign exact release SHA.
6. **C01-10:** import approved candidate native FBX into real Unity 6 URP, create prefabs/scene, verify collision and corridors; no pseudo-geometry or changes to ship.
7. **C01-03:** ingest new hashes from producer and QA evidence, update after version only when file bytes actually changed; do not merge PR #27.
