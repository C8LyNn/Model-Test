# C01-10 — PASS 04 | Real Binary FBX → Unity 6 URP (QA quarantine)

**Issues:** #33, #30, #9, #8. **Status:** SOURCE IMPORT TOOLING ONLY / UNITY NOT RUN / QA PENDING.

## Real delivered files

- `source_stage_36.json`: 36 source-ID paths from 10 existing producer branches, each pinned to a specific Git commit. These commit SHAs are NOT independently approved FBX SHA-256 hashes.
- `stage_real_fbx.py`: checks out detached producer commits via Git worktrees, hydrates LFS binaries using `git lfs pull`, rejects ASCII FBX and LFS pointer text, copies verified raw binary FBX with SHA receipts into a disposable QA staging folder.
- `Assets/C01InteriorProps/Editor/Pass04SourceImportAudit.cs`: Unity 6 Editor source importer measuring actual imported MeshFilter geometry, submeshes/triangles, UV0, normals, degenerate triangles, material slots, URP shader warnings, root scale and source collider presence. It writes one CSV record for every one of 36 IDs.
- Native QA-only prefabs with nested original FBX instances and static nonconvex test MeshColliders, and one source-inspection scene, are generated ONLY BY AN ACTUAL UNITY RUN and are not included as fabricated project files in this PR.

## Step 1 — source staging (Windows with Python 3, Git and Git LFS)

From local Unity repository root at this PR branch:

```powershell
py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo .
# This is a dry-run; no model downloaded.
py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo . --apply --ids P19-05 P19-07 P19-08
# Stage the three priority originals/current repairs first.
py -3 C01InteriorProps/Pass04/stage_real_fbx.py --repo . --apply
# Stage all 36 if every final source path/commit is still valid.
```

IMPORTANT: producer branches evolve. Refresh `source_stage_36.json` source_commit for any new producer PR revision, especially P19-05/07/08 after explicit triangulation. The script uses exact source commits, NOT an arbitrary branch HEAD, and never updates producer branches. A successful staging byte check is NOT a topology or Blender QA PASS.

Resulting local input: `Assets/C01InteriorProps/Pass04Incoming/Pxx-yy/Pxx-yy.fbx`. Receipt CSV: `C01InteriorProps_QA/PASS04/staged_sources.csv`. Copies/QA artifacts are gitignored pending review.

## Step 2 — actual Unity Editor, 6000.3.14f1 URP 17.3.0

1. Open the actual Unity project in this isolated branch and let FBX import finish.
2. Menu `C01 > Mesh Repair PASS04 > 00 — Enable Readable on Staged Copies`. This explicitly modifies only staged FBX import settings, not binary source meshes or producer branches.
3. Menu `C01 > Mesh Repair PASS04 > 01 — Audit 36 Source FBX`. Actual results: `C01InteriorProps_QA/PASS04/36_FBX_UNITY_IMPORT_AUDIT.csv` (36 records). Missing, ASCII or LFS pointer files remain BLOCKED/FAIL.
4. Menu `C01 > Mesh Repair PASS04 > 02 — Build Quarantine Prefabs and Scene`. Only true source precheck-pass models become native `Assets/C01InteriorProps/Pass04Quarantine/Prefabs/Pxx-yy_QA_ONLY.prefab` and the isolated `Scenes/C01_PASS04_FBX_Source_Inspection.unity`. With no valid imported models it throws, creating NO placeholder mesh.
5. Save REAL Unity Scene View Shaded/Wireframe captures and Console logs; manually inspect pivot, normals/hard edges, URP materials, articulated parts, and collider behavior.
6. Test physical clearance against real ship geometry in a separate test copy (nominal 3 m passages, doors, stairs, elevators and player capsule). The quarantine scene alone does NOT prove physical clearance.
7. Ask C01-02 to approve exact repaired FBX SHA and final Unity evidence. Only then use the existing accepted-only showcase builder and its approval ledger.

### Headless command (must point to an actual Unity executable)

```powershell
$UNITY = 'C:/Program Files/Unity/Hub/Editor/6000.3.14f1/Editor/Unity.exe'
& $UNITY -batchmode -nographics -projectPath (Get-Location).Path `
  -executeMethod C01.InteriorProps.Editor.Pass04SourceImportAudit.RunBatch `
  -logFile 'C01_PASS04_UNITY.log' -quit
```

## Scope and exact claim boundaries

- Source precheck reads the real imported FBX and can detect degenerates/UV/normal omissions when Mesh.isReadable. It does NOT prove weld connectivity, importer-independent concave n-gon triangulation, cross-part self-intersections, or full topology correctness.
- P19-05/07/08: C01-02 PASS03 reported importer-dependent n-gon triangulation P1 FAIL; C01-19 must repair on its existing PR #29 and request SHA-pinned independent retest. Do not self-approve based on local preview.
- Unity source importer, native prefab generation, rendering, physics and PlayMode **NOT RUN in this chat runtime** (no Unity/Blender executables); no generated Unity prefabs/scenes claimed.
- No ship geometry, layout, architecture or producer mesh changes. No merge, no new models, no Wave03.
