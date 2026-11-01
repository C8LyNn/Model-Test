# C01-12 — DETAIL PASS17 / Native Blender material-only v004 handoff

**Role:** C01-12 Floors & Ceilings. **Scope:** the existing LEGACY modular F01, F02, C01 models only. These are **not** additional members of the 36 P15–P19 props. Producer Draft PR [#20](https://github.com/C8LyNn/Model-Test/pull/20), parent HQ [#36](https://github.com/C8LyNn/Model-Test/issues/36). **No ship geometry edits, new model IDs, unapproved prefab replacements or merges.**

## REAL execution, not spec-only

- Verified Blender 4.x GitHub Actions [run 41348360876](https://github.com/C8LyNn/Model-Test/actions/runs/41348360876): **SUCCESS**. It actually opened three repaired source `.blend` files, added **non-geometric** PBR candidates, saved three native v004 `.blend`, exported three **binary FBX** and three **GLB**, reimported each FBX, generated nine real PNG PBR maps and 12 real Blender Workbench shaded/wireframe screenshots. SHA/real signatures checked in runner.
- Verified follow-up [run 41348558239](https://github.com/C8LyNn/Model-Test/actions/runs/41348558239): **SUCCESS**. Bundled genuine three GLBs and all Blender screenshots into one **6.2 MB self-contained model-data HTML**. HTML imports Three.js from CDN; image comparison works offline. No external model data, dummy boxes, old FBX or vendor imagery.
- The **authoritative after-manifest** is [DETAIL_PASS17_NATIVE_SHA256.json](../DetailPass17/QA/DETAIL_PASS17_NATIVE_SHA256.json). Each source `.blend`, final `.blend`, binary `.fbx`, `.glb`, every PNG and preview has **full byte SHA-256**. Git LFS pointer-only bytes must never be mistaken for delivered native files.
- Download latest real workflow artifact via the Actions run, or use the checked-in LFS-tracked files under `DetailPass17/`.

## Exact technical contract

- **Unchanged geometry:** F01, F02, C01 each **16 vertices / 28 edges / 14 quad polygons / 28 triangles**, all three original material-slot identities and face material indices. **Zero moved mesh vertices or UV0 entries.** The workflow hashes BEFORE/AFTER indexed positions, faces, per-face material indices, UV0, object location/scale/rotation and bounds. For each of the three IDs, the signatures are **identical**.
- Legacy spatial envelope unchanged: F01/F02 source Blender bounds **X=0..1, Y=-1..0, Z=-0.2..0 m**; C01 source **X=0..1, Y=-1..0, Z=3..3.2 m**. No new pedestals, screws protruding into walking path, actual anchors or attachment sockets.
- Original PASS03 repaired X-normal end-cap UV0 is preserved, not reprojected here.
- New 512×512 PNG candidates per ID: `basecolor` (sRGB), `normal` (linear/non-color OpenGL +Y tangent space), `roughness` (linear/non-color). Visual fastening hints and tile-edge wear are **normal/texture only, not physical bolts**.
- F02's original marked-face index and existing material-color separation are retained through the per-slot material handling; **actual Unity appearance not verified**.
- New native files: `DetailPass17/Blend/*v004.blend`, `DetailPass17/FBX/*v004.fbx`, `DetailPass17/GLB/*v004.glb`, and `DetailPass17/Textures/`. Previous v002 and fixed v003 remain untouched.

## Comparison / interactive preview

- `DetailPass17/Previews/*BEFORE_SHADED.png`, `*AFTER_SHADED.png`, `*BEFORE_WIREFRAME.png`, `*AFTER_WIREFRAME.png` are real **Blender Workbench source-mesh** images from the same camera; **not** a physically based render demonstrating accurate normal/roughness in Unity. Wireframe curves are traced from **real mesh edges**.
- [C01_12_DETAIL_PASS17_REAL_GLB_INTERACTIVE.html](../DetailPass17/C01_12_DETAIL_PASS17_REAL_GLB_INTERACTIVE.html) contains actual v004 `.glb` bytes and actual Blender PNGs, with asset select, wireframe and camera orbit.
- A browser runtime smoke gate, if actually executed, writes `DetailPass17/QA/DETAIL_PASS17_BROWSER_SMOKE.json`; its absence is **NOT RUN**. Passing static HTML embedding checks is not evidence of successful WebGL rendering.

## Remaining acceptance gates (fail closed)

1. **C01-02:** independent exact-final native SHA, hard-normal/UV0/material validation, LFS pointer vs binary provenance, suspect same-facing coplanarity and source/binary regression — **PENDING**.
2. **C01-10:** import the real v004 FBX into **Unity 6 URP**, assign base color with sRGB and normal maps with normal-map importer; roughness is **not** automatically a Unity smoothness map (`smoothness=1-roughness`, with the chosen URP Lit channel packing). Confirm F02 sign and ceiling orientation, texture seams, collider, prefab pivot, grid replacement eligibility and static lighting — **NOT RUN**.
3. **Browser:** Three.js CDN requires network; Chrome/WebGL execution is not inferred from generated HTML. Check the distinct smoke report.
4. **No merge** until C01-02 acceptance and C01-10 Unity integration. This historic kit may not silently replace the ship v4 floor/ceiling contract.

**Source:** `Tools/C01Floors12/detail_pass17_material_native.py`; **native CI:** `.github/workflows/c01-floors12-detail-pass17.yml`; **viewer generator:** `Tools/C01Floors12/detail_pass17_glb_viewer.py`.
