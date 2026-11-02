# C01-17 PASS03 — Real Blender topology repair: producer evidence

Related issue: https://github.com/C8LyNn/Model-Test/issues/30. Existing source models only; no redesign/no ship layout changes/no new models.

| ID | Vertices before -> after | Boundary/nonmanifold before -> after | Triangles preserved |
|---|---:|---:|---:|
| P17-01 | 408 -> 136 | 408 -> 0 | 204 |
| P17-02 | 480 -> 160 | 480 -> 0 | 240 |
| P17-03 | 456 -> 128 | 456 -> 0 | 208 |
| P17-04 | 696 -> 232 | 696 -> 0 | 348 |
| P17-05 | 480 -> 160 | 480 -> 0 | 240 |
| P17-06 | 312 -> 104 | 312 -> 0 | 156 |
| P17-07 | 456 -> 152 | 456 -> 0 | 228 |

Total: 3288 -> 1072 vertices, 4080 -> 2436 edges, 1624 triangles unchanged, 3288 -> 0 boundary/nonmanifold edges. 832 -> 130 connected components (each separate mesh object retained).
Exact repair: per-mesh conservative bmesh remove doubles (1e-6 meters), UV loop data and hard component boundaries preserved.
P17-03: local retriangulation of two malformed cylinder endcaps, preserving 10 triangles per cap and unchanged silhouette.

REAL Blender 4.0.2: source .blend opened; actual source Blender BMesh audited; .blend resaved, binary .fbx exported, Blender FBX reimport verified (dimensions, UV0, child pivots).
W01 successful CI: https://github.com/C8LyNn/Model-Test/actions/runs/41089779966
W02 successful CI: https://github.com/C8LyNn/Model-Test/actions/runs/41088800979
Detailed mesh_topology_before.json / mesh_topology_after.json / REPAIR_EVIDENCE.json records and 4 real Blender frames per model at QA/PASS03; binary SHA256 at QA/BLENDER_FBX_ROUNDTRIP.json.

LIMITATIONS: T-junction search, BVH self-intersection narrowphase and cross-object coincident face overlap checks NOT RUN. Unity 6 URP prefab/material/collider/door clearance NOT RUN. Independent C01-02 technical gate PENDING. No merge until QA approval.

Wave 01 draft PR #17: https://github.com/C8LyNn/Model-Test/pull/17
Wave 02 draft PR #23: https://github.com/C8LyNn/Model-Test/pull/23
