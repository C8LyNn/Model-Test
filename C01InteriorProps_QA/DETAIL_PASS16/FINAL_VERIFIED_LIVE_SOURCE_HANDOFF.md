# C01-02 — DETAIL PASS16 — FINAL LIVE SOURCE RECHECK (2026-10-30)

**Status:** Actual producer source mesh improvements independently confirmed on GitHub at immutable file Git blobs; native Blender/FBX/Unity still blocked. This note **SUPERSEDES** the earlier first-pass P17-01 P0 HOLD in `PASS16_INDEPENDENT_MESH_REFERENCE_QA.json` and the earlier first-pass `HANDOFF_REFERENCE_DRIVEN_INDEPENDENT_QA.md`. Newer commits landed during the audit.

## R0 — real source repair P17-01

Producer changed the **REAL authored glTF** `Assets/C01InteriorProps/Models/P17-01.gltf`:
- **before:** git blob `c604553c874b590cfd5fcae135f4c892561eba96`, SHA-256 `6dbb6933acdcbb3ee5ef9d1480bd786ad2da4ec5368046e8e579084af57c65b0`; `KeyboardGuide_L` and `KeyboardGuide_R` both Z=-0.170m node translation;
- **after:** git blob `e0df06d260a955fe926f7e0279068bf2a2e6a6b5`, SHA-256 **`77bffeffd7440c40882945e7341f659be2035eb23e67dae6329d108c74c88980`**, both node positions Z=-0.169m (+1.0mm).
- Independent **true after source narrowphase**: KeyboardGuide_L↔Keyboard **15** indexed triangle-pair crossing hits and same-facing coplanar **0mm²**; KeyboardGuide_R↔Keyboard **13** hits, coplanar **0mm²**. Previously 190mm² EACH same-facing overlapped. New 25 part mesh / 380 triangles has zero area-degenerate faces, no normal misorientation and valid all UV0.
- Independent actual `C01InteriorProps_Source/MeshText/P17-01.obj.txt` vs glTF geometry per *each of the 25 mesh names*: **380 of 380 triangles exact multiset parity with 0.01mm rounding tolerance**. OBJ current blob `8d6f6ccbc53ea42d3b2d8f0e423072b10a388f52`.
- **Verdict:** P17-01 P0 source mechanical/coplanar fix PASS. This is NOT a native Blender .blend/.fbx or Unity prefab signoff.
- [Actual before/after source glTF shaded + wireframe](Previews/P17-01_REAL_SOURCE_P0_BEFORE_AFTER_SHADED_WIREFRAME.svg) — analytic SVG from real triangles, **NOT Blender-rendered**.

## R1 — three more real detailed P18 authored assets

Producer added exactly **10 source OBJ mesh parts** (+248 triangles) to existing three IDs. Old 149 source object meshes retained with exact original per-object vertex and face content (149/149 byte-semantic match); no regression to PASS14 or PASS15 existing parts.

| Existing asset | Before PASS16 → current real source | Actual NEW detail components | Narrow-phase new part support | SHA-256 current exact SOURCE OBJ |
|---|---|---|---|---|
| **P18-01** crate | 41/844T → **43/868T** | 2 upper lid latch keepers | each keeper↔front lever **16** triangle pair contacts, keeper↔lid **8** | `a3f05396b78419f39e30f78eabecb1e39eb0403b171be945621329a311df0858` |
| **P18-02** rack | 51/1044T → **55/1172T** | 4 gusset screws for rear rails | each screw↔gusset **32** pairs; also genuine rear rail/post contacts, counts at least **13** per post where present | `edceacf8b3494da686186632b27c6a0885f95f401e9598830c7be33927eeff0b` |
| **P18-03** cart | 57/1628T → **61/1724T** | 4 caster anchor retainers | 4/4 retainer↔anchor strict triangle crossing contacts: **14/12/12/14** | `a67e5d708538f738bc6363ffe14a177217b506bfbbab8224f420b063ef09f1aa` |

**Current complete P18: 159 separate meshes, 3764 fan-triangulated triangles; 10/10 new functionally attached actual source triangle checks PASS.** Across all 3: independently 0 invalid vertex/UV0/normal corner indices, zero-area triangles, duplicate source polygons, face normal reversal, boundary/non-manifold edges. Same-facing cross-part exact planar triangle overlap area **0m²** in current 3 models (independent polygon clipping). Pre-existing **opposite-facing internal mating planes** still exist: P18-02 18 triangle pair hits / 0.27876m² (deck↔lip), P18-03 40 hits / 0.002128896m² (axle fastener↔fork outer); not demonstrated actual GPU-flicker and requires native material review. Rendered-pixel LOD/performance, movement sweeps and 3D full-scene BVH for ALL old parts are NOT RUN.

Source git blobs:
- P18-01 `dc1ad53e6651a091f9bb193b9baed568a3a7aa60`;
- P18-02 `f6ba1600294380416b567b443e328adccc29c270`;
- P18-03 `259d3687a7968172f275410cf49e9d66d479c8ca`.
Source baseline previous P18 producer HEAD `a36b22669526daba76ae0a4147f0a4d2a48e33fc`; after geometry pinned at `f0edf20df4fc760ad6ca8f6edd38268b9a408165`.

**Actual old/new source OBJ technical shaded+wireframe**:
- [P18-01 crate](Previews/P18-01_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg)
- [P18-02 rack](Previews/P18-02_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg)
- [P18-03 caster cart](Previews/P18-03_REAL_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg)

These are **genuinely derived from committed authored indexed OBJ triangles** with identical camera and scale, **not Blender screenshots**.

## R2 — other assets, references, original hierarchy

- **P17-03** exact real glTF blob `e882a5dafe3f9f5e600d6443ebf44b1aba519f30`, source SHA-256 `f38ed83c806b30deb55854b061492a0d89d278f7a7c20f900b2aeaed7933b23d`: 20 meshes / 424T, 0 zero-area/normals/UV issues; all 8 added functional mounting parts have actual 3D triangle contact. Existing LeverPivot translation [0,0.35,-0.015], children LeverShaft, LeverGrip, PivotAnchorVisual unchanged; **actual Blender/Unity motion NOT RUN**.
- P16-04/05/06 PASS15 8/8 true source attachment retained at last verified source pins; P15-01 8/8 specification-only source parametric supports, not baked/exported; P19 newest physical offline P19-01 candidate only producer report in HQ, not independent physical native file QA.
- **12 verified original manufacturer reference sources**, mapped as >=3 sources per key package C01-15/16/17/18/19, documented in [references catalog](References/VERIFIED_CONSTRUCTION_SOURCES.md). Covers Colson/Fallshaw caster anatomy, Southco hinges/latches, Bosch/80-20 structural connectors, Rittal enclosures, Arlico/Karl Dose/AWEX lights, Uline workbench frame. Design principles only; no proprietary photo/CAD copied or product cloned.

## R3 — hard native release blockers, no fiction

On last checked current producer branches, **Git LFS canonical FBX pointers still ORIGINAL pre-detail SHA**: P17-01 `fca67dad3e35e7070575c7d7d141fab3e6756eecb0d618d325ec36266eca2772`, P17-02 `af858385a0abae9c623ee4002bcf22bcbc401b5687024acd8df142eb1b848147`, P18-01 `84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939`, P18-02 `5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f`, P18-03 `639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19e165`. **No new canonical native Blender FBX** exists on those examined source commits.

Independent runtime check: `blender`, `bpy`, Unity6 **ABSENT**. GitHub Actions latest inspected run `41138214564` named `blender-export` and producer run `41137690882` FAILED before steps; **0 executed steps**, precise runner cause unresolved. Do not claim an actual Blender export or SHA of one. **Real Blender .blend save/FBX export-reimport/wireframe renderer = NOT RUN; Unity6 URP prefab/animation = NOT RUN. Global approved 36 final binaries: 0/36.**

**Next gate:** C01-17/C01-18 producers now have source-level PASS for corrections and new functional details, but must save actual scene via Blender 4.x, export real native FBX, publish SHA of hydrated bytes, capture Blender shaded/wireframe BEFORE/AFTER and test in Blender reimport. C01-02 independently tests exported file and Unity C01-10 imports/pivots. Do not merge any producer PR without owner approval and verified QA.

[Current machine QA, superseding earlier snapshot](PASS16_LIVE_SOURCE_RECHECK_FINAL.json) · [36 model release matrix](36_MODELS_DETAIL16.csv).
