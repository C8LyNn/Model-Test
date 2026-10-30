# C01-02 — DETAIL PASS 15 / independent source QA and native release gate

**Scope:** existing asset IDs only, [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36), [QA Draft PR #13](https://github.com/C8LyNn/Model-Test/pull/13). All producer PRs stay Draft; no merge, ship edits, or producer-owned model modifications by C01-02.

## Actually authored and independently checked PASS15 source changes

| Existing asset | Meaningful added source components | BEFORE → AFTER authoring triangle count | Independent QA | Exact SOURCE SHA-256 |
|---|---|---:|---|---|
| **P18-01** crate | Four hinge retainer collars with true surface intersections with pin, hinge leaf and lid | 37/684 → **41/844** (+160T) | 4/4 new attachment tri contacts; source clean | `5fb7ee496d6ed0d2e9f439629b9d9ed4774ca862290f04e13dc70239e44ec39d` |
| **P18-02** rack | Four mechanical rear-support gussets, attached to upright + rear rail | 47/1012 → **51/1044** (+32T) | 4/4 direct true triangle attachment; source clean | `37f81ce82235689980e86febdc4ea0f8bbfd5f9296e4462d156295f2c2297699` |
| **P18-03** cart | Four inner-fork crown bolts, attached to caster fork and crown; wheels preserved | 53/1532 → **57/1628** (+96T) | 4/4 true triangle attachment; old wheel-vs-upright fix still inherited | `39aba96fa20eb28f698b68b7daf435e96cabe15c0af2bb70e9db6392e2cd1aa2` |
| **P17-01** console | Four screen screws, two keyboard guides, two service latches | 17/204 → **25/380** (+176T) | 8/8 true surface attachment; **P1 same-facing coplanar guide/keyboard FAIL** | `6dbb6933acdcbb3ee5ef9d1480bd786ad2da4ec5368046e8e579084af57c65b0` |
| **P16-04** lighting | Four diffuser retainers | 19/324 → **23/372** (+48T) | 4/4 true triangle contacts to existing Steel/EmissionWhite | `e939e95ebec16e9922e9aac6c4063d765cf7dcd3930e4d9ac54e81d4a29e45d3` *new detail-only OBJ* |
| **P16-05** lighting | Two rear service-cover lips | 15/280 → **17/304** (+24T) | 2/2 true triangle contacts | `aaf082f77f9794f5b4395e66cf88e35a37f55381e731ca51a7db0743eb586ae5` *new detail-only OBJ* |
| **P16-06** lighting | Two static suspension-rod seats | 19/324 → **21/348** (+24T) | 2/2 true triangle contacts, separate original rotor hierarchy untouched | `12438d9684ac0e03e68982d5fe3a11d19e795245532f46d4c737f6a562c68557` *new detail-only OBJ* |
| **P15-01** pipe / installation | 4 steel ties + 4 fastening heads (**parametric specification**, not baked new mesh) | 17 → **25 spec parts**; new triangle count **NOT RUN** | 8/8 parametric AABB supporting contacts, not native mesh QA | `7f3d602af1040431134aa4cca236fb36c9613d77160b383f175ec6c02d144703` *whole geometry_spec v0.1.4* |

**28 real new authoring polygon mesh sub-parts** were independently read from committed OBJ/glTF files, plus **8 authored spec-only** P15-01 functional pieces (no baked topology yet). The three P18 models together have **149 meshes / 3516 triangles**, all 12 new pieces pass independent actual 3D triangle intersection attachment checks. The 7 P16 models now total **108 pieces / 1892 sourced triangles**, including 8 new PASS15 mesh parts verified at actual triangle interfaces. Actual expected aggregate P16 is BASE OBJ + PASS12 detail OBJ + PASS15 detail OBJ; importing only BASE would silently omit detailing.

P18 full static indexed audit on latest source mesh blobs: **0** invalid v/vt/vn corner references, zero-area fan triangles, flipped recorded normals candidates, exact indexed duplicate polygon faces, unexpected boundary/nonmanifold per-part edges, or positively separated whole objects (AABB definite isolation). UV0 values within [0,1] for current P18 authored OBJ. New visual detail usefulness, hidden internal surface area, hardware pivots and Unity LOD/performance are **not yet tested**; no automatic pass from polygon counts.

## Confirmed detail-level P1 and other cautions

**P17-01 — FAIL_SOURCE_COPLANAR:** actual decoded/glTF after applying node scale/translation, KeyboardGuide_L and KeyboardGuide_R have +Z oriented surfaces at **world Z=-0.065m** exactly coplanar with Keyboard, **0.000190 m² (190 mm²) per guide; 0.000380 m² total**, 6 matching triangle pairs each. This is newly introduced by PASS15 and qualifies as an actual source z-fighting risk, regardless of positive guide/Keyboard mechanical intersection. Producer C01-17 should recess or offset shared endcap surface by documented ~1mm while preserving guide support and unchanged console AABB. Independent retest on a NEW glTF SHA required. Old Backbone/Plinth same-facing area ~0.04797m² is inherited, not introduced here; separately assess shader visibility before final.

**P18-03 — REVIEW, not proved z-fighting:** four opposite-facing axle-fastener/fork-outer flush joints remain at exact same plane, 40 triangle-pair hits / total 0.002128896 m². **P18-02** six large old Shelf_Deck/Shelf_Lip opposing-mating planes 0.27876 m² also exist in unchanged old base parts. Opposite normals alone do not demonstrate GPU-flickering with single-sided materials. Validate Blender shaded and double-sided shader settings before treating as defect; don't blindly offset. P18 new detail parts themselves introduce 0 same-facing coplanar overlapped area across all 3 models.

**P15-01 standards caution:** two old CouplerBand0.055/0.945 spec shapes reach nominal Z=0.141m despite asset bound Z=0.140m (+1mm), pre-existing. The eight new P15 parts stay inside nominal envelope. C01-01 decides tolerance, not auto-source rewrite.

**P17-02:** 38 mesh-instance/536T authoring glTF preserved. Four correct 9×9×3mm screws contact backing; old Housing/Keybed gap repaired 0.5mm seating. Offline binary patched candidate exists but is **NOT Blender-exported** and not a native sign-off.

## Preview evidence — original polygon geometry, NOT Blender screenshots

- [P17-01 BEFORE/AFTER shaded + wireframe](Previews/P17-01_GLTF_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg) — actual decoded original/current glTF triangles, identical camera, gold = 8 new source parts. This is not a Blender screenshot.
- [P18-01/02/03 shaded + wireframe detail overview](Previews/P18_THREE_SOURCE_MODELS_SHADED_WIREFRAME.svg) — actual authored OBJ polygons, gold = newly added mechanical parts. This is not a Blender screenshot.

## Native exporter, Unity and global 36-model release gate

Canonical LFS pointers for P17-01, P17-02 and P18-01/02/03 **remain original pre-detail FBX binary SHA**, e.g. P17-01 `fca67dad3e35e7070575c7d7d141fab3e6756eecb0d618d325ec36266eca2772`, P18-01 `84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939`, P18-02 `5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f`, P18-03 `639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19c5e165`. These fingerprints **do not correspond to the current new details**.

**Blender 4.x app locally:** absent. **New native .blend saved via Blender:** NOT RUN. **New Blender-origin binary .fbx and roundtrip:** NOT RUN. **Actual shaded/wireframe rendered in Blender:** NOT RUN. **Unity 6 URP FBX import and animated prefab QA:** NOT RUN. Checked current C01 Actions run `41131027711` job `native-blender-roundtrip` failed with **0 executed steps**, runner allocation unresolved; do not assume a specific billing root cause. **Independent final binary acceptance remains 0/36.**

**Handoff:** C01-17 correct the two P17-01 KeyboardGuide coplanars; all owners export exactly current pinned source data through Blender 4.x, save true .blend and Blender-origin .fbx, hash source+native+FBX and reimport on host with Git LFS. C01-02 recomputes independent native topology/coplanars, mesh UV/material/pivots/animation checks and full 36; C01-10 performs Unity6 URP prefab import and runtime clearance. **NEEDS_OWNER_ACTION** if no authorized Windows Blender4 host or working GitHub Actions allocation. No asset completed/merged without actual evidence.

[Machine-readable actual independent QA](INDEPENDENT_DETAIL_MESH_QA.json) · [36-model final gate](36_MODELS_DETAIL15.csv).
