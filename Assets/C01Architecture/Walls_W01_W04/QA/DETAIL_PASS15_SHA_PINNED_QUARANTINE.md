# C01-11 — DETAIL PASS 15: physical SHA source lock and prefab quarantine

## Scope
C01-11 owns W01–W04 historical architectural components. These are **outside** the 36 P15–P19 prop models in [Issue #36](https://github.com/C8LyNn/Model-Test/issues/36); the issue prohibits new ship geometry. This pass has **zero new 3D meshes and zero new geometry modifications**, no unrelated producer files or merge. Existing Draft [PR #22](https://github.com/C8LyNn/Model-Test/pull/22) only.

## Real code modification — committed, NOT merely a plan
At [`e5763c31dc27941fb173fd52266655142a915699`](https://github.com/C8LyNn/Model-Test/commit/e5763c31dc27941fb173fd52266655142a915699), modified existing file `Assets/C01Architecture/Walls_W01_W04/Editor/C01WallPrefabBuilder.cs`:
1. Before any Unity asset write, computes cryptographic SHA-256 of the **actual physical FBX** opened from the source filepath and compares it to an exact pinned original-r2 SHA or exact existing PR22 LFS candidate SHA. If LFS points are unhydrated, stale/replaced or mutated, build fails closed; triangle counts alone no longer suffice.
2. Preflights source material-slot completeness on all selected FBXs before any prefab writes. Retains original root transform/pivot, mesh materials, model geometry and UV0.
3. Both menus save prefabs into `QA_Candidates/OriginalR2/Prefabs` or `QA_Candidates/LegacyNative/Prefabs`; ALL generated file names include `_QA_ONLY`. No direct writes to the production `Prefabs` folder or active spacecraft scenes. Refuses overwrite of an existing QA prefab path.
4. Original W02 source path and 572-triangle gate remain separate. The 12-triangle replacement candidate is never eligible.
5. Saved-prefab return checked for failure. Preview-scene isolation remains in place.

### Actual byte SHA-256 — four authoritative unchanged source FBX
| ID | Original r2 binary FBX SHA-256 | Source triangles |
|---|---|---:|
| W01 | `7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10` | 12 |
| W02 **detailed original** | `3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037` | **572** |
| W03 | `3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2` | 20 |
| W04 | `c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe` | 28 |

### Existing Blender-4 genuine source candidates in PR22 historical artifact
| ID | PR22 matched Blender-v400 `.blend` SHA-256 | PR22 matched native binary `.fbx` SHA-256 |
|---|---|---|
| W01 | `80a8999cc0a039eb4f5f907c38c492ec4c4ed49c22a66d44f36fbe14cb1356b2` | `4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f` |
| W03 | `77e1a52db293d4fc6b27b27e151c89865eb4473465bfeafefcc85935b810f9cc` | `4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c` |
| W04 | `4e533365634ffc5207734bbd258c7f7d267348813dacc8bdf6943354d8367f53` | `b8751c3816ac6745b99ca17cf0489187dda6f1fd3e5fe4f209030aaccef0ddc8` |

These files were actually generated historically by Blender in [Actions #41072466328](https://github.com/C8LyNn/Model-Test/actions/runs/41072466328), NOT in PASS15. The current PR22 LFS source pointers for the 3 native FBX files were independently fetched and matched to the historical archive's FULL BYTES; byte-level provenance verified. No claim that historical Blender QA for different byte hashes transfers to these current pins. Detailed W02 authored `.blend` is still missing; simplified W02 native source is rejected.

## Actual executed OFFLINE binary test outcome
Reopened real archived files `/mnt/data/C01-11_PASS13_ORIGINAL_R2_UNITY_STAGING.zip` and `/mnt/data/C01-11_W01-W04_native_sources_41072466328.zip`: **four** original hydrated binary FBX SHA/header checks PASS, **three** real current PR22 candidate FBX SHA/header checks PASS, **three** existing Blender native `.blend` signature/SHA checks PASS. All 10 hashes pinned. Additional **14/14 negative** tests PASS: ten one-byte mutations independently rejected, three unhydrated Git LFS text-pointers rejected, plus actual W02 candidate polygon triangulation **12 tris** versus original detailed **572 tris**. The FBX polygon count was triangulated correctly (6 original quad polygons in the erroneous candidate produce 12 triangles); direct raw polygon-count would incorrectly yield 6. Tested data, not Unity C# runtime.

**Source code** was fetched again after commit; **15/15 structural guards PASS** (hash computation, seven pins, preflight order, no W02 candidate, all outputs quarantine, no overwrite, materials, pivot, preview scene, exact one-file commit and Draft). This static code check is NOT C# compilation.

**Physical evidence ZIP** `C01-11_PASS15_EXISTING_NATIVE_AND_SHA_GATES.zip`: 347,084 bytes, **13 files**, archive SHA-256 `edff835efb3f628feb2384d08d2f9cd52c16095826f06394a9a41774951a1548`, verified ZIP CRC and internal manifest SHA entries. Holds physical four original FBXs plus three actual already-existing `.blend`+native FBX pairs in **QA_ONLY** folders, generated negative-test JSON, and README. No unauthorized file replacements. Packaged source assets are all **unchanged**.

## Quality gates
| Gate | PASS15 result |
|---|---|
| Corrected original 3D meshes or new detail geometry | **0**, not authorized for architecture / none confirmed broken |
| Existing physical FBX / native blend SHA validation | **10/10 PASS** |
| Negative mutation / Git LFS / W02 tests | **14/14 PASS** |
| Static import-tool guard checks | **15/15 PASS** |
| NEW Blender 4.x `.blend` save→FBX export→reimport | **NOT RUN**; Blender/bpy unavailable |
| Independent C01-02 final QA | **PENDING** |
| Real Unity 6 URP import and prefab compilation | **NOT RUN** |
| Release/merge | **NOT AUTHORIZED**, PR22 remains Draft |

Latest relevant GitHub Actions private-repo jobs remain `failure` before a runner/step was assigned; environment root cause unconfirmed, no billing/permission changes. **NEEDS_OWNER_ACTION** to restore runner or use authorized Windows Blender4/Unity6 setup for native QA. This branch does not claim progress towards the 36 prop releases; P18/P17 detail geometry remains owned by their respective producers.