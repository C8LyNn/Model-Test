# C01-02 — DETAIL PASS 16 / Independent QA + construction reference handoff

**HQ:** [#36](https://github.com/C8LyNn/Model-Test/issues/36) · **Owner:** [QA Draft PR #13](https://github.com/C8LyNn/Model-Test/pull/13) · **Status:** Source quality checked where actual current producer bytes exist; **no native-release approval**.

## Original sourced construction references

Completed a substantive [12-source construction reference library](References/VERIFIED_CONSTRUCTION_SOURCES.md) with **at least three references mapped to the critical existing assets for each producer package C01-15/16/17/18/19**. Sources: Colson and Fallshaw industrial caster anatomy, Southco removable hinges and draw-latches, 80/20 gusset and Bosch profile connectors, Rittal enclosure mounting, Karl Dose/Arlico/AWEX industrial luminaires, Uline steel workbenches. References have real manufacturer URLs, explicit mechanism and checkable target mesh interfaces. All original manufacturer intellectual property remains with rights holders; **NO product reference photos/CAD copied** into repository and NO 1:1 replica. Correct producer next-step: cite specific R01…R12 source ID on each new structural detail and document purpose, assembly direction, material, fasteners, clearances and moving/static classification.

## Confirmed P0 source defect and validated VIRTUAL repair — P17-01

Original actual producer [P17-01.gltf](https://github.com/C8LyNn/Model-Test/blob/c01/props-17-controls/Assets/C01InteriorProps/Models/P17-01.gltf) Git blob `c604553c874b590cfd5fcae135f4c892561eba96`; original exact physical SHA-256 `6dbb6933acdcbb3ee5ef9d1480bd786ad2da4ec5368046e8e579084af57c65b0`. It **still** contains P17-01 KeyboardGuide_L/R +Z same-facing surface coincident with Keyboard at Z=-0.065m, **190 mm² each**, **380 mm² total**. This is a source depth-fighting risk, NOT safe to release.

**Actually executed independent simulation**, decoding real glTF float32 buffers and applying node transforms, with **same-facing triangle polygon clipping** and **3D triangle edge vs triangle narrowphase** for intended supports:

| World Z translation applied to BOTH guides (virtual, NOT committed producer mesh) | Left Keyboard 3D intersection pairs | Right pairs | Left/Right coplanar same-facing areas |
|---|---:|---:|---:|
| 0 mm (current source) | 15 | 15 | 190 / 190 mm² |
| **+0.5 mm (proposed)** | **15** | **13** | **0 / 0 mm²** |
| +1.0 mm | 15 | 13 | 0 / 0 mm² |
| −1.0 mm | 13 | 15 | 0 / 0 mm² |

The small proposed **+0.5mm** offset is the least disruptive candidate verified numerically for these particular two surface supports. Source author C01-17 must actually modify BOTH **glTF node translations AND matching OBJ/spec source**, retain original total bounds, verify all other part intersections/visibility, and publish a *new immutable source SHA*; repeat C01-02 independent source audit **before** any native export. A virtual patch is NOT an actual repair. Original hidden Backbone/Plinth overlap (~0.04797m²) should receive material/visibility review separately; unrelated old source geometry should not be blindly welded.

## Independent actual P17-03 lever mesh QA

Decoded current real [P17-03 glTF](https://github.com/C8LyNn/Model-Test/blob/c01/props-17-controls/Assets/C01InteriorProps/Models/P17-03.gltf) Git blob `e882a5dafe3f9f5e600d6443ebf44b1aba519f30`, exact SHA-256 `f38ed83c806b30deb55854b061492a0d89d278f7a7c20f900b2aeaed7933b23d` (independent JS SHA256 standard test `abc` PASS). Real decoded source = **20 mesh instances, 424 triangles**; zero invalid triangle indices, zero degenerate triangles, zero flipped normals, **20/20 valid UV0**. All **8 new functional fasteners/retainers have real 3D source surface intersections**: four front panel bolts 16,16,16,18 pair hits; two socket ribs 10,10; two cover bolts 12,12. glTF node hierarchy remains: root→LeverPivot with **LeverShaft, LeverGrip, PivotAnchorVisual** as children; exact pivot translation [0,0.35,-0.015]m. **Animation swing and physical collision tests in Unity/Blender NOT RUN**.

## Other source QA carried forward, no invented producer enhancements

C01-18 P18-01/02/03 last pinned current source blobs unchanged at time of PASS16 scan:
- P18-01 `732a23a5c1c18fc39fb2e257e4de8c0a558c5e5f`, 41 parts / 844 T, hinge pin retainer true contact from PASS15. SHA-256 `5fb7ee496d6ed0d2e9f439629b9d9ed4774ca862290f04e13dc70239e44ec39d`.
- P18-02 `26894eb7c5fbbd1c25239905fc3ba228f9925a15`, 51 parts / 1044 T, gussets meet rails+posts. SHA-256 `37f81ce82235689980e86febdc4ea0f8bbfd5f9296e4462d156295f2c2297699`.
- P18-03 `e1e1b3444d00ff5ba0ba205ad1291e5968688f6e`, 57 parts / 1628 T, wheel crown bolts real attached, previous wheel/rim PASS14 fixes preserved. SHA-256 `39aba96fa20eb28f698b68b7daf435e96cabe15c0af2bb70e9db6392e2cd1aa2`.
Existing 3-model P18 source total **149 parts / 3516 triangles**, PASS15 12/12 new joints actual triangle intersections, 0 indexed degeneration or same-facing cross-mesh coplanar; this is a **carried-forward pinned result**, not new PASS16 detailed geometry edits. Engineering reference criteria new to PASS16 are available in the reference catalog. All native/pivot tests still needed.

C01-16 P16-04/05/06 last independent source PASS15 8/8 real structural contact and 8 new source meshes 96T; seven original light fixtures require combining BASE+PASS12+PASS15 before real native export. C01-15 P15-01 +8 spec-only steel ties/screws with AABB positive support PASS15 but 3D authoring export remains unverified. C01-19 P19-01 producer reported offline binary model candidate in HQ; **not independent audited here without its physical bytes**, and not Blender-origin proof. Do not promote.

## True files and shaded/wireframe provenance

Original [PASS15 P17-01 actual-source shaded/wireframe](../DETAIL_PASS15/Previews/P17-01_GLTF_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg) and [PASS15 P18 3-model source shaded/wireframe](../DETAIL_PASS15/Previews/P18_THREE_SOURCE_MODELS_SHADED_WIREFRAME.svg) exist in QA PR #13. They show real source geometry before/after PASS15 and are *not* new PASS16 Blender renders. P17-01 PASS16 guide fix is **numeric simulation only**, with no actual AFTER mesh available yet. Avoid claiming a post-fix render or native binary.

Canonical native FBX LFS fingerprints remain original **pre-detail**: P17-01 `fca67dad3e35e7070575c7d7d141fab3e6756eecb0d618d325ec36266eca2772`, P18-01 `84851387b58aeadc7f2ace49201077d847cfd294f82acfb2d0a7dce3e471a939`, P18-02 `5ba3faf85a3ea57f755eeb51d0db832c1ce37aa64721d710a22db509f2c6d03f`, P18-03 `639fc09c39b804b9bf83de75a4096cdefe1229f58549662ee777537c19e165`.

**Blender 4.x executable:** ABSENT. **bpy:** ABSENT. **Unity6:** ABSENT. **Blender real .blend-save:** NOT RUN. **Blender genuine FBX export→reimport:** NOT RUN. **Actual Blender shaded/wireframe:** NOT RUN. **Unity 6 URP scene/prefab/animation tests:** NOT RUN. Latest inspected Actions run(s) failed with no executed steps, runner provisioning root-cause unresolved. **36-model independent FINAL approval: 0/36 — RELEASE HOLD.**

## Mandatory owner handoff

C01-17 repair glTF+OBJ P17-01 two same-facing guide caps (virtual best +0.5mm), publish new source SHA, rerun actual P17-01 guide/Keyboard and all other screen/closure joints; preserve P17-03 pivot parenting. C01-18 add next only reference-driven functional details after clear evidence of need (e.g. actual axle bearing, fastener access), preserve 4-wheel tire/post clearances and tray lip seats, test wheel rotation sweep. C01-15/16/19 cite exact reference, prove positive component support and preserve cabinet door/rotor motion. C01-00 fix runner or use approved Windows Blender 4.x + Git LFS host; C01-10 use real reimported Blender FBX and test Unity6 URP prefab pivots/sweeps. C01-02 independently verifies native bytes and topology before accepting any of the 36. **No unauthorized merge, new asset ID, ship change or reference copying.**

Machine-readable receipt: [PASS16_INDEPENDENT_MESH_REFERENCE_QA.json](PASS16_INDEPENDENT_MESH_REFERENCE_QA.json); 36 model matrix: [36_MODELS_DETAIL16.csv](36_MODELS_DETAIL16.csv).
