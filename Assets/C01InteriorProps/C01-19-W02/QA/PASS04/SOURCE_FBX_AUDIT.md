# C01-19 PASS04 — actual binary FBX static audit before triangulation
Scope: existing draft PR #29; source native Blender/FBX as produced by PASS03, not a proxy model.
Performed a **local full binary FBX 7400 decode** of real files from verified PASS03 GitHub Actions artifact, including raw `Geometry.Vertices` and `PolygonVertexIndex` streams. This is NOT Blender execution and is not a completed PASS04 native repair.
Source code for Blender-side source edit and FBX roundtrip: `Source/pass04_triangulate.py` in this PR; GitHub Actions workflow: `.github/workflows/c01-19-pass04.yml`.

| ID | FBX verts | FBX faces | Nominal triangles | N-gons >4 | Largest face | Degenerate naive-fan triangles | Original FBX SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| P19-05 | 88 | 66 | 148 | 3 | 16 | 1 | `64156363cb5007831c243aeea50d5e59c862cc98b27cb12dd2f8af5b3c019892` |
| P19-06 | 56 | 42 | 84 | 0 | 4 | 0 | `d773f2d3c0fe9743a0ad619353766b669386997769eb8a59487b58295c7c3a7d` |
| P19-07 | 136 | 78 | 252 | 16 | 20 | 19 | `88b32fe2f5ddf981eecdc0469088f4e23e07c4c605a1db7bb9689a0b6011d585` |
| P19-08 | 149 | 100 | 282 | 35 | 12 | 7 | `cbbea5435f8326e06fb5f43237986594df044c0e3ff94100fc44f856dce35ae2` |

### Status and interpretation
- Measured counters reflect REAL original PASS03 binary FBX geometry; no substitute model was created. Fan-degenerate count is a **warning for unspecified triangulation**, not proof of actual Blender/Unity rendering failure.
- This branch includes an executable, per-part BMesh `EAR_CLIP` triangulation on actual stored native `.blend` files, with original mesh hierarchy/UV/material preservation and comparison gates (UV0, bounded AABB, signed volumes, triangle count, no degenerate faces, FBX importer check) and genuine source wireframe/shaded evidence.
- Never perform global weld, material cross-join, or animation hinge join.
- **Execution blocker:** GitHub Actions jobs fail before allocating a runner, with `steps=[]`, `duration_ms=0`, and no Blender log, including other project jobs. Local container lacks Blender and cannot fetch package dependencies. Hence NO newly repaired native `.blend`/FBX PASS04 outputs yet.
- Prior PASS03 native Blender/FBX roundtrip remains PASS on prior binaries; it does not cure these identified n-gon/fan risks.
- C01-02 must independently inspect final native outputs and T-junction candidates, including P19-07 (8) and P19-08 (2), **after** successful actual Blender execution. Unity 6 URP NOT RUN; no independent C01-02 PASS04 acceptance.
- Keep PR DRAFT and do not merge or touch any ship scene.

### Next executable task
Restore runner availability, execute `.github/workflows/c01-19-pass04.yml` on current existing branch; inspect `QA/PASS04/SUMMARY.json`, actual `.blend/.fbx` and before/after captures, then return exact resulting SHA to independent C01-02.
