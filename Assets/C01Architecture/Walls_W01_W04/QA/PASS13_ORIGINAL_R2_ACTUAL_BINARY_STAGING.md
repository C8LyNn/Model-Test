# C01-11 — Detail Pass 13: actual original-r2 binary FBX staging

**Owner:** C01-11 W01–W04 historic ship architecture, **not included** in the P15–P19 36-model Detail Pass 13 cohort. No architecture/model geometry was changed. Existing [Draft PR #22](https://github.com/C8LyNn/Model-Test/pull/22), no merge.

## Physical delivery (actual file bytes, not a proposed script)

`C01-11_PASS13_ORIGINAL_R2_UNITY_STAGING.zip` — **537,705 bytes**, **26 regular files**, archive SHA-256:

`193d4fb5cbc5b7a2db8f7149659c500cccd8ec95d21e9c01dd3c9b59faecf2ae`

Persisted in the user's ChatGPT Project Library at:

`/C01 — 3D Asset Factory/C01-11/PASS13/C01-11_PASS13_ORIGINAL_R2_UNITY_STAGING.zip`

The actual four untouched historic r2 **Kaydara binary FBX 7400** files now occur in the ZIP at precisely the destination paths expected by the existing PR22 `C01WallPrefabBuilder.cs` full-source mode:

| Unity stage path relative to archive root | Exact original FBX SHA-256 | V/E/F/T |
| --- | --- | --- |
| `Assets/C01Architecture/Walls_W01_W04/OriginalR2/FBX/W01_FULL_WALL_1M.fbx` | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 8/18/12/12 |
| `Assets/C01Architecture/Walls_W01_W04/OriginalR2/FBX/W02_TECH_PANEL_WALL_1M.fbx` | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | 288/858/572/572 |
| `Assets/C01Architecture/Walls_W01_W04/OriginalR2/FBX/W03_CORNER_90_1M.fbx` | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 12/30/20/20 |
| `Assets/C01Architecture/Walls_W01_W04/OriginalR2/FBX/W04_DOOR_OPENING_2M.fbx` | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 16/42/28/28 |

**Actual execution:** Recreated a disposable source-audit worktree from the archived authentic FBX and original `mesh_data.json`; ran the existing indexed binary-FBX topology test on all four exact source files. **4/4 PASS_UNCHANGED**, zero confirmed unwanted defects; UV0 and normal streams complete in each. No original byte changed; the archive SHA manifest was validated for 100% of files and ZIP CRC test PASSED.

The package also contains three **historical genuine native Blender v400** `.blend` + corresponding Blender-exported binary FBX pairs (W01, W03, W04) in `QA/HISTORICAL_PROVENANCE_ONLY/`; do **not** import these evidence-only files as the authoritative r2 variants, or transfer their older SHA-pinned native QA receipt to the PR22 Git LFS pointer versions. An actual W02 original detailed authored `.blend` is still unavailable. The supplied W02 FBX is 572 tris (correct) versus the existing PR22 **wrong substitute** W02 candidate 12 tris.

The package includes a true existing source W02 wireframe preview `QA/ACTUAL_W02_ORIGINAL_WIREFRAME.png`; no fabricated AFTER screenshot is provided because **no mesh modification** was made.

## Exact handoff and gates

This package is an **offline physical original-FBX archive**; binary files are **not committed to GitHub** and must be staged from the ZIP by the owner/Unity importer into a disposable worktree. No live ship scene or existing file is replaced.

- Existing PR22 Unity menu `Tools/C01/C01-11/Build W01-W04 Original R2 Prefabs` requires exactly these staged files; the QA-only candidate menu remains separate.
- Execute real Unity 6 URP Editor import on a disposable project, check UV/materials/normals/colliders, produce genuine prefab and inspector logs and obtain independent C01-02 verdict.
- Exact current C01 Actions job [41123424808](https://github.com/C8LyNn/Model-Test/actions/runs/41123424808) completed without any reported steps/runner; root cause not established. No local Blender/Unity executable, so no native `.blend` regeneration, no Blender FBX roundtrip this pass, no real Unity import.
- New repaired geometry `0`; four **existing unchanged original FBX** staged; indexed source topology `4/4 PASS`; Blender **NOT RUN**, Unity **NOT RUN**, independent C01-02 **PENDING**.
- **Owner-action required:** manually unzip in the authorized test project and run Unity 6, or restore GitHub runner allocation. No spending, repo settings, ship or PR merges changed.

**Boundary:** P18/P17 mechanical detail fixes in #36 remain owned by C01-18/C01-17. These four architectural FBX do not count toward the P15–P19 36-model QA tally.
