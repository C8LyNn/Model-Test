# C01-16 | W26 GLOBAL MESH REPAIR — REAL ORIGINAL P16 NATIVE QA

Owner: C01-16 LIGHTING & SIGNALS; strictly P16-01..07 in existing open Draft PR #12 and #28. Claude-assigned doors/gates and frozen PR #19/#32 completely excluded. No model or ship geometry changes.

## Direct ORIGINAL physical binary execution
- Downloaded genuine previous Blender4 Actions [W01 run #41348140241 / artifact #13099778112](https://github.com/C8LyNn/Model-Test/actions/runs/41348140241) and [W02 run #41348144803 / artifact #13100396298](https://github.com/C8LyNn/Model-Test/actions/runs/41348144803). Both original ZIP CRC checks PASS.
- Physically extracted seven original BLEND-v400 + seven original Kaydara binary FBX7400; recomputed full-byte SHA256 **14/14 match** current exact native hashes and the signed PASS17 manifest. This is NOT Git-LFS-pointer-only verification.
- Ran new standalone native FBX7400 indexed binary parser with zlib arrays, Objects/Geometry, PolygonVertexIndex, LayerElementNormal, LayerElementUV/UVIndex, Model parent transformations and FBX Connections. Checked 116 real mesh objects, **2052 triangles, 1258 raw vertex records and 3078 within-mesh unique topology edges**.
- **0** degenerate triangles, 0 unclosed boundaries, 0 nonmanifold edges, 0 same-mesh duplicated face triangles, 0 winding conflicts, 0 inverted/perpendicular per-corner normals, 0 missing UV0/zero-area UV triangles, 0 nonfinite coordinates, 0 negative closed signed volumes, and **0 exact intra-mesh T-junction candidates**. The physical per-mesh static topology gate is **AUDITED / NO_PER_MESH_DEFECT_FOUND**.

## Cross-object strict triangle narrowphase: measured, NOT auto-labelled FAIL
Evaluated actual original imported 0-degree geometry using AABB broadphase, two-sided Moller–Trumbore strict segment-triangle narrowphase, and separate planar polygon overlap check. **1729 actual strict intersecting triangle pairs across 144 distinct component pairs**, while **0 positive-area coplanar triangle overlays** (no proven literal coplanar z-fighting at the tested pose):

| Model | Original mesh parts | Triangles | Cross-component crossing triangle pairs | Component pairs | Independent W26 intent gate |
|---|---:|---:|---:|---:|---|
| P16-01 | 12 | 220 | 156 | 13 | REVIEW |
| P16-02 | 12 | 220 | 178 | 15 | REVIEW |
| P16-03 | 12 | 220 | 114 | 9 | REVIEW |
| P16-04 | 27 | 452 | 478 | 41 | REVIEW |
| P16-05 | 19 | 344 | 336 | 28 | REVIEW |
| P16-06 | 23 | 388 | 301 | 25 | REVIEW; rotor↔static previously clear |
| P16-07 | 11 | 208 | 166 | 13 | REVIEW |

Initial native witnesses are between named emission diffuser/dark panel, nested steel frame, physically seated fasteners, cable glands, corner gussets and bolted internal mounts, including P16-06 rotor details moving together. They can be intentional mating penetrations, and **must NOT be globally welded/remeshed or declared defective from counts alone**. C01-02 shall separately judge visible surface clipping, material shading, disconnected mechanical supports, true exterior intersections, and assembly functionality by exact FBX SHA and native meshes. P16-06 native W26 static 0-degree rotor↔static crossings = 0; **previous** independent 360-degree rotor conservative radial clearance = 120/120 pairs separated, min 4.748 mm (producer true Blender [run #41531991576](https://github.com/C8LyNn/Model-Test/actions/runs/41531991576)).

[Seven-row exact SHA and per-model measurements CSV](W26_7_ORIGINAL_BINARY_MESH_AUDIT.csv).

## Actual genuine Blender4 follow-up
[W26 read-only Blender native/open + FBX reimport script](audit_original_native_blender_fbx.py) and [native Blender GitHub Actions run #41708247906](https://github.com/C8LyNn/Model-Test/actions/runs/41708247906): read original hydrated 14 SHA, open original BLEND, reimport exact genuine FBX, recheck topology/UV and world bounds, generate seven source-mesh edge wireframe SVG and machine JSON. The result is **PENDING until run finishes and evidence is checked**, not yet a Blender W26 PASS; original Blender4 signed W01/W02 source production evidence exists.

## W26 release trace
- All seven IDs: **AUDITED → NO_PER_MESH_STATIC_DEFECT_FOUND / CROSS_OBJECT_INTENT_REVIEW → no model modification pending independently confirmed defect → C01-02 W26 review pending (previous exact-SHA scoped STATIC_PASS retained) → UNITY_NOT_RUN / FINAL_HOLD**.
- Confirmed defect repairs will use the EXISTING original Blender source + FBX export/reimport + changed vertex/edge/triangle counts + true before/after wireframes, then independent C01-02 acceptance. No speculative optimization/normal reset/UV remodel/mesh decimation.
- Authorized Unity Editor 6000.3.14f1 integration owner is C01-10; no real Unity Editor, prefab, PlayMode or URP screenshot PASS claimed.
- Frozen Claude doors, D01/D02, gates, PR #19/#32 were neither inspected, modified, tested nor exported. NO MERGE.
