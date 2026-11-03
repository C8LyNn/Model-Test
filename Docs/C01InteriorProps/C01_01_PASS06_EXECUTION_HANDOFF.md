# C01-01 — MESH REPAIR PASS 06 / source-validation blocker removed, runtime owner action

**Date:** 2026-10-30. **Scope:** C01-01 topology standards, direct minimal source-validation hotfix in C01-16's existing PR #12 and #28. **Dispatch:** #33 comment 6529370725, parent #30. **No new models, source mesh editing, redesign or merge.**

## Actual code changes committed in existing producer branches

| File type | W01 PR #12 branch c01/props-16-lighting | W02 PR #28 branch c01/props-16-lighting-wave02 |
|---|---|---|
| Blender Python runtime check | ci_pass04_native.py, commit `4f7e0081417d9b5d1a7de958a03bb2358270315a` | commit `07543fbfa0f40ae8df235081860d60b96236464e` |
| Native signature test 7 cases | test_native_blend_header.py, commit `dc47218ee34e063d7660bb24c610f0fec6527e56` | `34d00ccbed3fd6cf13a3c9766480c218f015630a` |
| Windows PowerShell runtime check | run_pass04_windows.ps1, commit `b26a6f4b7d2af40db74ed10c08a063edd503895f` | `7e68ace6ed30c929a0eab13569ba2cb1dabb0452` |
| CI test integration | .github/workflows/c01-16-pass04-w01.yml, commit `eadeb43d98571017c31b41e587ade8b84ef94da5` | c01-16-pass04-w02.yml, commit `8d24453d8c44026cf7ead9fc8282c3f8294f1250` |

**Defect 1:** Python compared 7 source bytes against 8-byte `BLENDER-`, so always rejected a genuine Blender source. Now checks binary startswith `BLENDER-`.

**Defect 2:** Windows PowerShell fallback also read only 7 bytes then compared string with `BLENDER-` (8 bytes). Now reads 8. Both PRs retain existing object/geometry/rotor logic unchanged.

Seven tests are committed to each producer branch for actual CI execution. Locally, a separate 12-assertion Python stdlib regression **passed 12/12** against two **real archived producer Blender .blend bytes** (P19-01 native source SHA256 `8327069f58c9991a560234091ca5536b5946dc5b907e8b36bc4f5f6ec245c60f`, P19-05 native source SHA256 `a308fe19455a68d7452060a33d6a8f5e807e648468d7ddc148913b731dffc86b`). Both began `BLENDER-v400`. The test explicitly demonstrates the previous check rejects genuine native files, new 8-byte logic accepts them, and rejects truncated/LFS/ASCII-FBX files. This is **byte-level signature verification**, NOT execution of Blender or C01-16 models.

## Runner and environment status

GitHub Actions earlier C01-01 run #41099146648 failed before allocation (runner_id=0, steps=[] on independently scheduled jobs), so Blender never started. The newly patched W01 run #41101370697 and W02 #41101376942 were **QUEUED** as last observed, not verified as completed in this report.

Current tool environment checks:
- No `blender` executable, no importable `bpy`, no `git-lfs` command.
- Package apt cache did not offer a Blender binary; remote download DNS to download.blender.org failed.
- GitHub connected app can retrieve public workflow runs and repo metadata (admin permission according to repository object), but its fetch endpoint expressly rejects repo Actions runners and Actions permissions settings paths. This cannot establish account billing, runner budget or eligibility root cause. **No payment/budget changes made**.
- Unity 6 URP absent. Blender/FBX roundtrip and Unity **NOT RUN** for PASS06, no seven P16 binaries newly produced by C01-01.

## Exact next executable Windows owner procedure

Check GitHub repository Settings > Actions > Runners and General, and account Settings > Billing and licensing > Actions usage/budgets (read-only first), as well as workflow annotations for **queued** jobs. Do NOT assume billing root cause or spend money without consent.

If hosted runners cannot execute, use a PC with **actual Blender 4.x and Git LFS**, with authenticated repo access. Check Blender 4.x path using `Get-Command blender` or point to the actual installed blender.exe. Execute existing producer Windows runners:

W01:
```powershell
git clone --branch c01/props-16-lighting https://github.com/C8LyNn/Model-Test.git C01-P16-W01
cd C01-P16-W01
git lfs install
git lfs pull
& ".\C01Source\Lighting\MeshRepairPASS04\run_pass04_windows.ps1" -BlenderExecutable "C:\path\to\blender.exe"
```

W02 in a separate checkout:
```powershell
git clone --branch c01/props-16-lighting-wave02 https://github.com/C8LyNn/Model-Test.git C01-P16-W02
cd C01-P16-W02
git lfs install
git lfs pull
& ".\C01Source\LightingW02\MeshRepairPASS04\run_pass04_windows.ps1" -BlenderExecutable "C:\path\to\blender.exe"
```

Result required: **7 actual native .blend**, **7 actual Blender binary FBX**, 7 real Blender export→import reports, SHA-256 and preserved rotor P16-06. Verify outputs against C01-02 independently; do not auto-commit / merge without inspected changes.

C01-19 still owns actual five model source triangulation and Cube.001 polygon #59 repair in existing PR #15/#29. C01-02 still owns independent 36 exact-SHA real FBX QA; C01-10 real Unity import. No model can inherit PASS just because its header validator now works.

## PASS06 quantitative status for this C01-01 task

- **Actual source Blender mesh files repaired by C01-01:** 0 (not geometry owner; no Blender runtime).
- **Actual Blender/FBX roundtrip tests newly completed:** 0.
- **Independent 36-model topology QA PASS newly confirmed:** 0.
- **Unity 6 URP PASS newly confirmed:** 0.
- **Real execution-ready blocker fix:** 4 runtime validation files fixed (two Python + two PowerShell), 2 regression test files and 2 workflows updated; 12/12 local real-byte magic checks PASS.
- **Critical unresolved:** host runner allocation and native executable / Git LFS access, five source P19 triangulations, seven P16 native exports, 36 C01-02 independent QA, actual Unity.
- **Status:** `NEEDS_OWNER_ACTION` for runner/Windows environment; `NOT_RUN` for native engine tests; independent QA `PENDING`. Draft PR #31 remains unmerged.
