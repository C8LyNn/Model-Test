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


## PASS 04 — AMENDMENT A1 / binding triangle-export safety (2026-10-30)

Source of truth: #33 (three independent C01-02 export-geometry FAIL), #30 (topology). Extends this standard, without changing the dimensional, mounting or material contracts.

### P0 explicit triangulation: P19-05, P19-07, P19-08 ONLY

Independent C01-02 found complex polygons in real binary FBX with unsafe naive-fan triangulation: P19-05 has 3 polygons with >4 vertices, P19-07 has 16, P19-08 has 35. This is **triangulation ambiguity**, NOT proof of Unity importer failure. C01-19 must triangulate the REAL Blender source in existing PR #29 before re-exporting. For these three specific final render meshes, all source Blender polygons AND all FBX reimported Blender polygons must be **exactly three vertices each**. This stricter rule is NOT imposed on other 33 assets.

**No-loss mandatory invariants:**
1. Before original native .blend remains available. After is an actually saved native .blend at a changed file SHA. Real binary FBX must start with the Kaydara FBX Binary header. Keep object identity, parenting, moving pivots/sockets, root scale, UV0 seams, hard edges, visible silhouette and material slot identities.
2. Blender loop-triangle count and total area must match the explicit source triangles; zero degenerate triangles and reversed winding relative to polygon normals. FBX reimport must preserve geometric triangle-position multisets in world space within <=0.00001m, triangle counts, UV0 and material semantics. Equal AABBs alone do NOT prove equivalent surface.
3. Re-evaluate accidental boundary/non-manifold edges, loose verts/edges, duplicate faces, T-junctions, self- and inter-object intersections. Never automatically merge deliberately separate animated components.
4. P19-07 previously had 8, P19-08 had 2 source T-junction candidates. Each needs a named-object inspection distinguishing genuinely unstitched surface from intentional separate shell. Candidate alone is NOT FAIL.
5. Each report carries original producer commit SHA, source and FBX byte SHA256, actual Blender and FBX importer logs, source BEFORE/AFTER wireframes and shaded after, and independent C01-02 verdict. No missing stage can inherit PASS.

**Native enforcement**: Tools/c01_mesh_repair/triangulation_gate.py opens actual producer .blend and reimports hydrated binary .fbx in real Blender. The --require-explicit-triangles switch enforces triangles-only source and imported FBX for precisely P19-05/07/08; checks missing UV0, degenerates, winding, area and world triangle coordinates. Failure denotes source/FBX technical gate FAIL, not a tested Unity failure. Success does NOT grant independent QA approval.

### P1 documented exceptions and provenance — ALL 36

- **Intentional openings**: for example the 48 currently reported P15-07 gauge boundaries can be accepted only per named submesh, exact affected SHA, coordinates/count, explicit rationale, and independent C01-02 review; otherwise mark REVIEW_REQUIRED.
- **Separate parts**: P16-06 rotor, P17 levers/covers/fuses, P18 lids and handles, P19 folding table and other movable children must remain separately animated; co-located coordinates across objects are NOT a global weld instruction.
- **P16-01..07**: initial PASS04 baseline shows seven native .blend and Blender-produced binary FBX missing. OBJ or ASCII FBX static repair does not satisfy the native gate. Mark Blender/native FBX stage NOT_RUN until actual bytes, hashes and importer logs are verified.
- **SHA policy**: every producer push changes the inspected revision. QA attaches per-ID verdict to exact producer commit SHA and file digests, then re-runs affected checks. Six sample models never imply 36/36 acceptance.
- **Ownership**: C01-01 standard and metrology; C01-19 source repairs; C01-02 independent topological QA; C01-10 Unity prefab/collider clearance; C01-03 source/version ledger; C01-00 release GO/NO-GO.

PASS04 remains OPEN until all 36 original geometry exports have independent SHA-pinned QA, three P19 failures cleared, Unity acceptance actually measured or explicitly blocked, and no unauthorized merges or redesigns.


## PASS 05 — ADDENDUM A2: five P19 export-risk assets + executable gate

**Authority:** C01-00 #33 PASS05 / C01-02 PR #13. **No new geometry family or global forced triangulation.** PASS04's P19-05/07/08 targeted triangle-only source/export gate is expanded to **P19-01 and P19-02**, for a total of **five** independently flagged P19 n-gon risks. P19-03 has complex faces without currently reproduced fan degenerates and requires evaluation, not automatic source triangulation. P19-06 and P19-04 are not subject to this stricter five-ID gate absent new concrete defects.

**PASS05 independent archived binary FBX readings:** P19-01 38 complex n-gons / 12 degenerate naive-fan triangles; P19-02 31 / 8; P19-05 3 / 1; P19-07 16 / 19; P19-08 35 / 7. P19-06 0 / 0. **Original polygon faces of these six contained zero degenerate source triangles as parsed from their native FBX indices.** The fan numbers are only *exporter-ambiguity stress-test candidates*, not real Blender or Unity mesh failure proof. The archived P19-02 file is **SHA a42a57d168...** from a cleanup artifact, which may differ from other QA's older candidate; conclusions must remain tied to exact SHA. Detailed per-part face indices and 3D coordinates of all zero-area fan triangles were measured from real FBX Geometry/Vertices/PolygonVertexIndex and retained in the handoff.

**Acceptance for each of the five named IDs:**
- Producer saves real original revised Blender .blend and a real **Blender binary FBX** with changed SHA-256; all final source render polygons and FBX imported polygons are triangles, no zero-area tris, invalid UV0, normal or winding errors. Blender checks triangle local/world position multiset, area, visual silhouette, hierarchy, sockets, material/UV loop attributes and pivot/movable parts before/after. Only source-confirmed flaws are repaired.
- Specific .blend + binary FBX hashes and producer commit pinned, before/after topology V/E/F/Tris + per-part boundaries, independent C01-02 per-SHA review and actual Blender FBX reimport. No blanket mesh welding and no fan triangulation used as repair algorithm.
- **P15-07** 48 boundary edges on 2 intentionally open gauge face submeshes must remain exception candidates until C01-02 confirms named object and exact source SHA; separate moving parts remain separate even when co-located.
- **No automatic QA promotion** from STATIC TRIANGLE_ONLY or CI SUCCESS. Real Unity 6 URP Editor import / prefab / PlayMode and C01-02 signoff are independent required gates.

**CI rule:** runner_id=0, steps=[], and Actions billable 0 ms indicate failure before execution; classify as **INFRA_NOT_RUN**, not Blender FAIL or PASS. Root cause (account billing, runners, plan, quota or GitHub allocation) requires authenticated repository Actions/billing permissions; public GitHub Status is insufficient to prove the account-specific cause. Do not disable release gates to conceal incident.

**C01-01 scope:** this addendum is standards and independently observed binary FBX forensics, NOT a source model repair claim. Existing Draft PR #31; no merge. Wave03 STOP.


## PASS 06 — ADDENDUM A3: source repair proof and executable signature gate

**Governing dispatch:** #33 comment 6529370725. Binding C01-01 technical gate, NOT evidence that producer source meshes have been repaired.

- P19-05/07/08 then P19-01/02: native .blend must be actually saved after geometry-preserving triangulation and binary FBX re-export, with file SHA-256 and Blender FBX reimport, UV0/material/hard normals/winding/pivot/hierarchy invariants. Offline FBX candidates without matching revised .blend are NOT final fixes.
- **P19-01 specific hold:** investigate genuine Cube.001 polygon 59 self-intersection in source Blender before triangulation. Triangle-only files alone do not certify that crossing contours were fixed. Preserve original silhouette and real wireframe BEFORE/AFTER.
- **P19-07/08:** inspect T-junction candidates before welding. Preserve intentionally separate and animated components.
- **P16 native file signatures:** correct prefix is exactly the initial 8 bytes BLENDER- (e.g. real 4.x source begins BLENDER-v400); use data.startswith(b"BLENDER-") in Python or read at least 8 bytes in Windows PowerShell. Reject 7-byte truncation and Git LFS pointers. FBX must start Kaydara FBX Binary and be imported in actual Blender. Magic success is NOT an importer/topology PASS.
- C01-01 corrected Python and Windows signature validators in existing C01-16 PR #12/#28 and added seven regression test methods in each. Independent local real-bytes header regression on two archival .blend source files: 12/12 PASS, but Blender runtime and seven new C01-16 exports NOT RUN.
- GitHub Actions failures with runner_id=0 and steps=[] classify as INFRA_NOT_RUN. Repo admin metadata does not guarantee app access to Settings/Actions/billing. When no Blender 4.x + Git LFS runner is accessible, status NEEDS_OWNER_ACTION; specify exact owner control and executable commands. No budget, payment, ship, geometry or merge changes without approval.
- Only actual producer-owned changed Blender source SHA, 36 SHA-pinned binary exports, independent C01-02 QA, and real Unity 6 URP validation can close #30. Keep all production PRs Draft.
