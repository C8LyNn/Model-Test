# C01-02 — DETAIL PASS 17: independent, immutable-commit source QA

**Date:** 2026-11-01. **Gate:** SOURCE-ONLY PARTIAL PASS / NATIVE & UNITY HOLD. **0/36 FINAL APPROVED.**

## Inputs and live-source proof
- C01-17 producer Draft [#17](https://github.com/C8LyNn/Model-Test/pull/17), immutable HEAD `7664324f503b83f01d0dccfc9578299465da1926`.
- C01-18 producer Draft [#18](https://github.com/C8LyNn/Model-Test/pull/18), immutable HEAD `5769d0326a1bc4bdcfa892de0f95d912ab30b55a`.
- **Read actual bytes** from six OBJ meshes and decoded three P17 glTF embedded buffers. Source SHA-256 independently computed using a SHA-256 implementation verified against the empty-string and `abc` standard test vectors. All exact source hashes and Git blob SHA in [machine receipt](INDEPENDENT_PINNED_SOURCE_QA.json). No source material re-created from a spec.
- **New producer race correctly handled:** P18 data changed mid-audit from 159 parts/3764T to **169 parts/4044T**; all final P18 results in this report refer ONLY to pinned `5769d03`, not earlier HEAD.

## Independent current OBJ/glTF topology (observed)
| Asset | OBJ mesh parts | Triangles | Invalid/degenerate/duplicates/nonmanifold/winding | Co-oriented coplanar area |
|---|---:|---:|---|---:|
| P17-01 | 25 | 380 | 0 | 0 |
| P17-02 | 38 | 536 | 0 | 0 |
| **P17-03** | 20 | 424 | **8 boundary edges** (2 separate loops), otherwise 0 | 0 |
| P18-01 | 47 | 980 | 0 | 0 |
| P18-02 | 59 | 1284 | 0 | 0 |
| P18-03 | 63 | 1780 | 0 | 0 |

**Total: 242 actual mesh parts / 5104 OBJ triangles.** Geometric-edge manifold counts use positional welding ONLY in the read-only analyzer at 1e-7 m; NO destructive source welding. Same-facing overlaps are true projected triangle clipping, not AABB-only tests. Current P18 OBJ 3/3 complete UV0 and vertex-normal references, checked against geometric face normals. P17 fallback OBJ has **no** `vt/vn`, so UV/normal attributes were **separately checked in three REAL P17 glTF**: 3/3 decode and finite accessor data, zero degenerate/index/misoriented faces. Unique reusable glTF mesh triangles differ from instanced OBJ triangles, as expected.

**P17-03 P1 REVIEW:** `LeverShaft` 4 open boundary edges at Y=0.349m; `LeverGrip` 4 at Y=0.490m. These are the joint-side open ends, potentially hidden by connected parts. They are NOT an automatically confirmed visible hole, but producer must explicitly document intentional non-manifold geometry OR seal the ends, then provide actual animation/clearance proof. Do not misreport global 0 boundary edges. P17-01 repaired keyboard guides remain zero co-oriented coplanar overlap. P17-02 existing source integrity retained.

## P18 delta from final PASS16 (not merely producer assertion)
- P18-01: **43/868 → 47/980**. Four lid UpperKeeper screws, **16** triangle-pair support hits each.
- P18-02: **55/1172 → 59/1284**. Four rack post footplates, **24** source triangle-pair support hits each.
- P18-03: **61/1724 → 63/1780**. Two handle clamps; each intersects intended handle post **24** triangle pairs and handle grip **16**.
- **10/10 new functional pieces** had positive real 3D segment/triangle crossings against named original supports. Previous P18 OBJ is an exact source-text prefix of new OBJ for 3/3 files; all pre-existing part bounds unchanged; no new same-facing coplanar overlaps; all four cart wheels still contact ground **Y=0m**.
- This check does NOT prove animated clearance, exact weld craftsmanship, Unity collision shape correctness, or photoreal material parity.


## Read-only interactive actual-source geometry comparison

[Open or download the standalone **actual-source before/after HTML viewer**](Previews/ACTUAL_SOURCE_INTERACTIVE_BEFORE_AFTER.html). For P18-01/02/03 it embeds both real PASS16 and current pinned PASS17 OBJ geometry (synchronized camera); P17-01/02/03 show their current exact authored OBJ triangles. Local user workflow: download the .html file from the private GitHub repository and open it in a browser. No private GitHub API key or external CDN needed.

**9 distinct real OBJ source versions embedded**, with all current **5104** triangles and prior P18 **3764** triangles. Source vertex coordinates are signed micrometer-quantized (max 0.5µm deviation); actual face indices, per-face source material names, and group names retained. The browser script parsed successfully and **9/9** decoded packed binary lengths / all triangle-index/material/group references PASS on read-back from the actual committed HTML Git blob (`93e06e68c2db01558285933e6c7b26d94e4158d1`). No invented geometry and no historical FBX loading. Diagnostic Canvas2D draws shaded and optional wireframe overlay, with drag-to-rotate and wheel zoom; scene material appearance is approximate and painter-sorted occlusion is not a substitute for native render. **Visual browser-run validation NOT RUN.** Real Blender 4.x and Unity 6 screenshots **NOT RUN**.

## Release blockers and required handoff
**Six current canonical P17/P18 FBX paths contain Git LFS text POINTERS (130 bytes each), not the new hydrated Blender-exported binary FBXs.** The SHA-256 of an LFS `oid` refers to an earlier binary and MUST NOT be claimed as current-detail FBX SHA. Full pointers listed in JSON. No new native FBX/BLEND supplied to this QA role in this wave.

| Gate | Status |
|---|---|
| Six actual OBJ authoring-source topology scans | **RUN** |
| Three actual P17 glTF attribute scans | **RUN** |
| New P18 +10 actual triangle-based mechanical attachments | **RUN: 10/10 CONTACT** |
| P17-03 explicit intentional open ends or repair | **P1 REVIEW** |
| New Blender 4.x .blend save and Blender-origin binary FBX | **NOT RUN** |
| Hydrated current FBX SHA256 and Blender reimport | **NOT RUN** |
| Actual-source interactive shaded/wireframe before/after viewer | **GENERATED** from 9 real current/prior OBJ sources. Script syntax and packed indexed geometry **9/9 PASS**; visual browser runtime **NOT RUN**, and not a Blender render. |
| Unity 6 URP actual importer, materials, pivots, hierarchy, animation | **NOT RUN** |
| Release acceptance across 36 existing model IDs | **0/36 FINAL APPROVED** |

**C01-17:** inspect/cap or justify P17-03 shaft/grip boundary loops, keep `LeverPivot` moving hierarchy; preserve repaired P17-01 guides and P17-02. **C01-18:** keep 10 new real attached parts, P18 wheel ground contact and old part bounds; source-only QA now pinned to HEAD `5769d03`. **C01-00/03:** produce current native Blender4 FBX+BLEND, hydrate exact LFS binary, record file SHA and runner evidence. **C01-10:** run Unity 6 importer/prefab QA on exactly those approved binary hashes. **C01-02:** inspect the exact native files independently before recommending acceptance. **NO MERGE.**
