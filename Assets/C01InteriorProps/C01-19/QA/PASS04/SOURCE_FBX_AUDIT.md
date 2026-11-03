# C01-19 PASS04 — actual binary FBX static audit before triangulation
Scope: existing draft PR #15; source native Blender/FBX as produced by PASS03, not a proxy model.
Performed a **local full binary FBX 7400 decode** of real files from verified PASS03 GitHub Actions artifact, including raw `Geometry.Vertices` and `PolygonVertexIndex` streams. This is NOT Blender execution and is not a completed PASS04 native repair.
Source code for Blender-side source edit and FBX roundtrip: `Source/pass04_triangulate.py` in this PR; GitHub Actions workflow: `.github/workflows/c01-19-pass04.yml`.

| ID | FBX verts | FBX faces | Nominal triangles | N-gons >4 | Largest face | Degenerate naive-fan triangles | Original FBX SHA256 |
|---|---:|---:|---:|---:|---:|---:|---|
| P19-01 | 133 | 78 | 254 | 38 | 10 | 12 | `47b4d6f2017626b6084584fbf0bad907505eb9e194703032d83af5315c1a4009` |
| P19-02 | 118 | 86 | 216 | 31 | 8 | 10 | `a42a57d168164cea335de3c9ee175a3074edca4a48b707a14beadbea16a8b6d8` |
| P19-03 | 72 | 48 | 128 | 10 | 10 | 0 | `872688775a1f373090867a466b21be441d8962b16b2a47703cc50c12220f1891` |
| P19-04 | 72 | 54 | 108 | 0 | 4 | 0 | `529c1886bf8d727699db72578f01da9f6226981e02738a1b9fcd24ade489bc9` |

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
