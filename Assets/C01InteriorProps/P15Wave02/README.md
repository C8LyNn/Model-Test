# C01-15 — WAVE 02 Technical Installations
Owner: C01-15. Scope: P15-04 / 05 / 06 / 07 only. Target: Unity 6000.3.14f1 URP.

## Produced meshes
| Asset | Description | Mount | Anchor |
| --- | --- | --- | --- |
| P15-04 | 3m straight ceiling cable tray with longitudinal cables, brackets, warning labels | ceiling | local root=(0,0,0), Y=0 mounting plane |
| P15-05 | 90-degree curved cable tray, cable strands, matching socket | ceiling | input center (0,0,0), outgoing center (.55,0,.55) |
| P15-06 | 1.5m technical wire bundle with 6 flexible cores and five retaining brackets | wall | Z=0 mounting plane, beginning of +X run |
| P15-07 | wall coolant distributor, 3 pipes, header, two manometers | wall | Z=0 mounting plane, bottom at Y=0 |

The P15-04 / P15-05 interface is the same U-profile at the same orientation. Incoming tray cross-section Y=[-.18,-.05], width ±0.19m. Elbow centerline x=0.55sin(t), z=.55(1−cos(t)), t=0..π/2. Its outgoing section is perpendicular at x=.55, z=.55; no arbitrary scaling or unapproved architectural changes.

## Generated files
- Four actual native .blend Blender sources under Sources/Blender (CI-generated).
- Four binary FBX under Models/FBX, each with UV0, normals and 4 URP-oriented material roles.
- Twelve Blender viewport renders (three directions × four IDs), PNG.
- Four manifest JSON files with bounds, native triangle counts, mounting interface and QA state.
- Tools/C01Props15Wave02/blender_build.py for deterministic rebuilding.
- QA/blender_roundtrip.json and QA/file_integrity.json with actual Blender FBX re-import checks and hashes.

Unity prefabs: Generated only after importing actual FBX in Unity 6 by invoking Tools > C01 Props15 > WAVE02 Build & Audit (or CLI -batchmode -executeMethod C01Props15Wave02PrefabBuilder.Build). Creates prefab per model with colliders, URP/Lit materials, measured import bounds and QA/unity_editor_import.json. This action was NOT RUN by author because Unity is unavailable in author environment. Generated C# source is not equivalent to a tested .prefab.

## Placement safety
No ship hull/room/corridor/door/elevator/stair/structural scene files are modified. Neither C01-10 showcase nor gameplay scene is part of this PR. C01-10 must position cable tray in free ceiling space and the wall manifold outside traversal/door sweep. For fittings mounted near ceiling use Y=0 at underside of mounting slab; align with measured ship structure, not guessed deck heights.

Review gate: C01-02 independently validates each exact SHA; C01-10 checks Unity 6 URP prefab clearance and makes test-room instances. Do not merge before review. Wave 01 lives in independent PR #16; there is no geometry or dependency coupling between branches.
