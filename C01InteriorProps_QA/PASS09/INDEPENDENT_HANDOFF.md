# C01-02 — PASS09 / Independent source mesh QA

**Scope:** 36 original models P15–P19. Read-only independent inspection of actual GitHub OBJ and producer source files, no new model/ship edits, no merge.

## Producer #18, actual pre/post OBJ source verification

| Model | Old OBJ git blob | Current OBJ git blob | Polygon count | Fan triangles | Oriented geometry+UV+normal+material equality |
|---|---|---|---|---|---|
| P18-01 | 5787314578f8042f6f64bdafb6ccc421b1621b5f | 665b940dd9ba1ab9c7a1339a8a395bdc35fe72b9 | 180 → 90 (90 quads) | 180 → 180 | PASS, 0 mismatches |
| P18-02 | c451166192d6035f382a5b926944d00b5be7bf21 | 6200a15fdf29a23d4e2106359fdaed347b1656fd | 204 → 102 (102 quads) | 204 → 204 | PASS, 0 mismatches |
| P18-03 | 77b544df2e1ddb9752eb3bf9e8613a9327e94066 | 901959fa24658c9beb1439fc06805f3feb8aa069 | 348 → 270 (78 quads + 192 triangles) | 348 → 348 | PASS, 0 mismatches |

Source before commit 19a8fa905c4fbc3921e1b3b4924fbdd629e3d134; after 41d5f6a46bf9c4f6fb9a86f331a6214ec590387a. Actual vertex coordinate strings, UV coordinate records, corner normals and object order exactly equal before/after. Indexed source OBJ faces were triangulated deterministically and compared by oriented triangle signature plus object, material, UV0 and corner normals: **732/732 triangles identical**. This supports authoring-topology cleanup only. Existing Blender .blend and binary FBX Git LFS pointers remain the old PASS03 SHAs: P18-01 FBX 84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939; P18-02 FBX 5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f; P18-03 FBX 639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19c5e165. Native Blender/FBX re-export **NOT RUN**.

## Producer #26, P18-07 source contact

Actual current source build_wave02.py commit ce5f80db7121f435b09e3bed17d7daa93b4147c8 changes only the Front_Lock center Unity Z 0.164 → 0.165m (+1mm), one production line, from previous commit f76233ab4ea67ce44647e175342654072739b3b2. Existing lid exposed front face remains Z=0.170m, new lock front face Z=0.171m, old was Z=0.170m. **Source analytical separation PASS.** Measured source assembly envelope: previous 0.560 × 0.340 × 0.380m W/D/H → 0.560 × 0.341 × 0.380m: **1mm depth increase requires C01-01 nominal-tolerance check and visual native confirmation.** Actual .blend Git LFS OID 302a6832594702c7eff11a486d9e581c159993ff7b7f5c5abe124bf29edbc8d8 and FBX OID 56c19c7ea12fe2713ae30b72ecf8771613f794d4a2e8c4da18c41cb9dd825e08 are still pre-fix. Blender/Unity NOT RUN.

## Release gate, 36 models

PASS06 has 22 previously hydrated binary FBX P17-P19 with SHA-pinned independent byte tests; this is historical, not 36 newly exported PASS09 models. P19-01/02/05/07/08 remain five export-triangulation FAIL_PREFLIGHT risks (not proven Unity failure). P16-01…07 still lack actual native Blender+binary FBX; P15-01…07 lack independent hydration of final Git LFS FBX; P17-05 is source-updated but its .blend/.fbx remain old. Updated 36 rows in PASS09/36_MODELS_PASS09.csv.

**Runtime:** no blender, bpy, git-lfs or Unity in the QA environment; DNS resolution to Blender/GitHub/PyPI download hosts fails. GitHub Actions 41108063941 and 41103140385 end before runner allocation (runner_id=0, steps=0). Administrative root cause unknown; no payment changes, no ineffective reruns. NEEDS_OWNER_ACTION: restore runner eligibility after inspecting GitHub Actions General/Runners/job annotation and read-only usage/budgets, or execute existing owned native producer scripts on Windows Blender 4.x + Git LFS, producing actual saved source .blend, binary FBX, reimport evidence, wireframe BEFORE/AFTER and exact new SHA. Then C01-02 does independent full QA, C01-10 Unity.

## ENV01–ENV05 cross-project exchange

Checked B01 RoboRougelike Draft PR #288 ENV01, #290 ENV02, #291 ENV03, #289 ENV04 and #293 ENV05. Their v002 workflows show real historical Blender 4.x save/reopen, GLB exporter validation, manifold/degenerate and pivot tests, authentic image/byte SHA receipts, plus separation of Unity NOT_RUN; producer completion does not equal independent Unity or HQ acceptance. Transferable only QA methodology, not asset bytes or rights. C01 acceptance specifically requires native Blender binary FBX rather than GLB.

## Verdict

New actual native source repairs: 0. New Blender roundtrip: 0. New Unity PASS: 0. Fully accepted: 0/36. New independently source-verified P18 edits: 4 IDs (3 OBJ topology equivalence PASS, 1 analytic contact-plane PASS with dimensional warning). Source-only PASS must never be counted as final FBX PASS.

Machine details: P18_REAL_SOURCE_EQUIVALENCE.json ; 36_MODELS_PASS09.csv.