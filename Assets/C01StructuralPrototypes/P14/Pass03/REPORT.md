# C01-14 / PASS 03 — TRUE SOURCE MESH INTEGRITY (2026-10-30)

**Scope:** own two *unapproved*, optional structural prototypes RMP-01 + RAI-01. Not counted among 36 P15–P19 interior props. No ship architecture, pathways, doors, deck geometry, or any other owners' source models changed.

**Existing draft PR:** #24. **Verified Blender 4.0.2 CI run:** https://github.com/C8LyNn/Model-Test/actions/runs/41089475908 (SUCCESS; Blender source verification, before/after topology, native FBX export, FBX reimport, preview screenshots, SHA, LFS push). Original v001 comes from immutable native source artifact run 41072902015 and original manifest hashes were checked.

## Measured original-source results
| Model | V | E | Faces | Tris | Mesh parts | Detected defects BEFORE→AFTER | Source modification | Blender FBX roundtrip |
|---|---:|---:|---:|---:|---:|---|---|---|
| RMP-01 | 48→48 | 108→108 | 72→72 | 72→72 | 6 | 0→0 | NONE — clean original topology | PASS, 60 visual tris 60 imported |
| RAI-01 | 32→32 | 72→72 | 48→48 | 48→48 | 4 | 0→0 | NONE — clean original topology | PASS, 48 visual tris 48 imported |

Counts are **per native Blender source**, summed over original separate parts. The RMP-01 72 tris include 12 triangles on a dedicated invisible collider proxy that shares the deck shape with the visible deck; the rendered FBX has 60 visible triangles. This is intentional, not duplicate faces within a single mesh. RAI rail/posts are intentionally separate editable solids that contact/overlap at assembly joints.

Every closed mesh part has 0 unexpected boundary edges, 0 nonmanifold edges, 0 loose vertices/edges, 0 duplicate faces, 0 degenerates, 0 coincident source vertices, 0 detected T-junction candidates, positive signed volume and UV0. Source-based wire BEFORE == AFTER images because the measured source had no topology defects requiring repair. **Do not pretend that 0→0 is a repair.**

Source GLB expanded shared positions at UV/hard-edge GPU vertex splits; that is distinct from native source Blender topological vertices. No automatic Merge by Distance applied.

## Actual files committed to this PR
- `Assets/C01StructuralPrototypes/P14/Pass03/Sources/C01_14_RMP-01_v002.blend` SHA256 `7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa`
- `Assets/C01StructuralPrototypes/P14/Pass03/Sources/C01_14_RAI-01_v002.blend` SHA256 `8a2f16205874f8485adb87c5251f6adbba3f51816936c0bf1964ad40a47850a5`
- `Assets/C01StructuralPrototypes/P14/Pass03/FBX/C01_14_RMP-01_v002.fbx` SHA256 `97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443`
- `Assets/C01StructuralPrototypes/P14/Pass03/FBX/C01_14_RAI-01_v002.fbx` SHA256 `b51c3c012f5680de2d02c2deaf5c67c4ae9a12bb7e8347f179ed08d181a7e103`
- `Pass03/QA/{RMP-01,RAI-01}/mesh_topology_before.json`, `mesh_topology_after.json`, `fbx_roundtrip.json`
- `Pass03/Previews/{RMP-01,RAI-01}/` four real mesh views each: wireframe_before, wireframe_after, shaded_after, joint_inspection_after.
- `Tools/C01Structures14/mesh_integrity_pass03.py` source-aware non-destructive Blender auditor, conditional repairs, FBX roundtrip.
- CI artifact `C01-14-PASS03-native-before-after` in run 41089475908.

## Test boundaries / gate
- **PASS** native Blender input SHA, topological invariants listed above, FBX binary export, re-imported triangulated visual surface positions at 1e-4 precision and UV0, screenshot generation, CI artifact and PR binary evidence.
- **NOT RUN** exhaustive cross-object self-intersection/coplanar-overlap solver. Component assembly contacts and a collider proxy are intentional and documented, not proof of no overlap.
- **NOT RUN** actual Unity 6 URP import, prefabs, collision/play mode and door/route clearance (not available in this job).
- **BLOCKED** independent C01-02 QA and C01-00 structural interface acceptance. Do not merge, do not count toward 36 P15–P19 models.

**Next step:** C01-02 independently validate committed .blend and .fbx, evaluate intentional exceptions; C01-10 only if approved, perform Unity import/prefab and 25% ramp collision / headroom clearance.
