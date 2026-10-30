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


## DETAIL PASS 12 — ADDENDUM A4: mechanical detail and physical contact acceptance

**Dispatch:** issue #36. Authorization applies only to the existing P15–P19 asset IDs. No new models, random greebles, ship changes or automatic welding; C01-01 does not independently sign C01-02 QA.

### Actual source-pinned observations

C01-18 authoring OBJ producer HEAD **4a0e58d422335af9c7f79fdcf6a80feb7c9c6435** compared to **ecfac25934a98985eca8222060e190f8d5cecd5c**: **49/49** ORIGINAL parts have identical oriented face-corner positions, UV0 and normals (full loop signatures, not merely bbox). P18-01: parts 15→37, tris 180→684; P18-02: 17→47, 204→1012; P18-03: 17→53, 348→1532. **88 actually added submeshes in 3 existing real source OBJ.** Read-only evidence recorded in [C01_01_DETAIL_PASS12_PILOT_SOURCE_EVIDENCE.json](C01_01_DETAIL_PASS12_PILOT_SOURCE_EVIDENCE.json).

C01-17 authoring P17-02 current spec commit **bff1886e09ec04d21bab84a2f15e52c1cfb4a72b** compared to **85732482b075bcfab68e5d660d26318dfe9c630d**: **20/20** original spec parts unchanged, 18 new definitions (12 key guides, 2 clamp reinforcements, 4 fasteners). Actual native mesh export NOT RUN.

### Mechanical attachment gates

- **P18-01 crate:** Original eight trim strips were displaced **28 mm** from the shell. Revised source has eight TrimBacker support meshes whose AABBs contact both trim and shell with **0 mm box separation**. Confirm actual triangle faces physically connect without coplanar overlaps; assess hinge/latch mechanical attachment and preserve original corner/lid structure and opening pivot. Added purposeful hinges or latches may protrude slightly; document silhouette/AABB delta, don't require identical old box if intentional.
- **P18-02 rack:** Two original top labels were **50 mm above the top deck** and **22 mm behind its edge**. Revised source adds two mounting backplates; their AABBs overlap the correct original label and top shelf with **0 mm box separation**. Confirm physical bracket/bolt/shelf-to-frame support in real Blender. No floating plate or fastener; eliminate coincident face z-fighting, not valid touching edges.
- **P18-03 cart:** Preserve **four** separate movable wheels and Y=0 ground contact, all original wheel orientation and symmetry. Wheel center to corresponding upright horizontal offset is **67.268 mm**; shifting wheels toward posts without checking steering/rotation and collision is prohibited. Revised source has **nine assembly parts per wheel** (hub, axle, forks, anchor, gusset, fastener); the Axle→ForkOuter→Anchor chain has zero AABB gap for all 4. Actual face-level joins and pivot motion must be checked in Blender/Unity; AABB proximity cannot prove attached surfaces.
- **P17-02 access reader:** Preserve 12 separately interactive keypad keys and state/EMISSION materials, existing wall-mount pivot and collider. Actual source spec now adds 12 retaining guides, 2 clamp reinforcements and 4 screws. Check guide-to-keybed and screw-to-backplate contact and avoid doubled outward-facing planes.
- **P15/16/19:** Finish existing export, UV/normal and source triangulation defects before extra purposeful details. P16-06 rotor remains separate. No extra detail may hide a P19 topology defect.

### 5-stage signoff contract

1. **AUTHORING:** Pin exact producer Git commit and Git blob; preserve all original face-corner geometry/UV0/normals/pivots except approved targeted defects. Record individual new parts and contact gaps. AABB checks are screening, never final geometry acceptance. Never global merge-by-distance.
2. **DETAIL COST:** Record actual V/E/F/T/material slot and part count, actual Unity draw calls, inspect hidden polys and LOD. Measured pilot increases: 3.8x, 5.0x and 4.4x triangles; these are review triggers (not automatic reject thresholds).
3. **REAL BLENDER:** Open actual revised source in Blender 4.x, save a changed native .blend, export genuine Blender-origin binary FBX, and independently reopen/import it. Compare scale, pivots, parenting, UV loops, normal/winding, material assignments, moving parts and actual triangle contacts. Save matching real BEFORE/AFTER shaded/wireframe and detail closeups plus complete SHA-256 of final .blend and FBX.
4. **INDEPENDENT C01-02:** Audit actual final FBX SHA bytes and triangle-level interpenetration, coplanar z-fight, T-junction, nonmanifold and proper attachment; no automatic signoff by old SHA.
5. **UNITY C01-10:** Real Unity 6 URP prefab/import, wheel clearance and rotation, reader states, colliders/scale; if editor unavailable, NOT RUN. No merge without formal authorization.

**C01-01 status here:** REAL authoring source verification executed and producer details measured; no native Blender roundtrip or Unity run by C01-01. Related #33/#30 source export blockers remain unresolved.


## DETAIL PASS13 — A5 / world-space source contact acceptance

**Supersedes the P17-02 unresolved screw-gap claim in PASS12.** At C01-17 producer commit `97f6d77eab77dbdd171c2321a922980517efefed`, glTF blob `d80a67af140e434b983104aaec0078f9cf5bd66f`, independently decoding actual POSITION indices and applying node TRS exactly once yields four 9×9×3 mm mount screw heads. Each head penetrates original MountBacking by 0.5 mm and **16 real screw-mesh triangles per head cross the backing front plane within backing XY bounds**. Earlier 0.81 mm screw-size / 0.976 mm detached-gap report is not a valid verdict for these source bytes; do not alter correct screws or force-weld them.

The only confirmed former reader clearance issue was **Keybed back 58.0 mm versus old Housing front 57.5 mm** (+0.5 mm separation). The latest source revision changes only Housing node translation/scale and its spec: back stays 22.5 mm, front advances to 58.5 mm, creating **0.5 mm positive seating against the Keybed**, preserving the 38-part, 536-triangle source and silhouette. **Source contact geometry PASS at pinned SHA**, BUT native Blender source save, genuine binary FBX re-export/reimport, hard-normal/pivot/material and Unity importer are separately **NOT RUN**. Do not conflate authored glTF source with approved final binary.

**Independent latest P18 source readback** on exact existing producer OBJ bytes (P18-01 SHA256 `5749f13e30f8e1d853c4488dde2e030fb7b55a59b14b71bedeef61297c8c3adf`; P18-02 `55d652a42ab7c22709814938535445a0814d9c9ff81237b59925a9115521ee98`; P18-03 `3996be33105a17163d4c8a753012aca891c1b19b156abf32ddab02d8fbca50e0`): axis-aligned **closed eight-corner boxes** permit unambiguous solid-overlap contact acceptance for inspected P18-01 trim/backer/shell pairs and P18-02 both label/backplate/shelf pairs. They overlap by positive thickness, not merely touching AABB corners. Four P18-03 wheels have minimum Y=0 and fork-outer/anchor are both closed boxes with 16×4.5×46.5 mm solid overlap. **Do not extrapolate axis-aligned-box evidence to cylinder/caster meshes**: wheel motion/axle rotating pivots require Blender/Unity narrow-phase and animation checks, 0 blind weld.

Full SHA-locked numerical source evidence: `Docs/C01InteriorProps/C01_01_DETAIL_PASS13_SOURCE_CONTACT_RECHECK.json`. Previous P0 export/Unity blocks remain open; source preflight is not C01-02 release PASS. Keep producer PRs Draft.


## DETAIL PASS14 — A6 / real mechanical source repair verification

Independent **actual producer OBJ** source before/after verification in `C01_01_DETAIL_PASS14_ACTUAL_SOURCE_MESH_QA.json` proves three specific producer-owned repairs in existing C01-18 Draft #18 at pinned after commit `996b8e8f8deb86e2a59f1468fb8b318a7815cfa7`:

- **P18-01**: eight genuine same-facing trim/backer coplanar pair candidates (**0.002496 m²** total) are reduced to **zero** by local backer end-plane inset; source `Lower_Rim` 10mm gap is replaced with **2mm closed-box contact** with `Crate_Shell`. Source face/UV/normal/material indexing and 37 part names are unchanged. The eight trim/backer corrections are **not** equivalent to blindly welding parts or deleting whole interior faces.
- **P18-02**: two original `Back_Support_0.6/1.48` free 30mm lateral ends are extended into both existing `Rack_Post` closed boxes by **5mm**, without new parts or face-index changes. Both established upper-label supports remain in place.
- **P18-03**: source wheel-vs-upright noncoplanar **triangle intersection pairs** fall from **11+11+13+13 = 48** to **0** by raising each upright lower plane from 0.145m to 0.212m, retaining a 2mm tire-top gap and all four wheel ground-plane contacts. Four original lip-to-deck gaps of **5mm** become **2mm positive box embedment** by shifting the original lips 7mm down; wheel/hub/pivot identities and face/UV/normal/material records remain unchanged.

The source repair is attributable to C01-18, not C01-01. This independent QA is at a fixed **Git producer commit**, not an unpinned branch. Source contact is **PASS_TARGETED** for listed interfaces only; full interpenetration BVH, rotating hierarchy, material tangent parity, 4.x Blender native source save/export/reimport, independent final 36 FBX C01-02 QA and Unity 6 URP remain separate `NOT_RUN` / `PENDING` gates. Read the receipt's full original and revised physical SHA256 and Git blob SHA1; **never promote source PASS into binary FBX release**.


## DETAIL PASS15 — A7 / detail density, source quality and performance gate

**Executed source-data baseline:** `Docs/C01InteriorProps/C01_01_DETAIL_PASS15_TEN_MODEL_ACTUAL_SOURCE_QA.json` is an independent readback of 17 actual existing GitHub OBJ files spanning seven P16 lights and three P18 cargo props (10/36 existing IDs), with individual physical SHA-256 and Git blob SHA1. Combined current geometry is **237 mesh parts / 5,024 triangles**, up from **92 parts / 1,248 triangles** prior to the controlled detailing (145 new functional pieces; +3,776 authored triangles). All 10 current model sources passed specific per-part indexed integrity gates (face-corner UV0/normal reference presence, winding, manifold edge pairing, 0 duplicated/zero-area indexed triangles and normal direction mismatch). This is NOT final output topology after Blender FBX triangulation and importer changes.

**Functional attachment review:** for P16 seven lighting IDs, all **57 added existing-model detail meshes** have transitive AABB broadphase contact paths back to at least one original part; **zero have no broadphase neighbor**, but six connect via another newly authored mounting element rather than directly to a pre-existing part. Do not label this result "57 verified triangle intersections": AABB contact is *necessary screening only*, and moving meshes may intentionally be independent. Specifically P16-06 four `ROTOR` bolt objects share support bounds with original `ROTOR_Steel_4` and `ROTOR_DarkPanel_6`; their parent/animation allegiance must be confirmed in real Blender/Unity and must never be transferred to `STATIC` through mesh joining.

**Density guard — no arbitrary polygon target:** actual P16 model triangles are 208–324 each and P18 pilots 684/1,012/1,532; source growth factors range ~3.0–4.96×. A high detail multiplier is a *performance review trigger*, not a topology failure. QA must inspect readability, purposeful mounting and whether surface-only screws are better served by textures/normal maps before increasing geometry further. Cost must be measured as **imported renderers, submesh-material slots and draw calls**, not triangle count alone. A theoretical upper bound of **237 individually imported object renderers for these ten simultaneously instantiated assets** is **not an actual measured draw-call count** (engine batching, mesh combining and instancing can change it). C01-10 should record Unity6 URP batches/set-pass/frame times for a controlled staging scene with material and lighting parity. Do not prematurely combine moving controls, rotor blades or castor/wheel pivots; consider selective mesh-combining for *static* detail children only after a real import and hierarchy/UV/material audit.

**Detail-pass release gates:**
1. `SOURCE_INDEXED_PASS`: exact authored file SHA/commit, verified source polygon and normal/UV0 consistency, purposeful attachment pairs, no additional floating or duplicate coplanar surfaces.
2. `NATIVE_BLENDER_PASS`: actually open and resave revised original .blend through Blender4.x, verify material, pivot, moving child identity and render BEFORE/AFTER shaded+wireframe with common camera.
3. `BINARY_FBX_PASS`: export true Blender binary FBX, re-import in new process, compare world-space triangulation, transforms, normals and UV0 with authoring target, record physical SHA256.
4. `INDEPENDENT_C01_02_PASS`: independent verification of exact current binary bytes and all **36/36** final assets.
5. `UNITY6_URP_PASS`: actual importer/prefab/LOD-material/pivot-animation/clearance and staging performance measures. Prior separate candidate FBX or glTF/OBJ source checks cannot satisfy this gate.

**P0 holds:** P19-07 vertex-on-edge candidates need *actual Blender visual* diagnosis; native Blender/export for P16/P17/P18 remains NOT RUN in this execution environment. Never use a report or synthetic preview to replace genuine native files; do not add unrequested model IDs, modify ship scenes, blindly weld or merge production drafts without independent QA.


## DETAIL PASS15 — A8 / latest producer commits supersede the first PASS15 snapshot

**IMPORTANT freshness correction:** A7 and `C01_01_DETAIL_PASS15_TEN_MODEL_ACTUAL_SOURCE_QA.json` describe an independently checked **earlier immutable source snapshot**, not the newest PASS15 source commits. The authoritative **later source** SHA-pinned readback is `Docs/C01InteriorProps/C01_01_DETAIL_PASS15_LATEST_12_MODEL_QA.json`. Future C01-02/03/10 gates must use that later receipt's file SHA or re-evaluate any additional producer commits. Do not copy earlier P18/P16 SHA or P17 count into latest-source catalog.

New PASS15 authored, actually read and statically screened existing-ID detail meshes at locked producer commits: **P18-01/02/03** at `91659e272ef1fe49fdaf7a906b4b6b2769ce50c8` add **12 functional hinge retainers/support gussets/fixed fork-crown bolts** (+288 triangles), all 12 with named original geometry AABB contact; original 137 component mesh source sections remain byte-semantically identical (newline differences only). **P16-04/05/06** at `604b6b9afb41ff9988cc2eea05c1d02034b2070e` add **8 purpose-built diffuser retainers/cover lips/suspension rod seats** (+96 triangles), all 8 with original support bounds; P16-06 additions are explicitly STATIC, separate from four original ROTOR solids and four PASS12 ROTOR bolts. **P17-01/03** at `28824c2fa48e8523f9a8715df71c57379fa7634a` add **16 support/bolt/guide/retainer meshes** (+392 tris); all 16 with named source AABB support. The original glTF mesh buffer, primitive, accessor and original node values have been compared with immutable BEFORE revisions and preserved.

A total of **12 existing IDs / 302 authored source parts / 6,212 triangles** are now represented in the source QA scope (before this PASS15 wave 266 / 5,436). **36 net added existing-model child meshes and 776 new source triangles.** Each of 8 newly modified/created source files passed relevant indexed UV/normal/triangulation checks (P16+P18 OBJ closed edge incidence; P17 actual transformed POSITION / NORMAL / UV0 glTF geometric triangle check), and all 36 added functional parts pass **broadphase support**, NOT true animated/narrowphase QA.

Do not optimize based only on a raw `302` object count: it is a potential number of imported object renderers when all 12 models are instantiated uncombined, *not* a measured draw-call number. Prevent duplicating tiny decorative bolts; prioritise meaningful silhouette and user interactions. On Unity6 URP native import, measure actual draw-calls, materials, triangle budget, LOD and prefab child hierarchy. No movement-preserving weld or material/UV loss is authorized. **New real .blend sources, Blender-exported FBX, Blender reimport, Unity and C01-02 full 36 QA remain NOT RUN/PENDING.**


### A8.1 — independently executed 36/36 new detail triangle support

**Source narrowphase upgrade:** the `C01_01_DETAIL_PASS15_LATEST_12_MODEL_QA.json` receipt has been updated from preliminary AABB support to actual geometric indexed-triangle support tests. On exact pinned latest P16/P17/P18 source file bytes, all **36 newly added PASS15 child meshes** were confirmed to cross a named existing physical attachment surface by at least one true noncoplanar triangle-edge intersection: **P16 eight, P17 sixteen, P18 twelve**. The receipt records the individual child/support names and positive triangle-pair hit counts; each was evaluated from authored mesh triangles, with full glTF node TRS applied for P17.

**Important acceptance boundary:** this is `SOURCE_NEW_DETAILS_36_OF_36_TRIANGLE_SUPPORT_PASS` for those 36 named interfaces, **not** a global proof of zero coplanar z-fighting, unrelated structural collision, runtime animation or precise render-state acceptance. Keep each original moving part and pivot separate. Never mark an exported FBX or Unity6 prefab as PASS based on this test alone. Export/QA/Unity release gates remain NOT RUN/PENDING until real native Blender source, real Blender-exported binary and independent final SHA-locked engine checks.
