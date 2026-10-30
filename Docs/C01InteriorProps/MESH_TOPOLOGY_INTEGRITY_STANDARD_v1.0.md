# C01-01 — MESH TOPOLOGY INTEGRITY STANDARD v1.0 / PASS 03

**Owner:** C01-01 ASSET STANDARDS & PIPELINE | **P0 issue:** #30 | **Scope:** P15-01–P19-08 (36 unique props; Wave01=16, Wave02=20).  
**Scope of this document:** binding topological acceptance contract; it does **not** change `C01-PROP-INTERFACE-0.2.1` or `C01-PROP-INTERFACE-0.2.2-WAVE02` dimensional, mounting or scene contracts.

**Freeze:** Wave03, redesign, new meshes/materials for aesthetics, ship scenes, deck layouts, corridor topology, door geometry and unauthorized merges. Owner threads C01-15–19 perform actual repairs on their existing production branches. This standard author must not overwrite producer mesh sources.

## 0. Ground truth and evidence precedence

1. First compare **actual authored .blend** and binary FBX from the producer's referenced commit. The prior six-model gallery showed reconstructed primitives: visual faults there are **VIEWER_RECONSTRUCTION_DEFECT** until reproduced in original source.
2. An automatic audit generates **candidate defects**, not final diagnoses. Each candidate requires classification by mesh role: `SOURCE_MESH_DEFECT`, `INTENTIONAL_OPEN_SURFACE`, `INTENTIONAL_SEPARATE_PART`, `UV_SHARP_SPLIT`, `VIEWER_RECONSTRUCTION_DEFECT`, `UNCONFIRMED_CANDIDATE`, `NOT_RUN`.
3. Results must be keyed by `asset_id`, `source_revision_sha`, native .blend SHA256, object name + mesh datablock name. No claims of passing **Blender/Unity** from Python-only or reconstructed previews.
4. Lock the **original** appearance. Save repaired sources with a new version/commit; preserve original for BEFORE. Every comparison uses the same actual asset root, camera, projection and pose.

## 1. Vertices and edges

| Rule | Fail condition | Exception |
|---|---|---|
| Vertices | Unused vertices, accidental splits in what should be one connected surface, orphaned islands | A separately authored intentionally isolated mesh child, hard-edge and UV seam splits after export |
| Weld | Repair only where a topologically shared surface is intended | NEVER `Merge by Distance` blindly across material boundaries, UV seams, distinct rigged/animated objects, parts that pivot independently or deliberately overlapping components |
| Candidate threshold | First measure co-located candidates at ~1e-6m, inspect 1e-5m neighborhood; any destructive weld requires controlled per-vertex patch | Duplicate coordinates can be deliberately split for normal and UV indexing |
| Zero length | Edge length < 1e-7m (scale 1 unit=1m) and not part of a documented deliberate degenerate placeholder | Normally no valid exemption for export geometry |
| T-junction | Vertex interior lies on another intended connected face edge and is not stitched | Explicit independent adjacent shell may intersect/touch without topological identity |
| Non-manifold | More than two incident faces on single surface edge, bad winding, unintended open boundary | Intentional thin panel, grille, decal, single-sided card, separate mechanic geometry; define expected open edge set/count or documented reason |
| Connected components | Unexpected separate islands *within one required closed mesh* | Multiple intentionally independent structural islands, screws or accessory children with separate material/animation purposes |

Connected component count must be per Blender mesh datablock/object. Never demand that the whole prefab is one connected component or one watertight volume.

## 2. Faces and self-intersection

- **Degenerate face:** area < 1e-12m², invalid triangle winding, zero area after export => hard defect unless genuinely nonrendering explicit marker; prefer remove marker from export.
- **Duplicate face:** identical physical polygon with coincident vertex positions, including opposite winding, creates z-fighting and requires explicit review. Identical surface on independent mesh parts is a candidate only, not guaranteed bug.
- **Overlap:** treat BVH overlap as a **candidate**, not definite self-intersection (touching faces on legitimate mechanical parts also flag). Confirm in real Blender geometry, inspect physical penetration >0.0001m. Do not automatically boolean-union mechanically independent parts.
- **Triangulation:** compare source face area/shape with actual FBX triangulation; preserving visual silhouette/UV0/material assignment is more important than retaining identical source quad face count. An OBJ/FBX may legally split vertices on UV/hard edges.
- **Open surface:** not an automatic FAIL. Annotate intentional open geometry by object, reason and expected boundary topology. Unexplained boundary on an expected closed body is FAIL on independent QA.
- **Normal orientation:** adjacent manifold faces should have consistent winding; inward/outward across solids assessed visually in Blender. Signed volume can diagnose fully closed solids, but a negative aggregate volume is insufficient to identify a specific wrongly oriented disconnected component. Preserve hard/sharp edges.
- **UV0 and material slots:** UV0 must remain valid on all rendered surfaces, normal tangents consistent after FBX export. Do not destroy deliberate seams to satisfy coincident-vertex warnings.

## 3. Parts, transforms, silhouettes and mounting

Pivots, socket coordinates, dimensions, material families and named moving child hierarchies are **immutable** unless C01-01 approves a documented compatibility revision. Object roots remain local scale (1,1,1) for Unity and keep authored front −Z. Compare BEFORE and AFTER bounds, pivot and sockets to ≤1mm; root scale deviation ≤1e-4, no arbitrary transforms. If repair changes face/vertex count while preserving silhouette and UV0, that's fine. **P17-06 covers, P18-05 lid, P19-06 foldable tabletop, P16-06 rotor, P17-07 fuse, P18 wheels** (and equivalent moving children) remain separate meshes and pivot transforms.

## 4. Tooling and evidence (mandatory per asset)

- `mesh_topology_before.json` — original .blend, per real mesh object: V/E/F/tris, disconnected components, loose geometry, zero-length edges, degenerate faces, duplicate/co-located positions, boundary, non-manifold, winding, T-junction candidates, BVH overlap candidates, UV0/materials, object transforms, local bounds, source SHA.
- `mesh_topology_after.json` — exact same measurement after producer's actual repair. Include list of named edits and before/after per defect. **No fabricated zero-defect after report**.
- Actual Blender wireframe BEFORE/AFTER and shaded AFTER from same camera, plus topology joint close-up, with screenshot file hashes. Parametric recreations cannot substitute for original source.
- Real saved repaired `.blend`; exported **binary** FBX; import FBX back into Blender; report comparing object count, part hierarchy, transform/pivot, axis directions, bounds, UV0 count, normals, triangulation, materials and any changed seams. FBX may split vertices normally; don't compare exact counts as a hard gate.
- Unity 6 URP imported prefab with measured bounds, correct shading, colliders and moving part sweeps if Unity available; otherwise explicit `NOT_RUN`. Test corridor/door/elevator clearance only in scene referencing actual source files.
- C01-03 versions and SHA of before/after; C01-02 verifies exact independent source SHA and individual stages; C01-10 viewer only genuine GLB/FBX; C01-00 authorizes final release.

## 5. Audit statuses

| Status | Meaning |
|---|---|
| `PASS` | Mandatory defects confirmed absent or individually justified; actual Blender and native export checks executed and reviewed by C01-02 |
| `FAIL` | Reproduced actual model source defect with geometry pointer and steps |
| `BLOCKED` | No real source/engine/evidence to finish required check |
| `NOT_RUN` | Stage was not executed |
| `INTENTIONAL` | Per mesh exception with reason, reviewed by C01-02, not blanket exemption |
| `CANDIDATE` | Diagnostic signal not yet reproduced in original mesh; **never** report as automatically repaired |

The code `Tools/c01_mesh_repair/topology_audit.py` is *read-only*, and never auto-merges anything. `qa_blender=AUDIT_EXECUTED` only means inspection occurred: it is **not a PASS**. `qa_fbx_roundtrip` and `qa_unity` remain NOT_RUN until executed by independent stages.

## 6. Priority queue

P0 six actual models: `P17-04`, `P17-05`, `P18-04`, `P18-05`, `P19-07`, `P19-08`. Then the remaining 30, after the P0 six actually undergo independent retest. Model production **STOP**. Every producer repairs their own PR only. C01-01 does not mutate their `.blend` or create replacement models.

**Exit gate:** 36 per-SHA BEFORE/AFTER verified, real FBX roundtrip, independent C01-02 topological PASS, exact montage in Unity when possible. No blanket approval from static code.
