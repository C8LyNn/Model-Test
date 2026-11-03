# C01-15 — DETAIL PASS17 / P15-02 native-export handoff

**Owner:** C01-15 Technical Installations; existing Draft [PR #16](https://github.com/C8LyNn/Model-Test/pull/16) under [HQ #36](https://github.com/C8LyNn/Model-Test/issues/36). Wave02 Draft #25 untouched. NO merge, new model ID or ship architecture change.

## Authored and committed

Current P15 original source **v0.1.6** SHA256 `9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3`, Git blob `07531d92cef59d81c9e185810c4a407c48bb918a`, [source commit](https://github.com/C8LyNn/Model-Test/commit/b1d3c69d082afb713801cba00fd494b8126dfed2).

P15-02 now has **four 8-sided 10mm-diameter / 37mm-long through-fasteners**, each in source spec, at `X=±225mm, Y=±164mm, Z=44..81mm`. Two attach top and two attach bottom rear louver guide rails to original top/bottom frame; all previous 30 meshes/6 louvers/12 previous blade studs/frame/4 existing screws stay unchanged. 34 named parts, no new asset IDs; original bounds, pivot, hierarchy and material roles unchanged. Uses previous IKON/Eaton/Rittal engineering references documented in `Assets/C01InteriorProps/P15/References/DETAIL_PASS16_CONSTRUCTION_REFERENCES.md` without copying vendor CAD or images.

## Actually executed mesh QA and tangible files

- Physical before input was genuine prior PASS16 *offline source-derived* GLB SHA256 `c8b81d26c52f9d7416cc137988836108deb6b9173fe0327ac6f25c4e2b240034`, NOT stale FBX. Source change applied as **4 new meshes** to exact 30 old parts; new GLB exported and re-imported. Original 30 indexed vertex/face arrays preserved.
- **After source-derived GLB SHA256:** `e612e53a545ffbb2ac4ec13ade793990b03504c37bd7658ab6b07dff2663924f`.
- **After source-derived OBJ SHA256:** `cd9a4dce55c269d2adb14f528bbdcadf958b3d3f8439d12e6d4c5841901e8bfd`.
- **34 named closed/consistent winding/positive-volume mesh objects**; V 416→488, T 712→840, degenerates 0, full AABB unchanged; **8/8** real new fastener ↔ existing frame/support surface intersections found with bidirectional segment-triangle tests (32 hits per required pair). Same-facing co-planar overlaps 0→0 via planar projected polygon scan on all triangle orientation groups (approximate plane tolerance; not all possible oblique/near-coplanar interpenetrations).
- Offline software-derived real-GLB before/after shaded + wireframe PNGs (NOT Blender Workbench), and self-contained interactive HTML `P15-02_PASS17_INTERACTIVE_VIEWER.html`, displaying **all actual 840 GLB triangles**, 34 named mesh selection, orbit, zoom, shaded/wire toggles, no external assets. WebGL fallback Canvas2D provided. **JS syntax validated**; actual headless WebGL screenshot not validated because local EGL driver failed.
- Conversation-delivered physical ZIP `C01-15_DETAIL_PASS17_P15-02_SOURCE_QA.zip`, 11 entries, **1,275,870 bytes**, CRC PASS, SHA256 `2f5f99233735f964c111b31577e4cba3a415a3156bfb45a383df89b0d08b2536`. Includes GLB, OBJ, interactive HTML, four BEFORE/AFTER PNG, closeup, SHA256 manifest, QA JSON and README. No Blender or Unity binary fabricated.
- Machine-readable QA: `Assets/C01InteriorProps/P15/QA/Pass17/P15-02_SOURCE_DERIVED_ACTUAL_GLTF_QA.json`.

## Native production completion gate — BLOCKED

**Current host:** Blender 4.x, bpy, Git LFS and Unity 6 URP absent. Existing native `.blend` and Blender binary `.fbx` are **historical, stale, and not regenerated** from v0.1.6. Native save, Blender-origin FBX export, Blender FBX reimport, native UV0/hard normal/material QA, genuine Blender BEFORE/AFTER and C01-02 final approval **NOT RUN / PENDING**. Historical GitHub Actions runner pre-allocation failure should not be represented as mesh test failure.

**NEEDS_OWNER_ACTION:** restore eligible runner or provide authorized Windows Blender4.x + Git LFS. Checkout current PR16 HEAD; ensure hydrated sources; run `Tools/C01Props15/blender_build.py` against exact spec v0.1.6, re-import new FBX, compare model hierarchy/pivot/UV0/normal/materials, inspect new four shanks in real mesh and clearance; save genuine .blend, binary .fbx, Blender same-camera shaded/wireframe and full SHA manifest. Then independent C01-02 exact hydrated FBX QA and C01-10 Unity6 URP prefab/collider staging. **Keep Draft and unmerged until acceptance.**
