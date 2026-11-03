# C01-03 — MESH REPAIR PASS07 / REAL SOURCE SHA-256 INTAKE

**Issue:** #33 / parent #30. **Existing Draft PR:** #27, no merge, ship changes or new models.

## Real verified work

- **36/36** assets pinned to the current producer PR commit SHA and earlier immutable BEFORE SHA. Real independent C01-02 PASS06 matrix source Git blob: `104ef23e5ced350d1599a0e847606a1de3bda802`.
- **P17-05 actual editable glTF changed** in C01-17 PR #23: only `LowerDisplayRail.translation` changed from `[0,0.957,0.12]` to `[0,0.957,0.121]` (+1 mm Z). Verified by comparing actual two GitHub glTF JSON payloads; reversing that one translation yields EXACT original JSON: geometry buffers, UV, normals, meshes, materials and all other fields unchanged.
- **P17-05 genuine source SHA-256:** BEFORE `02d4c44471d5cf6237c0123fcd6a24c5427f2c5ce141d4a5313e51771d39e9d4`, AFTER `cc4b0e9a7b7a78c461baca467f0ca433b81c0c60d14895531af9ddf556371378`; corresponding real Git blob SHA-1 `4a6d45a0d84086e2bec964545346e150e2137fe2` → `abb88f40afa5502130fad4bb2f1f9abb46fe3ac8`.
- **P17-05 native Blender/FBX are NOT updated**: most recent independently audited FBX SHA `3fa314481f87d66f9a878936028b809cd78440d781146a058594e28f3f4e1740` is still the ORIGINAL export. The glTF source edit is NOT release approval.
- **C01-16 now fixed Python and PowerShell eight-byte `BLENDER-` header checks** on both actual producer branches (PR #12 and #28); the fix is CODE ONLY, there are no new seven real native .blend and binary FBX files.
- **C01-19** newer commits in PR #15 and #29 update only tools and scripts; no corresponding changed .blend or FBX binaries. Five original risky export triangulations persist; offline P19-02/05/07/08 FBX candidates remain quarantined, not promoted to Blender-native repairs.
- **18/18 checks PASS** in `Pass07/VALIDATION_RESULT.json` for actual source provenance and catalog state. These tests are NOT Blender or Unity.

## Full 36-model gate

| Group | Count | Actual evidence | Release status |
|---|---:|---|---|
| C01-15 | 7 | Source .blend + FBX Git LFS OIDs; no independent final binary hydration | 7 BLOCKED |
| C01-16 | 7 | OBJ/ASCII FBX only; 7 native .blend and binary FBX missing | 7 BLOCKED |
| C01-17 | 7 | Earlier independently audited 7 original binary FBX; P17-05 glTF 1 mm fix not exported | 7 BLOCKED |
| C01-18 | 7 | Earlier independently audited 7 original binary FBX; no new confirmed defect fix | 7 BLOCKED |
| C01-19 | 8 | Earlier independently audited 8 original binary FBX; 5 static fan-triangulation risks | 5 FAIL / 3 BLOCKED |
| **TOTAL** | **36** | **22** previously independently hydrated, 14 not independently available as final binaries | **0 FULL APPROVED** |

QA details: P19-01/P19-02/P19-05/P19-07/P19-08 remain FAIL_EXPORT_PREFLIGHT. P19-01 has a real invalid six-corner polygon (Cube.001 #59); candidates for T-junctions must not be blindly welded. No Unity importer failure is inferred from a fan stress test.

## Execution blocker and owner action

**NEEDS_OWNER_ACTION:** GitHub Actions run [41101786547](https://github.com/C8LyNn/Model-Test/actions/runs/41101786547) observed QUEUED with ten queued jobs, not a successful runner execution; earlier workflows consistently failed before runner allocation (runner_id=0, steps=[]). Exact GitHub runner root cause unverified; billing or budget not adjusted. C01-03 runtime has no `blender`, `bpy`, `git-lfs` or Unity and has no connected user Windows PC.

Owner must either restore GitHub Actions runner assignment (check Settings → Actions → General / Runners and account Actions billing/budgets without changing spend) or run existing C01-19 and C01-16 native Blender 4.x + Git LFS scripts on an existing Windows workstation. C01-17 must propagate source glTF P17-05 to genuine new Blender .blend and binary FBX, preserving UV/materials/pivot. Then C01-03 records actual new binary SHA, C01-02 independently tests and signs it and C01-10 tests Unity.

## PASS07 quantified results

| Metric | Verified in this pass |
|---|---:|
| Source glTF edits verified (P17-05) | **1** |
| New genuine native Blender .blend repaired | **0** |
| New real Blender→FBX→Blender roundtrip | **0** |
| Full independent QA approved | **0** |
| Actual Unity 6 URP import PASS | **0** |

**DO NOT MERGE or mark RELEASE APPROVED.** Machine-readable complete per-asset version lock: `Pass07/repair_ledger.json`.
