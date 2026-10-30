> **HISTORICAL PIN / SUPERSEDED** (2026-10-30): This handoff is an earlier PASS16 snapshot. P17-01 KeyboardGuide and Backbone geometry was subsequently repaired on real producer source PR #17 and independently rechecked by C01-02. P18-01/02/03 producer source gained 10 functional parts after this snapshot. For current immutable source SHA-256, reference index, QA and release gate use **[CURRENT_SOURCE_AND_NATIVE_QA_HANDOFF.md](./CURRENT_SOURCE_AND_NATIVE_QA_HANDOFF.md)** and **[LIVE_ASSET_REGISTRY_36.json](./LIVE_ASSET_REGISTRY_36.json)**. Original observations below are preserved as history; they are **not current failed P17-01 source status**. Native Blender/FBX/Unity remain NOT_RUN and 36/36 final release BLOCKED.

# C01-03 — DETAIL PASS16 / reference-driven library intake and technical handoff

**Date:** 2026-10-30  
**HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Existing Draft:** https://github.com/C8LyNn/Model-Test/pull/27  
**Immutable producer heads (read-only):** C01-18 PR #18 `a36b22669526daba76ae0a4147f0a4d2a48e33fc`; C01-17 PR #17 `f6ded93b8f2ac387c056446856fded87853d1f6e`; C01-15 PR #16 `67b6d6f800b417e9d2300bcfdef71c266eb5f23c`.

## Scope and result

C01-03 owns **asset library, source SHA, provenance, intake, version/status discipline and producer/QA/Unity handoff**. We **do not author/overwrite C01-15…19 geometry**, create new asset IDs, alter vessel layouts or merge drafts. Actual source SHA-256 and 3-model P18 OBJ index/topology QA was newly executed. See [machine-readable exact-byte receipt](./PILOT_ACTUAL_SOURCE_SHA256_QA.json). Previously recorded independent C01-02 contact or z-fighting measurements are **not** presented as newly executed tests.

### Fresh source facts (not Blender exports)

| Owner | Existing ID | Source parts / indexed triangle count | Latest source SHA-256 (actual fetched UTF-8 bytes) |
|---|---|---|---|
| C01-18 | P18-01 crate | 41 / 844 | `5fb7ee496d6ed0d2e9f439629b9d9ed4774ca862290f04e13dc70239e44ec39d` |
| C01-18 | P18-02 rack | 51 / 1044 | `37f81ce82235689980e86febdc4ea0f8bbfd5f9296e4462d156295f2c2297699` |
| C01-18 | P18-03 cart | 57 / 1628 | `39aba96fa20eb28f698b68b7daf435e96cabe15c0af2bb70e9db6392e2cd1aa2` |
| C01-17 | P17-01 console GLTF | 18 unique mesh primitives / 25 instances, 380 instanced triangles (previous producer measurement) | `6dbb6933acdcbb3ee5ef9d1480bd786ad2da4ec5368046e8e579084af57c65b0` |
| C01-17 | P17-02 access GLTF | 21 unique meshes / 39 nodes | `a9995704a70776b49f2bd6916a50cf222a4ab40b370a0a9e258b63bdc4429786` |
| C01-17 | P17-03 lever GLTF | 13 unique meshes / 22 nodes | `f38ed83c806b30deb55854b061492a0d89d278f7a7c20f900b2aeaed7933b23d` |
| C01-15 | shared P15 spec 0.1.4 | JSON spec only, not mesh | `7f3d602af1040431134aa4cca236fb36c9613d77160b383f175ec6c02d144703` |

**P18 actual parser checks, re-run at immutable commit:** 149 separate OBJ objects; 2,056 `v`; 8,884 UV entries; 8,884 normal entries; 3,516 fan-triangulated triangles. 0 out-of-range corner indices, 0 degenerate triangles (threshold 1e-12 m²), 0 duplicate indexed triangles, 0 reverse-facing normals, 0 boundary/non-manifold/misoriented edges **within individual authored parts**. This does **not** certify global part-to-part contact, z-fighting, UV overlaps or swept motion.

## 3 reference types per top pilot: observed mechanics, not copied product geometry

Manufacturer/publisher pages were inspected as engineering inspiration **only**. Each external source is third-party copyrighted material; **rights to reuse image/CAD content are not established**. Link/reference only: no external drawings, photos, or product meshes copied into project; independently model generic mechanisms and use original dimensions.

### P18-03 — cargo cart / caster assemblies (C01-18)

1. **Blickle — [basic wheel and caster definitions](https://www.blickle.com/guide/basic-information-definitions)**: distinguish rubber tread, rim, bearing, fork, wheel axle, swivel head and mounting plate. Detail may be added around existing axle/hub assemblies, not as disconnected decoration.
2. **Blickle — [caster fitting types](https://www.blickle.com/guide/fitting-types)**: load-bearing plate must lie against actual frame supporting surface; bolts/holes make the plate interface legible. Test current 4/4 wheel-floor contact and preserve wheel pivots.
3. **Blickle — [bracket types](https://www.blickle.com/guide/bracket-types)**: fork, bearing and protected service hardware; preserve real offset to avoid wheel/post collisions. Check swept/rotated fork and axle motion, not only stationary AABB.

**Producer acceptance:** four caster fork/axle/plate connections actually touch their supports, no wheel↔upright triangle penetration in rest or motion, wheel axis and pivots unchanged, four wheels on floor; caster crown bolts maintain prior wheel clearance.

### P18-02 — industrial rack (C01-18)

1. **IKEA — [BROR shelving construction](https://www.ikea.com/us/en/p/bror-shelving-unit-black-s29619398/)**: powder-coated galvanized steel, shelf/post assemblies and fastening to structure for overturn prevention.
2. **80/20 — [gusseted 90-degree bracket](https://8020.net/4138-black.html)**: real corner reinforcement and multiple fastener locations transfer forces to adjacent profiles; no unattached gussets.
3. **80/20 — [framing fastening methods](https://8020.net/fasteningmethods.html?cat=189&color=15)**: distinguish internal/hidden anchors from external connector plates/corner gussets; add mechanically consistent bolts.

**Producer acceptance:** retain repaired rear crossbar/post support contacts, keep 4 added gussets seated on both members, inspect shelf labels with backing/mounting screws, eliminate coplanar overlaps, do not alter nominal proportions.

### P18-01 — cargo crate / hinges and latch (C01-18)

1. **Southco — [draw latches](https://southco.com/latches/draw-latches)**: keeper must meet latch and actually clamp panels; handle/latch link is mechanically constrained.
2. **Southco — [enclosure hinges and access hardware](https://southco.com/en_gb_int/resources/Adding-Value-To-Heating-Ventilation-And-Air-Conditioning-With-Access-Hardware)**: real hinge support and sealing/contact design, not decorative hinge floating at surface.
3. **80/20 — [mechanical external/internal joints](https://8020.net/fasteningmethods.html?cat=189&color=15)**: fasteners should pass through mating bracket/flange, with sensible support and service access.

**Producer acceptance:** retain prior lower-rim seating and 8 eliminated trim/backer coplanar pairs, pin-keeper collars follow hinge pins, lid movement separate, true triangle contact and latch closure verified.

### P17-01 — console keyboard guides / panel fastening (C01-17)

1. **Accuride — [how to choose a sliding guide](https://help.accuride-europe.com/pl/knowledge/jak-dobra%C4%87-prowadnic%C4%99-do-szuflady)**: side vs flat mounting, permissible slide travel, mounting/clearance and cyclic loading.
2. **80/20 — [serviceable connector types](https://8020.net/fasteningmethods.html?cat=189&color=15)**: physically distinct fastened guide carrier rather than a zero-thickness coplanar overlay.
3. **Southco — [service panel latches](https://southco.com/latches/draw-latches)**: functional keeper/latch relationships for independently movable/serviced panels.

**P0 defect/hold:** Independent C01-02 PASS15 detected `KeyboardGuide_L/R` coplanar same-facing +Z surfaces against `Keyboard`, approx. 0.000190 m² **per guide**. Latest P17-01 glTF was fetched here at commit `f6ded93...` and both named guide nodes remain. This C01-03 pass did **not** run a fresh full triangle clipping test or edit producer geometry. C01-17 must reposition/recess the guide and re-run exact pairwise coplanar test **before acceptance**; preserve P17-02 mount repairs and P17-03 movable `LeverPivot`.

## Mandatory gates and handoff

| Gate | Pass16 status | Required action |
|---|---|---|
| Pilot actual source SHA-256 | **7/7 EXECUTED** | Update pins when any producer file changes |
| P18 OBJ indices, UV0/normal reference consistency, winding and watertight part topology | **3/3 SOURCE PASS** | C01-02 repeat on exact final files |
| Global triangle-triangle contact/self-intersection / coplanar z-fighting | **NOT RUN this pass** | C01-02 independent mesh+assembly QA |
| P17-01 keyboard guide z-fighting | **HOLD** from independent PASS15 | C01-17 correct actual source and re-test |
| Real Blender 4.x new `.blend` save and current binary FBX export + reimport | **NOT RUN** | Producers C01-15…19 on Blender-capable executor |
| New same-angle shaded/wireframe BEFORE/AFTER and closeups | **NOT RUN** | Producers native Blender renders |
| New native Blender/FBX SHA-256 | **NOT AVAILABLE** | Do not substitute source hashes or historical FBX |
| Independent final exact-FBX C01-02 | **BLOCKED** | Hydrate final LFS binary first |
| Real Unity 6 URP importer / pivot / material / wheel motion | **NOT RUN** | C01-10 after binary QA |
| Asset release | **0/36 APPROVED; 36/36 BLOCKED** | C01-00 final review and authorized merge only |

**Execution blocker observed:** local executor has no `blender`, `Unity`, or `git-lfs` and cannot resolve github.com through git CLI, although GitHub connector can fetch/write text files. Earlier Actions attempts reported unallocated jobs; this is a reported symptom, not a proven root cause. **NEEDS_OWNER_ACTION**: run genuine Blender 4.x + Git LFS in available authorized Windows environment or restored Actions runner, then C01-02 and C01-10.

**Ownership handoff**: C01-17 P17-01 geometry defect; C01-18 P18-01/02/03 mechanical source authoring; C01-15/16/19 own source details; C01-02 independent mesh topology/contact/swept QA; C01-10 Unity native import; C01-00 merge/release gate; C01-03 update current source/FBX SHA registry after actual binary artifacts. No source mesh was changed by this document.
