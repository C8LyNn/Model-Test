# C01-17 — PASS04 real binary FBX source crosscheck

**Owner** C01-17 | **Parent** #30 | **Wave** #33 | **P0 prototypes** P17-04/P17-05 | **Date** 2026-10-30

**Evidence source:** 7 actual hydrated FBX 7400 files from previous PASS03 successful native Blender 4.0.2 exported Actions artifacts. All SHA256 digest values crosschecked against producer FBX roundtrip manifest. This PASS04 audit reads **genuine binary FBX vertices, polygon indices, per-polygon normals and UV0 records**, NOT primitive viewer reconstructions.

## Before (actual native Blender PASS03) → after (real hydrated binary FBX PASS04)

| ID | Blender before → FBX after V/E/F/T | Boundary/nonmanifold before → after | Cross-part coplanar candidate pairs | FBX SHA256 prefix |
|---|---:|---:|---:|---|
| P17-01 | 408/510/204/204 → 136/306/204/204 | 408 → 0 | 0 | fca67dad3e35 |
| P17-02 | 480/600/240/240 → 160/360/240/240 | 480 → 0 | 0 | af858385a0ab |
| P17-03 | 456/540/208/208 → 128/312/208/208 | 456 → 0 | 0 | 749c0a6e3df5 |
| P17-04 | 696/870/348/348 → 232/522/348/348 | 696 → 0 | 1 | 093be5df6e60 |
| P17-05 | 480/600/240/240 → 160/360/240/240 | 480 → 0 | 1 | 3fa314481f87 |
| P17-06 | 312/390/156/156 → 104/234/156/156 | 312 → 0 | 3 | d9fcaf1a5b0f |
| P17-07 | 456/570/228/228 → 152/342/228/228 | 456 → 0 | 1 | c9e4b221c96d |

Aggregate: original 3288V/4080E/1624F/1624 triangles → repaired 1072V/2436E/1624F/1624 triangles. Unexpected boundary/nonmanifold 3288→0. Exactly 130 deliberately separated mesh parts preserved. All 7 exports contain **zero n-gons**, zero mesh-local T-junction candidates, zero degenerate triangles, zero duplicated polygon index faces, zero loose vertices/zero edges, zero reversed polygon normals and zero missing UV0 mesh parts.

## PASS04 cross-part narrow phase on actual FBX

Same-part T-junctions 0/7; cross-part vertex-on-edge candidates 0/7 under numerical tolerance on mesh components. Narrow-plane 2D polygon intersection screen identified **six** distinct pairs of same-facing coplanar component faces. These are **REVIEW CANDIDATES**, not automatically confirmed visible defects; no blind weld or part movement performed:

- P17-04: `CableBar` × `Underframe` — area 0.003750003 m²
- P17-05: `DisplayBezel` × `LowerDisplayRail` — area 0.059199984 m²
- P17-06: `Actuator` × `SwitchBlack` (0.00468 m²); `CoverBottomLip` × `Housing` (0.000275 m²); `Actuator` × `SwitchPlate` (0.000156 m²)
- P17-07: `RemovableCore` × `RemovableHandle` — area 0.002274999 m²

These may represent intended interpenetrating mechanical assembly surfaces. Need real shaded/wireframe inspection for z-fighting and visibility before applying surgical changes. Across-part general BVH self-intersections/non-coplanar intersections are **NOT RUN**. A candidate is NOT a proven defect.

## Actual Blender and Unity

- Native Blender 4.0.2 **PASS03** real source `.blend` repair plus FBX export/re-import **7/7 PASS** with exact source SHA records, actual Blender shaded/wireframe before/after and native `.blend`/`.fbx` in existing PRs.
- W01 true Blender pass: https://github.com/C8LyNn/Model-Test/actions/runs/41089779966
- W02 true Blender pass: https://github.com/C8LyNn/Model-Test/actions/runs/41088800979
- **PASS04 added strict Blender-vs-FBX script and CI** in both PRs; new GitHub Actions runner jobs terminated before running steps (runner_id=0, steps=[]). Retried once. **NEW PASS04 Blender CI NOT RUN / infrastructure BLOCKED**. Do not cite failed startup as mesh failure.
- Unity 6 URP FBX import, native prefab generation, colliders, PlayMode and corridor clearance: **NOT RUN**.
- C01-02 independent technical topology and visual-interface QA: **PENDING**, no full acceptance. Both PRs remain Draft.

## Files

- W01 existing draft PR: https://github.com/C8LyNn/Model-Test/pull/17 ; branch `c01/props-17-controls`.
- W02 existing draft PR: https://github.com/C8LyNn/Model-Test/pull/23 ; branch `c01/props-17-wave02`.
- Complete per-part source/weld before-after metrics, actual Blender rendered captures and SHA256: `C01InteriorProps_Source/QA/PASS03/` and `C01InteriorProps_W02/QA/PASS03/`.
- New P04 strict original source-vs-FBX script: `Tools/pass04_strict_fbx.py` per existing branch. Requires actual Blender Actions runner before PASS04-specific in-editor validation.

**Changes PASS04:** tests and forensic reports only. Original repaired meshes unchanged. **No unnecessary weld, no new meshes, no redo of P19 defects, no architecture edits, no merges**.

**Next gate:** C01-02 re-run exact FBX SHA audit, inspect six candidate assembly interfaces in real render and decide INTENTIONAL vs defect; C01-10 run Unity import/prefab/physics. C01-00 controls final gate.
