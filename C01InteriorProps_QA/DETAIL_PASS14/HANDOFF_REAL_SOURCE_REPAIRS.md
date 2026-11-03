# C01-02 — DETAIL PASS14 / Independent mechanical source QA

**Review date:** 2026-10-30. **Work item:** [#36](https://github.com/C8LyNn/Model-Test/issues/36). **QA ownership:** [Draft PR #13](https://github.com/C8LyNn/Model-Test/pull/13), source changes owned by **C01-18 PR #18**. **Pinned producer source commit:** `996b8e8f8deb86e2a59f1468fb8b318a7815cfa7`.

## Genuine authored geometry changes verified

| Existing model | BEFORE genuine source defect | AFTER actual repaired OBJ proof | SHA-256 of current **SOURCE OBJ bytes** | Source gate |
|---|---|---|---|---|
| P18-01 crate | 8 same-facing coplanar Trim/TrimBacker face pairs, 48 overlapping triangle pairs, 0.002496 m²; Lower_Rim 10 mm detached | **0** overlapping face pairs / 0 m²; Lower_Rim 2 mm penetration into Crate_Shell, original floor Y=0 retained. 68 source vertices updated; 416 V / 684 T / 37 parts unchanged | `6d1cbedba52d975594c4d1c4c1addcf14f752ee7118a521a3e63c880e8044b06` | PASS scoped source |
| P18-02 rack | 2 Back_Support bars 30 mm short from posts on each side | Both bars X extent ±0.985 m, 5 mm **solid overlap** into both side posts each (4 ends); 16 vertices changed; 600 V / 1012 T / 47 parts unchanged | `dc9434a32b7de2235d80a374cc04778b657e39c8f98d88b288bdad40fbf6af2c` | PASS scoped source |
| P18-03 cargo cart | 4 shelf lips 5 mm detached, **48** wheel/Upright intersecting original triangle pairs (11/11/13/13) | Four lips seated **2 mm into shelves** (40 intersecting lip/deck triangle pairs), wheel/Upright **0** intersections; all wheel tops Y=.210, Upright bottoms Y=.212 (2 mm clearance), **4/4 wheels ground Y=0** and anchors still intersect four uprights (16/20/16/20 triangle pairs). 48 source positions changed; 872 V / 1532 T / 53 parts unchanged | `22513002afb38d2d3f4a13ef429a41c9a04928528b3cffef87613d51351c1901` | PASS scoped source |

**Note on methodology:** source OBJ is triangulated and checked against actual vertex positions; same-facing coplanar face pairs are tested using oriented plane grouping and true 2D convex polygon clipping; wheel/upright actual narrow-phase counts rely on 3D segment–triangle crossings with per-triangle AABB prefilter; 0 intersections does not mean the surfaces are guaranteed invisible in every native Blender/Unity configuration. Wheel pivot simulation and noncoplanar contact for all other part pairs are NOT RUN.

For all **3 current new OBJ** (137 authored components / 3,228 triangulated triangles), independent parsed tests find **0** invalid vertex/UV0/normal indices, **0** zero-area fan triangles, **0** flipped normal-vs-face candidates, **0** duplicated indexed faces, **0** anomalous open / nonmanifold component edges, and **0** same-facing cross-part coplanar overlap candidates (area tolerance > 1e-8 m²). Source face arrays / UV0 corner streams / normal arrays / material assignments have not changed in this corrective wave.

**New matching SHA-256 is a SOURCE checksum, NOT a newly exported FBX fingerprint.** Git blob identifiers: P18-01 `051ab09222a354f1c64f7c682442529b6f4d54ee`, P18-02 `349fd2307eca8d2334cb8c8cbeb5f43ff9408d4b`, P18-03 `e6440810d917df3c978505ce79f084ba1f98086c`. Physical SHA-256 independently calculated from GitHub-returned exact OBJ text; SHA-256 test vector `abc` PASS.

P17-02 remains **PASS source-level transformed glTF mechanical supports** as verified PASS13: four actual 9×9×3 mm screws embedded 0.5 mm into MountBacking, Keybed↔Housing repaired positive 0.5 mm seating. The old 2 m or detached-screw claims have been explicitly retracted. Existing PR #17 `cdcc18428d2fb52c2c60826fc8af9a70f51c82f9` contains current glTF blob `d80a67af140e434b983104aaec0078f9cf5bd66f`.

## Real geometric BEFORE/AFTER technical previews

All are generated **directly from actual current/previous OBJ polygon meshes**, same project-space camera and scaling, correction components highlighted. These are valid source-space technical previews, **NOT rendered in Blender** and not substitutes for Blender wireframe + material/shader screenshots:

- [P18-01 crate before / after](Previews/P18-01_SOURCE_BEFORE_AFTER.svg)
- [P18-02 rack before / after](Previews/P18-02_SOURCE_BEFORE_AFTER.svg)
- [P18-03 cart before / after](Previews/P18-03_SOURCE_BEFORE_AFTER.svg)

## Critical unavailable runtime and release gates

- Blender 4.x app and `bpy`: **NOT AVAILABLE** locally, so genuine newly saved `.blend` after corrections **0**.
- New Blender-origin FBX 7400 export and real Blender save→FBX→reimport: **NOT RUN**, 0.
- Current producer LFS FBX P17-02 `af858385a0abae9c623ee4002bcf22bcbc401b5687024acd8df142eb1b848147`, P18-01 `84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939`, P18-02 `5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f`, P18-03 `639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19e165` are still **original pre-detail sources** (old SHA, not after the actual repairs).
- Current C01 Actions run `41124421941` (`check-manifest`) failed **before any step**, `steps=[]`, no runner assigned. Actual administrative root cause not determined; no unapproved billing/permissions change or blind reruns.
- Unity 6 URP FBX real import, prefab collider/pivot/rotating wheel behavior: **NOT RUN**.
- **Final 36-model independent binary release APPROVED: 0/36.** P16 final native seven pairs, P15 original hydrated seven and P19 true Blender exporter/native issue remain separately open. No artist repo source files altered by QA; all PRs remain Draft/unmerged.

**Owner handoff:** C01-18 should run actual Blender4 on exactly these 3 source blobs (save revised .blend, re-export genuine binary FBX, reimport, confirm UV0/materials/world space and wheel pivot parenting, supply actual Blender before/after), C01-02 independently validate actual byte SHA and geometry, then C01-10 Unity6 build+prefabs. `NEEDS_OWNER_ACTION` for C01 Actions runner or authorized Windows Blender host. No new asset ID, ship edit, unauthorized welding or merge.

Source machine evidence: [INDEPENDENT_MECHANICAL_REPAIR_QA.json](INDEPENDENT_MECHANICAL_REPAIR_QA.json); 36-model release gate: [36_MODELS_DETAIL14.csv](36_MODELS_DETAIL14.csv).
