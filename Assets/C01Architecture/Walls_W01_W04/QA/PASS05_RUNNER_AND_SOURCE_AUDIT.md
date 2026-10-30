# C01-11 PASS05 — Runner allocation + immutable source mesh provenance

## 1. Real runner allocation diagnostic — executed

GitHub Actions [run 41098792689](https://github.com/C8LyNn/Model-Test/actions/runs/41098792689), HEAD `702695410f965cfa8b070c4ce917b4ff5ce7cd0f`, workflow `.github/workflows/c01-11-pass05-runner.yml`:

- Job `ubuntu-22`, ID `124211391437`: **FAIL**, no runner allocated, steps empty/null; no shell ran.
- Job `ubuntu-24`, ID `124211391792`: **FAIL**, no runner allocated, steps empty/null; no shell ran.

Both jobs use one `echo`/Python-version diagnostic only, no source checkout/Blender/FBX processing. Thus the **GitHub Actions failure occurs prior to executing our scripts**. This does not establish a precise root cause (GitHub account/billing/runner provisioning all require separate owner-side inspection). Do not call this a failed Blender geometry test.

GitHub Actions public health page currently reports Operational, but repo-local runner allocation has failed on multiple workflow families in #33. **Blender 4.x and Unity 6 are not installed in C01-11's current local executor**. Actual new PASS05 Blender source recovery and import: **NOT RUN**.

## 2. Actual original r2 geometry static rerun — executed locally

Original source: **byte-identical original historical October 28 binary FBX**, not regenerated PR22 candidate.

| ID | Original filename | SHA-256 | Vertices / Edges / Faces / Triangles | Source topology defects |
|---|---|---|---|---:|
| W01 | `W01_FULL_WALL_1M.fbx` | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 8 / 18 / 12 / 12 | 0 |
| W02 | `W02_TECH_PANEL_WALL_1M.fbx` | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | 288 / 858 / 572 / 572 | 0 |
| W03 | `W03_CORNER_90_1M.fbx` | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 12 / 30 / 20 / 20 | 0 |
| W04 | `W04_DOOR_OPENING_2M.fbx` | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 16 / 42 / 28 / 28 | 0 |

Source topology static checks: original indexed mesh coordinates and connectivity, loose/duplicate verts, non-manifold/boundaries, area, winding, T-junction candidates, UV0 and face normals, coplanar intersections: **4/4 PASS UNCHANGED**, 0 repairs; before = after, SHA unchanged. These results **do not** substitute for Blender native import or C01-02 acceptance. In particular they do **not** count toward the 36 P15–P19 props in #33.

## 3. Concrete PASS05 safety fix

Updated `Editor/C01WallPrefabBuilder.cs`: **all four source names now point to `OriginalR2/FBX/`**, and the exact triangle preflight executes **before any .mat/.prefab writes**. The previous PR22 W02 prototype (12 triangles, renamed `W02_PANEL_WALL_1M.fbx`) must never silently replace the authentic W02 r2 (572 triangles, `W02_TECH_PANEL_WALL_1M.fbx`). If original FBXs are not staged in the Unity project, importer fails CLOSED. The original historical binary inputs are available in the C01-11 PASS05 handoff archive, not yet committed as binaries in this PR.

## 4. Actual Blender recovery procedure (not executed)

Use the `C01-11_PASS05_original_r2_and_native_recovery.zip` handoff from the current C01-11 chat, including the real original FBX, saved source mesh and `Sources/recover_native_blend_from_original_fbx.py`. On a Windows workstation with Blender 4.x run `RUN_REAL_BLENDER_WINDOWS.ps1`. Script checks original SHA, imports actual FBX to Blender, saves `*_RECOVERED_FROM_ORIGINAL_R2_FBX.blend` (NOT the historical authored .blend), binary FBX exports and reimports, compares triangle world positions/UV/materials/pivot and emits source/output SHA-256. This procedure is ready **but NOT RUN** in this environment.

## 5. Remaining gate

- Original native historical .blend unavailable; recovered .blend = NOT RUN until actual Blender.
- Real Unity 6 URP prefab import, W04-D01 door fit = NOT RUN.
- Independent C01-02 = PENDING, C01-10 integration = BLOCKED.
- Draft PR #22, no merge, no ship changes.
