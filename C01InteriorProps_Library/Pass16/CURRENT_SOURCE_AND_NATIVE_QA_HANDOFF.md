# C01-03 — DETAIL PASS16 / CURRENT source registry and release-gate handoff

**Date:** 2026-10-30 · **HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Owner:** C01-03 ASSET LIBRARY · **Draft PR:** https://github.com/C8LyNn/Model-Test/pull/27  
**Supersedes:** the earlier C01-03 PASS16 pilot snapshot and initial `REFERENCES_QA_HANDOFF.md` where P17-01 was still marked unresolved. Those are valid *historical pinned observations*, not the present source-level acceptance decision.

## Work actually executed by C01-03

- Independently re-fetched and **calculated exact UTF-8 authoring SHA-256 for 10 current source files** at pinned PR #16/#17/#18/#28 producer commits. Verified SHA algorithm against standard empty/abc vectors. Git blob SHA-1 and exact original source SHA-256 are stored in [LIVE_ASSET_REGISTRY_36.json](./LIVE_ASSET_REGISTRY_36.json).
- Indexed **36 unmodified asset identities**, owners and native release gates; **22/22 registry/references assertions PASS** ([validation](./VALIDATION_CURRENT_22.json)).
- Cross-indexed **23 producer-documented source URLs** from **five official-source research files**, each package 4–5 references, in [REFERENCE_LIBRARY_23.json](./REFERENCE_LIBRARY_23.json). Spot-checked four official pages externally (Uline, Southco, Rockwell, Rejs); remaining links are producer-documented, not each independently re-verified by C01-03.
- Read independent [C01-02 final live PASS16 QA](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS16/PASS16_LIVE_SOURCE_RECHECK_FINAL.json), immutable Git blob `7cf6b5de21fb79a292c88febb8eeccf40a6180a6`; distinguishes **scoped source acceptance** from native .blend/.fbx approval. C01-03 did **not edit any producer source meshes**.
- Checked three recent Actions job executions: [41138429511](https://github.com/C8LyNn/Model-Test/actions/runs/41138429511), [41138214564](https://github.com/C8LyNn/Model-Test/actions/runs/41138214564), [41137473086](https://github.com/C8LyNn/Model-Test/actions/runs/41137473086): each failed with no assigned runner and **0 steps**, so no Blender/Unity or CI PASS can be inferred. Runner cause unknown.

## Current exact authoring source evidence — not final Blender FBX SHA

| Owner / ID | Latest actual SOURCE SHA-256 | Reality / scoped source QA |
|---|---|---|
| C01-15 P15-02 | Shared P15 `geometry_spec.json` **v0.1.5**: `f569f1272873e4350c12fd8061e23ad5dcb2d90fd533d00319dfca80e207e434` | 30 parametric grille parts; producer reports 32/32 targeted real triangle support pairs and 4 old coplanar pairs→0 in offline reconstructed mesh. **No native bake** |
| C01-16 P16-04 | Additive `P16-04_detail16.obj` `220cdcbe31d7437e9b99b3a56fd24a4caff887aaab23fd2e75dfd4539503e2cd` | 4 structural clip bolt heads, +80 source triangles, producer source-QA only |
| C01-16 P16-05 | Additive `P16-05_detail16.obj` `de9a3df21dfed8cd94a66d06520dd188aadb0b306f623d3fe1a7b6edab5e63f1` | 2 service-cover heads, +40 source triangles |
| C01-16 P16-06 | Additive `P16-06_detail16.obj` `ae94bc41df6cca17d95c5b21f8ae76457b63f695f5d94816eb3efd98dc269581` | 2 static suspension-seat screws, +40 source triangles; moving rotor must remain separate |
| C01-17 P17-01 | `77bffeffd7440c40882945e7341f659be2035eb23e67dae6329d108c74c88980` | **P0 source guide defect corrected**, per independent C01-02 each previous 190mm² KeyboardGuide/Keyboard overlap→0. 25 mesh parts, 380 instanced triangles. Separate Backbone/Plinth internal material visibility review still required |
| C01-17 P17-02 | `a9995704a70776b49f2bd6916a50cf222a4ab40b370a0a9e258b63bdc4429786` | 536 instanced triangles, source unchanged; previous correctly mounted screws maintained, not native final |
| C01-17 P17-03 | `f38ed83c806b30deb55854b061492a0d89d278f7a7c20f900b2aeaed7933b23d` | 424 instanced triangles, independent source 8/8 fixture contacts; LeverPivot and three moving children retained, swept Unity test NOT_RUN |
| C01-18 P18-01 | `a3f05396b78419f39e30f78eabecb1e39eb0403b171be945621329a311df0858` | Crate now 43 parts/868T; two new upper latch keepers physically contacting lid and levers |
| C01-18 P18-02 | `edceacf8b3494da686186632b27c6a0885f95f401e9598830c7be33927eeff0b` | Rack 55 parts/1172T; four back-brace gusset fasteners; same-facing overlap 0. **18 opposite-facing existing internal pairs** need native materials/culling check |
| C01-18 P18-03 | `a67e5d708538f738bc6363ffe14a177217b506bfbbab8224f420b063ef09f1aa` | Cart 61 parts/1724T; four stationary caster-anchor retainers. Wheel pivots/4-wheel contact and swept movement must be rechecked in Unity. **40 existing opposite-facing internal pairs** need visual review |

**C01-18 totals:** 159 source parts / 3764 indexed triangles. Independent C01-02 source reports old 149 authored parts unchanged, **10/10 new positive triangle mechanical mount contacts** and zero same-facing source coplanarity. Opposite-facing internal meeting planes **are not automatic visual z-fighting**; verify actual rendered surface visibility, back-face culling and materials before removing anything. No blanket weld or triangle dissolves.

**C01-19 P19-01:** producer provided an *offline* modified Blender-format/FBX-format candidate with 4 gussets+4 bolts, reported 358→470 triangles and analytic contacts. Binaries are **not hydrated in current producer Git LFS** and were **not saved/exported by the Blender application in this wave**; keep `CANDIDATE_ONLY`. **P19-07 inherited geometric vertex-on-edge candidates = visual HOLD** until inspected, not automatic T-junction FAIL.

## Original manufacturer reference document pointers (no product copying)

| Producer | Manufacturer links recorded | Construction purpose | Source document |
|---|---:|---|---|
| [C01-15](https://github.com/C8LyNn/Model-Test/pull/16) | 4 | Grille blade support, clamps and enclosure hinges | [P15 references](https://github.com/C8LyNn/Model-Test/blob/c01/props-15-installations/Assets/C01InteriorProps/P15/References/DETAIL_PASS16_CONSTRUCTION_REFERENCES.md) |
| [C01-16](https://github.com/C8LyNn/Model-Test/pull/28) | 5 | Cable glands, diffuser fasteners, independent rotor mounting | [P16 references](https://github.com/C8LyNn/Model-Test/blob/c01/props-16-lighting-wave02/C01Source/LightingW02/References/DETAIL_PASS16_CONSTRUCTION_SOURCES.md) |
| [C01-17](https://github.com/C8LyNn/Model-Test/pull/17) | 4 | HMI panel retainers, guide clearance, moving control mount | [P17 references](https://github.com/C8LyNn/Model-Test/blob/c01/props-17-controls/C01InteriorProps_Source/References/PASS16_C01-17_CONSTRUCTION_REFERENCES.md) |
| [C01-18](https://github.com/C8LyNn/Model-Test/pull/18) | 5 | Caster forks/plate/axle, racking and latch keepers | [P18 references](https://github.com/C8LyNn/Model-Test/blob/c01/props-18-cargo/Assets/C01InteriorProps/C01-18/References/DETAIL_PASS16_CARGO_REFERENCES.md) |
| [C01-19](https://github.com/C8LyNn/Model-Test/pull/15) | 5 | Bolted workbench frame, gussets, locker hinges, bench feet | [P19 references](https://github.com/C8LyNn/Model-Test/blob/c01/props-19-furniture/Assets/C01InteriorProps/C01-19/References/PASS16_MECHANICAL_CONSTRUCTION_REFERENCES.md) |

All references are **URLs + own functional abstraction only**. No vendor CAD, images, textures, logos, or product dimensions copied into C01 geometry or the asset-library registry. Their copyright/licensing is not implicitly granted.

## Before/after preview evidence: available but NOT Blender renders

C01-02 created analytic source-mesh shaded/wireframe SVG at consistent viewpoint: [P17-01](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS16/Previews/P17-01_REAL_SOURCE_P0_BEFORE_AFTER_SHADED_WIREFRAME.svg), [P18-01](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS16/Previews/P18-01_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg), [P18-02](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS16/Previews/P18-02_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg), [P18-03](https://github.com/C8LyNn/Model-Test/blob/c01/props-02-independent-qa/C01InteriorProps_QA/DETAIL_PASS16/Previews/P18-03_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg). These are genuine *source-derived drawings*, not screenshots generated by Blender Workbench. Producer offline previews likewise do not prove Blender execution.

## Native source→export→QA→Unity release order

1. **C01-15…19 producers:** on an authorized executor with Blender 4.x and Git LFS, open the actual current source, save real new `.blend`, export binary `.fbx` using Blender's exporter, reimport FBX, retain pivots/UV0/hard normals/materials, capture genuine same-camera Blender shaded/wireframe BEFORE/AFTER plus closeups, compute exact SHA-256 for hydrated artifacts. No new model IDs, no ship geometry changes.
2. **C01-01 and independent C01-02:** pin exact new FBX SHA and source commit, verify proper attachment with triangle testing, face normals, 0 unintended coplanar overlaps, UV0 and materials, continuous movement clearances and documented opposite-facing internal material visibility. P19-07 visual HOLD must be explicitly resolved.
3. **C01-10:** run actual Unity 6000.3.14f1 URP import/serialization, unit scale, prefab hierarchy, emission/material slots, appropriate colliders, movable wheel/lever/lid sweeps, memory and performance checks. Do not change ship architecture.
4. **C01-03:** only after authentic deliverables update canonical manifest native .blend/FBX SHA-256 and approvals; retain original history and distinguish old LFS binary hashes from current exporter bytes.
5. **C01-00:** explicitly authorize any integration/merge after gates are satisfied.

### Gate at this pinned snapshot

| Gate | Result |
|---|---|
| Authoring-source exact SHA-256, refreshed this turn | **10/10 PASS** |
| C01-03 metadata/reference integrity | **22/22 PASS** |
| Producer reference pages indexed | **23 references across 5 groups** |
| C01-02 P17-01 keyboard guide source correction | **PASS scoped source** |
| C01-02 P18 10 new physical support contacts | **PASS scoped source** |
| Native Blender 4 .blend save and Blender-exported FBX + reimport | **NOT_RUN** |
| Blender-produced shaded/wireframe of final assets | **NOT_RUN** |
| Final independent C01-02 **native exact-FBX** approval | **BLOCKED / 0 of 36** |
| Real Unity 6 URP prefab/animation import | **NOT_RUN** |
| Formal release / merge | **BLOCKED 36 of 36 / NO MERGE** |

**NEEDS_OWNER_ACTION** — running Blender 4.x + Git LFS and Unity on authorized Windows host or restoring eligible GitHub Actions runner. Three checked job failures had `runner_id=null` and `steps=0`; exact root cause cannot be confirmed from those failures alone. No spending, permission change, merge or producer mesh changes performed by C01-03.
