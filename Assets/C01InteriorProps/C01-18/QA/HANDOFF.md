# C01-18 — DETAIL PASS17 / CARGO & MOVABLE OBJECTS — PRODUCER HANDOFF

**Date:** 2026-11-01 · **Draft PR:** #18 · **HQ:** #36 · **branch:** `c01/props-18-cargo`.
**Decision:** Producer OBJ + native Blender/FBX roundtrip **PASS**; independent C01-02 mesh QA and Unity6 prefabs **NOT RUN**. **NO MERGE / RELEASE HOLD**.

## Real current deliverables, not legacy geometry

| Asset | Actual OBJ parts / triangles | PASS17 physical changes | Native .blend/FBX |
|---|---|---|---|
| P18-01 crate | 47 / 980 | Four small lid keeper screw heads; old latch + hinge mechanics unchanged | Blender 4.0.2 CI PASS |
| P18-02 rack | 59 / 1284 | Four octagonal steel floor-post shoes; top-label backplates and rear gussets retained | Blender 4.0.2 CI PASS |
| P18-03 cart | 63 / 1780 | Two metal handle/post clamp collars; four wheel and hub pivots unchanged | Blender 4.0.2 CI PASS |

Source dimensions AABB meters X/Y/Z: crate `0.900 / 0.907 / 0.919`, rack `2.162 / 2.100 / 0.862`, cart `1.000 / 1.200 / 0.700`. Rack foot shoes increase horizontal footprint by **62 mm** per full X/Z extent versus earlier source; review placement in corridors. Cart ground contact min Y=0 for all four wheels and wheel centers Y=0.105 m.

**Source QA:** Indexed v/vt/vn + faces physically parsed on actual latest GitHub OBJ for all 169 mesh parts / 4044 triangles. No bad index, missing UV0, non-finite UV, degenerate face, duplicate face, boundary/nonmanifold edge, bad winding or face/normal direction found. All ten new solids share a point inside their original mechanical support (actual triangle ray parity 10/10). None of the newly added faces have same-facing coplanar projected bounding-box candidate against earlier faces. This does **not** constitute the required full independent triangle intersection, opposite-facing joint or animated clearance audit.

**Actual Blender/FBX evidence:** [successful GitHub Actions run #41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313), real Blender **4.0.2**, binary FBX **7400**, saved 3× BLEND and exported/reimported 3× FBX with UV presence and triangle counts 980/1284/1780. CI commit `03f97354e47645ee80422115d29c67ef48808679` pushed **six real Git LFS binaries**, not placeholders. CI artifact `C01-18-native-blender-fbx`, ID `13099325067`. SHA256 for every current OBJ/BLEND/FBX, byte sizes, per-model receipt and exact evidence: [PASS17 machine report](Pass17/DETAIL_PASS17_SOURCE_NATIVE_QA_AND_SHA256.json).

**Visual source previews:** [Interactive standalone actual OBJ BEFORE/AFTER viewer](Pass17/C01_18_REAL_OBJ_INTERACTIVE_BEFORE_AFTER.html) (download HTML via GitHub Raw and open locally; drag rotates, mouse wheel zooms, buttons toggle shaded/wireframe and BEFORE/AFTER). Static actual OBJ four-panel BEFORE/AFTER SHADED/WIREFRAME: [P18-01](Pass17/P18-01_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg), [P18-02](Pass17/P18-02_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg), [P18-03](Pass17/P18-03_SOURCE_BEFORE_AFTER_SHADED_WIREFRAME.svg). These are geometry-projected **source previews**, not native Blender screenshots. Browser rendering itself **NOT RUN**.

## Unity gate and what still needs execution

- Actual C# editor builder `Editor/BuildWave01CargoPrefabs.cs` updated: exact **169** per-source material mappings (fixes historical RUBBER material assigned to wheel forks), strict **47/59/63** mesh and **980/1284/1780** triangle checks, exactly **1/7/6** structural BoxCollider parts, and fixed previously broken wheel test: checks **only** `Wheel_LB/LF/RB/RF`, not all `Wheel_*` accessory mesh names.
- Existing checked-in serialized `Prefabs/P18-01.prefab` through `P18-03.prefab` remain historical; **no claim** they now include current 169 meshes. Run a real Unity 6 URP Editor import and select `Tools → C01 → Cargo → Build Wave 01 FBX Prefabs`; inspect generated prefabs, pivots, materials, colliders and moving/lid parts. Commit new prefab YAML only after real Unity output, not handwritten simulation.
- **Independent C01-02:** fetch current producer OBJ + LFS BLEND/FBX and SHA pin, run native topology, cross-object triangle/narrowphase, UV/normal/tangent, pivot hierarchy, wheel-to-upright clearances and opposite-facing interior z-fighting audit. Do not accept source-only producer checks as the independent release gate.
- **C01-10:** after C01-02, import into actual Unity 6000.3.14f1 URP and regenerate prefab YAML; verify scene scale, 4 wheels on ground, handles/latches, collision geometry, 3 materials types? Four exact materials **STEEL/DARK/RUBBER/CAUTION**, optional animation/rotation and actual corridor clearance.
- **Unexecuted:** C01-02 independent final binary audit **NOT RUN**; Unity6 Editor build/import **NOT RUN**; dynamic animation/collision **NOT RUN**; native Blender shaded screenshot capture **NOT RUN**; browser HTML runtime smoke **NOT RUN**.

No new model IDs, no architecture/ship source edits, no merge.
