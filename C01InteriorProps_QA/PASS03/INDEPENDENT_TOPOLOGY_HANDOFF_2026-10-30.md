# C01-02 — Independent Technical Mesh Integrity QA / PASS 03

**Date:** 2026-10-30 · **Parent:** #30 · **QA PR:** #13 · **Independent QA status:** 0 FULL PASS / 3 FAIL (export-triangulation risk) / 33 BLOCKED.  
**Asset scope:** 36 P15–P19 IDs. **Real binary FBX audited:** 12 Wave02 models (6 P0 first + 6 extra files downloaded from the same producer archives). **Others:** NOT RUN on the newest originals.

## Provenance — real binary FBX, not the viewer's reconstructed geometry

Original BEFORE artifacts obtained from producer GitHub Actions:
- C01-17 W02 run [41073534111](https://github.com/C8LyNn/Model-Test/actions/runs/41073534111)
- C01-18 W02 run [41073033354](https://github.com/C8LyNn/Model-Test/actions/runs/41073033354)
- C01-19 W02 run [41073111779](https://github.com/C8LyNn/Model-Test/actions/runs/41073111779)

AFTER artifacts obtained from **successful** PASS03 producer workflow runs:
- C01-17 run [41088800979](https://github.com/C8LyNn/Model-Test/actions/runs/41088800979)
- C01-18 run [41088293330](https://github.com/C8LyNn/Model-Test/actions/runs/41088293330)
- C01-19 run [41088782744](https://github.com/C8LyNn/Model-Test/actions/runs/41088782744)

All 6 original Actions ZIP files pass independent ZIP CRC. Their FBX bytes were inspected directly with an independent binary FBX 7.x parser, additional indexed mesh checks with trimesh, normal/UV layer checks, and exact original-to-repaired geometric triangle-coordinate comparison. **No Blender or Unity executable in QA environment**. Producer-reported Blender FBX roundtrip is NOT independent QA Blender execution. The findings are bound to the exact binary SHA256 in this report, **not a moving PR branch head**.

## P0 priority-six independent BEFORE/AFTER

| ID | V before → after | E before → after | F before → after | Tri before → after | Components before → after | Boundary before → after | Binary FBX static gate |
|---|---:|---:|---:|---:|---:|---:|---|
| P17-04 | 696 → 232 | 870 → 522 | 348 → 348 | 348 → 348 | 174 → 29 | 696 → 0 | PASS indexed topology; full QA BLOCKED |
| P17-05 | 480 → 160 | 600 → 360 | 240 → 240 | 240 → 240 | 120 → 20 | 480 → 0 | PASS indexed topology; full QA BLOCKED |
| P18-04 | 192 → 192 | 288 → 288 | 114 → 114 | 348 → 348 | 9 → 9 | 0 → 0 | PASS indexed topology; full QA BLOCKED |
| P18-05 | 80 → 80 | 120 → 120 | 60 → 60 | 120 → 120 | 10 → 10 | 0 → 0 | PASS indexed topology; full QA BLOCKED |
| P19-07 | 104 → 136 | 156 → 204 | 78 → 78 | 156 → 252 | 13 → 6 | 0 → 0 | **FAIL P1: ambiguous concave n-gon triangulation** |
| P19-08 | 96 → 149 | 144 → 241 | 72 → 100 | 144 → 282 | 12 → 6 | 0 → 0 | **FAIL P1: ambiguous concave n-gon triangulation** |

**C01-17 source repair is independently verified at the FBX indexing level:** former six disconnected surface-islands per mesh are now a single connected solid per intended part. All 4 C01-17 Wave02 assets have zero indexed boundary/nonmanifold edges after repair. After P17-04/05/06/07, full before/after geometric triangle-coordinate *multisets are exactly equal*, not merely equal bounds.

**C01-18:** P18-04/05/06/07 already had one closed connected component per distinct moving/static mesh before the repair; all retain identical geometric triangle-coordinate sets after. Forced welding or merging the separate parts is not justified.

**C01-19:** AFTER Boolean union yielded more/complex polygons. Indexed FBX polygons can still have zero boundary edges, but safe triangulation is not established. **Never classify this as an observed Unity failure; Unity importer NOT RUN.**

## New P1 defect — exporter-dependent fan triangulation

An independent conservative fan triangulation test found:

| ID | AFTER polygons with >4 vertices | Maximum vertices per polygon | Degenerate fan triangles | Fan non-manifold edges | Result |
|---|---:|---:|---:|---:|---|
| P18-04 | 10 | 16 | 0 | 0 | PASS (regular cylinder caps) |
| P19-05 | 3 | 16 | 1 | 1 | **FAIL P1** |
| P19-07 | 16 | 20 | 19 | 2 | **FAIL P1** |
| P19-08 | 35 | 12 | 7 | 3 | **FAIL P1** |

For P19-07 one polygon's first triangle normal is also opposite the stored normal when checked with the fan method; it may be due to concavity. This does **not** prove Blender/Unity use that triangulation. It proves the export is **not safely triangulation-independent**. Please triangulate the actual Boolean-generated n-gons inside Blender with controlled winding before FBX export, preserve UV/material loops, and show Blender/Unity rendered tests. Do not add visual detail/redesign. Confirm whether source-space self-intersections or interpart overlaps remain; these require BVH narrowphase/manual inspection.

## Independent stream/geometry checks

- All 12 repaired binary FBX have UV0 and normals array records, valid indexing, no nonfinite UV/normals, no indexed duplicate faces, zero loose vertices/zero-length edges and zero source polygon degenerates.
- All 8 repaired P17/P18 FBX exhibit exact triangle-coordinate equality to their original source exports, unchanged bounds. Trimesh independently confirms watertight/winding-consistent positive-volume per intended part.
- P19 after source AABBs remain unchanged but surfaces were Boolean modified; bounding-box equality is NOT proof of identical silhouette. Naive fan triangulation of P19-05/07/08 loses watertight triangle topology.
- FBX self-intersection/narrowphase coplanar overlap, real Blender UI opening of blend, Unity importer, prefab transforms, colliders, light/shading, physical 3 m corridor clearance, PlayMode **NOT RUN**.
- 6 priority models have true original-FBX-derived wireframe BEFORE + wireframe AFTER + shaded AFTER (and source-part closeup). No procedural geometry substitutes used. Visuals are Python FBX renderings, not Blender or Unity screenshots.
- Local QA tests: 8/8 original-FBX and 9/9 repaired-FBX regression tests PASS on the actual downloaded archives. These test the QA tooling and pinned geometry invariants only.

## Ownership and gate decision

- **C01-17 (#23):** static indexed mesh repair verified; FBX/UV gate provisional PASS, full Unity QA BLOCKED.
- **C01-18 (#26):** original per-part topology was sound; no forced weld; full Unity QA BLOCKED.
- **C01-19 (#29):** P19-05, P19-07, P19-08 need safe explicit Blender triangulation/export + exact binary FBX retest; **FAIL P1 export gate**, regardless of supplier-reported polygon-edge PASS.
- Other 24 assets not independently retested from new PASS03 binaries here; static NOT RUN, overall BLOCKED.
- **C01-10 (#9):** do not substitute gallery reconstructions for FBX; use producer original binary exports in viewer after export gate.
- **C01-00 (#30):** no full QA acceptance or unauthorized merge. Leave PASS03 open.

The complete executable Python parsers, 12-model source and repaired FBX JSON metrics, 36-model CSV, per-sha provenance and six BEFORE/AFTER contact sheets are delivered separately in the conversation as an evidence ZIP. This file alone does not contain the binary assets or claim test execution in Blender/Unity.
