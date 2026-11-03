# C01-14 / DETAIL PASS18 — REAL Blender Workbench shaded/wireframe, binary FBX QA, Unity HOLD

**Scope:** optional EXISTING C01-14 RAI-01/RMP-01 only. Both OUTSIDE the 36 canonical P15–P19 interior props. NO model additions, source asset changes, ship edits or merges; own PR #24 remains DRAFT.

## Actually executed NEW Blender 4.0.2 render

[Workflow #41352169704](https://github.com/C8LyNn/Model-Test/actions/runs/41352169704) = SUCCESS **all steps**. Genuine Git LFS source checkout: original RAI-01 v002 4 parts/48 triangles; final real native v003 20 parts/424 triangles. Blender 4.0.2 Workbench rendered **six genuine PNG frames**: full BEFORE/AFTER shaded and true original-mesh wireframe, two after base-socket closeups, same full-scene camera. Wireframe is Blender's temporary non-destructive rendering-only modifier showing original triangle edges, removed immediately after each frame. Actual BLEND/FBX original binaries unchanged. Per-file image SHA256 in [full Blender-generated JSON receipt](REAL_BLENDER_PASS18_SHADED_WIREFRAME.json); all 6 PNG SHA verified from downloaded original artifact 13101532651 (ZIP CRC PASS). PNGs committed to [Pass18 Blender preview folder](../Previews/Blender/).

## Exact unchanged native SHA-256

| Model | Genuine BLEND SHA-256 | Actual Blender binary FBX7400 SHA-256 | Parts / Triangles |
|---|---|---|---|
| RMP-01 v002 | 7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa | 97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443 | 6 / 72 |
| RAI-01 v003 | 715bd015029b6f4cfc4126b4b6e0e944cd03c2719f70ceb719d5912baa3e0e42 | f0c8fd590d7752431c869be2f9807209b7632d87a77ab619049c90f60f0ff1fe | 20 / 424 |

RAI original source authoring OBJ SHA256 634716a4ee5c7f8ffb5e53d80d862833670e28c90f07fec133c88d7632efb798. Independent real binary FBX triangles ↔ OBJ coordinates are 424/424 at 1µm (previous PASS17 physically executed receipt). Real native Blender export/reimport run [#41347007426](https://github.com/C8LyNn/Model-Test/actions/runs/41347007426) PASS.

## New read-only actual FBX7400 independent topology and UV QA

Reopened true physical FBX bytes for RMP v002 and RAI v003, verified all four BLEND/FBX full SHA and signatures. RMP: 6 mesh parts/72 tris, 48 indexed vertices, ZERO degenerate triangle, duplicate face, loose vertex, UV0 out-of-range or zero-UV area, wrong face-corner normal, indexed boundary, nonmanifold or reversed edge winding. RAI: 20 parts/424 tris/1160 raw indexed FBX vertices, ZERO degenerate triangle, duplicate face, loose vertex, UV0/normal defect, nonmanifold or bad winding.

**Important nuance:** direct RAI FBX *indexed* topology exposes 1128 boundary edges because 912 vertex instances are split at face UV/hard-normal seams. Independent per-part audit-only coordinate-equivalence weld at 1 micrometre in a COPY yields 248 position-unique vertices across all 20 parts and ZERO true geometric boundary, ZERO nonmanifold edges, ZERO bad winding on all 20. This is not a real source edit or blanket Auto Weld. Do not mistake split UV vertices for floating geometry or holes.

**Complete physical user-delivered ZIP:** C01_14_DETAIL_PASS18_REAL_NATIVE_BLENDER_QA.zip (26 members; 12,484,650 bytes; SHA256 079222b37a296616dca0c1475b3352caf1ea3644133e5ce79264433a495455fe; CRC + every member SHA PASS). Contains real 4 BLEND/FBX, current OBJ, 6 true Blender renders, shaded/wireframe comparison board, independent real binary QA JSON and scripts, exact interactive GLB/HTML, SHA manifest. Browser runtime smoke in sandbox NOT PASS (EGL/Xvfb obstacle), so no browser-execution claim.

## Unity and release acceptance

Actual Unity 6 URP project/editor import = NOT RUN. Independently signed C01-02 release QA = PENDING. For optional RAI Unity staging: require exact current FBX SHA, 20 imported named meshes, 424 tris, 20 UV0 and material slots, imported 2.0m width / 1.10m height / 0.14m maximum depth, correct rail upright basis and static colliders; no added moving parts. RMP original unchanged. These are tests to run, NOT observed Unity facts. 36-model P15–P19 release status unchanged by this optional asset. NO MERGE.