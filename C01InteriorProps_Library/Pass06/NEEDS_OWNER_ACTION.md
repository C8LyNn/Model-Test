# C01-03 — PASS 06 / NEEDS_OWNER_ACTION / FINAL SOURCE INTAKE

**Mission:** [C01-00 dispatch #33](https://github.com/C8LyNn/Model-Test/issues/33#issuecomment-6529370725) · **P0:** [#30](https://github.com/C8LyNn/Model-Test/issues/30) · **existing library Draft PR:** [#27](https://github.com/C8LyNn/Model-Test/pull/27).

## Verified state — no false "new repair"

**Owner C01-03** indexed source snapshots from *all 10 current producer Draft PRs* and compared each updated head with its exact PASS05 catalog head. **Zero changed paths with extensions `.blend`, `.fbx`, `.obj`** among commits since PASS05. This does **not** mean zero historical repairs: it means PASS06 did not yet receive any genuinely changed native model source/export from producers.

- **36/36** old/working source identities and producer before/after *reports* retained in [PASS06 repair ledger](./repair_ledger.json), with candidate versions kept separate from signed accepted versions.
- **22/36** P17–P19: current registered Git-LFS FBX SHA256 equals the 22 previously independently hydrated FBX from C01-02 PASS05. Prior static QA source evidence remains applicable to *unchanged bytes*, not a fresh Blender run.
- **7/36** P15: source `.blend` and export FBX Git LFS OIDs available, but C01-02 has not independently hydrated/QA'd these latest binaries.
- **7/36** P16: source OBJ + **ASCII FBX**, missing authentic native `.blend` and **binary Blender-exported FBX**.
- **5/36** P19 static export-triangulation risk FAIL: P19-01, P19-02, P19-05, P19-07, P19-08. P19-01 `Cube.001` polygon #59 is a self-intersection requiring real source-level review.
- **Four real offline re-triangulated binary FBX candidates from PASS05** P19-02/05/07/08 are *NOT* replacement source assets, not Blender roundtrips, not C01-02 approved. Their report-sourced hashes are quarantined in `repair_ledger.json`, separate from the actual current source FBX hashes.

### Actual outcome numbers

| Gate | Completed PASS06 |
|---|---:|
| New genuine native `.blend` repaired and verified | **0/36** |
| New actual Blender-to-binary-FBX-to-Blender roundtrip | **0/36** |
| Newly independently final QA approved by C01-02 | **0/36** |
| Actual Unity 6 URP importer/prefab PASS | **0/36** |
| Models with still-open P19 static export risk | **5** |
| Models FULL APPROVED | **0/36** |

## Why the pipeline cannot actually execute now

**GitHub Actions**: earlier real C01-03 rerun [#41095968082 attempt 2](https://github.com/C8LyNn/Model-Test/actions/runs/41095968082) returned ten failures, all `runner_id=0`, `steps=[]`, billed **0 ms**. Other simple producer smoke tests also failed before allocating `ubuntu-22.04`/`ubuntu-24.04` runners. **Root cause NOT established**: GitHub connector does not expose owner billing/runner-policy endpoints. Do not infer a billing issue, Blender test failure or syntactically invalid job YAML solely from this evidence. No further futile rerun was performed in PASS06.

**Available C01-03 host:** `blender` missing; `git-lfs` missing; `git ls-remote https://github.com/C8LyNn/Model-Test.git` returns `Could not resolve host: github.com`; Unity absent. This host cannot hydrate Git LFS or use a native Blender executable. Windows PC is not connected to this ChatGPT session.

## Exact required owner step (choose one)

**A. GitHub Actions administration:** Open GitHub **C8LyNn/Model-Test → Settings → Actions → General / Runners**, check whether GitHub-hosted Ubuntu runners and Actions permissions are enabled and organization policies permit scheduling. Then check **account/organization Settings → Billing and licensing → Actions usage/budgets/payment restrictions** and the failed run annotations. Do not increase spending limits or enter payment details without authorization. If runner availability should be normal, use GitHub Support and attach `41095968082` + `Pass05/CI_RUNNER_DIAGNOSIS.json`. Confirm a *single* smoke workflow actually obtains nonzero `runner_id` and executes a step before retrying Blender-heavy jobs.

**B. Existing Windows 11 workstation with real Blender 4.x and Git LFS:** Confirm that `blender.exe` exists and run `git lfs version`; use real producer branches in isolated local worktrees. **Important existing P16 validator bug:** PR #12 native Python script still does `read_bytes()[:7] != b"BLENDER-"`; both PR #12/#28 Windows fallback scripts compare 7 read characters with `BLENDER-` (8 characters). Fix both, preserving actual header check and adding a real regression test, *before* trying to run the P16 fallback (issue #4 notified).

### Existing, actual producer commands (Windows PowerShell from each worktree root)

```powershell
git lfs version
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --version
# Producer C01-19 W02 branch c01/props-19-furniture-wave02
pwsh -File Assets/C01InteriorProps/C01-19-W02/Tools/run_pass05_native_windows.ps1 -Wave W02 -BlenderPath 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
# Producer C01-19 W01 branch c01/props-19-furniture
pwsh -File Assets/C01InteriorProps/C01-19/Tools/run_pass05_native_windows.ps1 -Wave W01 -BlenderPath 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
# Producer C01-16 W01 branch c01/props-16-lighting, AFTER HEADER FIX
pwsh -File C01Source/Lighting/MeshRepairPASS04/run_pass04_windows.ps1 -BlenderExecutable 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
# Producer C01-16 W02 branch c01/props-16-lighting-wave02, AFTER HEADER FIX
pwsh -File C01Source/LightingW02/MeshRepairPASS04/run_pass04_windows.ps1 -BlenderExecutable 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
```

The path above is an **example**—replace with the installed Blender 4.x path. These commands are not claimed as executed. The W01 and W02 scripts need the **respective matching checkout branch**. Use the default **without `-Push` first**; require actual successful `.blend`, binary FBX, roundtrip QA JSON and logs. Only producer owners should commit/push their own reviewed source; do **not** merge.

**P19 source special case:** `P19-01 Cube.001 polygon #59` self-intersecting projected face needs Blender viewport review and safe correction before triangulating; do not blindly ear-clip it. P19-07/08 T-junctions are candidates, not automatic weld commands. Preserve UV0, material slots, pivot, hierarchy, scale and independent moving parts.

## Concrete accepted output per model

1. Original model ID, original source commit and BEFORE SHA256 from PASS05.
2. New genuine, native `.blend` saved **by Blender 4.x**, 8-byte `BLENDER-` header, exact file SHA256; verified source silhouette, hierarchy and topology BEFORE/AFTER.
3. New genuinely binary `.fbx` (`Kaydara FBX Binary` header) exported and reimported by Blender 4.x, SHA256, matching UV0/materials/parts/triangles and logs.
4. Actual source wireframe BEFORE/AFTER and shaded AFTER screenshots, plus topology metrics.
5. **Independent C01-02** retests exact after-FBX hash, statuses per Blender/FBX/geometry/Unity. C01-10 tests Unity 6 URP and prefabs; C01-00 authorizes release. No `APPROVED` until all gates.

**Status: NEEDS_OWNER_ACTION**; no native source repairs executed by C01-03, no unauthorized merge and no new model or ship geometry changes.
