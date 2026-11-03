# C01-10 — DETAIL PASS 17 / Independent real Blender FBX QA

**Scope:** P18-01 crate, P18-02 industrial rack, P18-03 four-wheel cart. Existing models only. No ship changes, new IDs or merge.

## Provenance and integrity

- Producer Blender 4.0.2 native export [GitHub Actions #41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313) completed SUCCESS. Source matched exact commit `03f97354e47645ee80422115d29c67ef48808679`. Actual Blender/FBX package artifact #13099325067 was downloaded and independently opened.
- Original exact six-file ZIP: 446041 bytes, SHA256 `24ecf87d774e9ff3de87f22f34a59564a4668f926c7813b9f3ae2ea0b35683b0`, ZIP CRC PASS.
- Three actual Blender sources begin with `BLENDER-v400`; three actual FBX files begin with `Kaydara FBX Binary`, FBX 7400. Independent SHA-256 of physical files exactly matches new Git LFS OIDs.

| Asset | Old native FBX parts/T | New native FBX parts/T | Full native .blend SHA-256 | Full FBX SHA-256 | New bounding XYZ |
|---|---:|---:|---|---|---|
| P18-01 | 15/180 | 47/980 | `d8a525acdb0eb7dcfd7b37fb31117b42a53bb655a6543282adac3dff857900a1` | `f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c` | 0.900 × 0.907 × 0.919 m |
| P18-02 | 17/204 | 59/1284 | `49b3697ff01efe0497f12703421f05fedb4e9a29636626bf72d1e57493a369d5` | `e962c47fc60d84fb0d06d69f7aec3eead745705be002b7eb0abf11c5da452558` | 2.162 × 2.100 × 0.862 m |
| P18-03 | 17/348 | 63/1780 | `ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56` | `f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926` | 1.000 × 1.200 × 0.700 m |

## Independent native binary mesh QA — EXECUTED

- Read and parsed all **169/169** true FBX binary Geometry objects and indexed `Vertices`, `PolygonVertexIndex`, `LayerElementUV` and `LayerElementNormal` data. Source after export totals **4044 actual triangles**.
- Per-mesh polygon topology and winding test: **0** boundary edges, **0** nonmanifold edges, **0** inconsistent edge orientations. **0** degenerate triangles, invalid triangle indices, invalid UV0 indexed corners or missing corner normals.
- Each of the 169 FBX meshes has valid UV0 and corner normals. All three models have expected source 47/59/63 part counts and 980/1284/1780 triangles. This is FBX real-byte QA, not a proxy/manifest-only claim.
- P18-03 true FBX OO parent/child links: four wheel mesh nodes; 8 hubs parented to their moving wheels; 28 stationary fork/axle/anchor/gusset/crown elements not children of wheels; four CrownBolt children of their ForkCrown and four AnchorRetainer children of their Anchor. All tested relations PASS.
- Still NOT RUN: full global cross-mesh z-fighting, moving collision sweep, Unity PhysX/colliders, actual URP materials and Unity prefab acceptance.

## Preview sources and native before/after evidence

- Created 12 **true physical FBX geometry-derived** preview PNGs: BEFORE / AFTER × shaded / wireframe × three assets, identical diagnostic camera configuration. Also a full contact sheet.
- Renderer: **VTK** applied to independently parsed FBX 7400 geometry and parent transforms; this is NOT a Blender Workbench render. Diagnostic per-object colors, not copied PBR materials.
- Contact sheet SHA-256 `c450552e59401dadbc814c2f7522eff7bb6fbb250cb16438bea59b4a20560a32`. Full 12 PNG + JSON QA ZIP SHA-256 `b4cb51ae4ff4121bd4492b4d4a9e88a1dd01a018767db7477648922a312b3f1e`.
- Actual preview images/ZIP delivered via ChatGPT conversation sandbox, not falsely claimed to be committed as GitHub PNGs. Source code of independent FBX parser and VTK diagnostic renderer also available as generated conversation files.
- Interactive latest actual source viewers (fully embedded OBJ/glTF, offline, no CDN): [P18 cargo](./PREVIEW_P18_SOURCE_INTERACTIVE.html) and [P17 controls](./PREVIEW_P17_SOURCE_INTERACTIVE.html). Browser visual runtime not yet automatically tested.

## Release decision and remaining gates

- **P18-01/02/03** are true native Blender FBX export PASS and independently binary mesh QA PASS, promoted to **quarantine diagnostic candidate** with exact new SHA-256 in 36-ID manifest. **Not a final Unity release**.
- Independent **C01-02 final approval: PENDING**. **Actual Unity 6000.3.14f1 URP import, mesh/normal/UV prefab inspection, collision and PlayMode: NOT RUN.** No Unity executable in active execution host and authorized Unity-capable CI runner/activation not verified.
- Updated model manifest: **19 BLOCKED / 17 QA-only CANDIDATES / 0 final approved**. Draft PR #11 remains unmerged, ship unchanged.

## Exact source OBJ blobs at export

- P18-01: `7dc5c975e39ff6eb9be093b77e8720b7c26a89ab`
- P18-02: `fe96d137d0ac6de5b4c53820cade6cce89ccf2b9`
- P18-03: `2aaea1148ca37d8835c1298fadf1010b7ebf7875`
