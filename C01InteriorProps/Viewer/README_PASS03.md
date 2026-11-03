# C01-10 — PASS 03 source-mesh gallery

**Authoring scope:** integration and visualization of original existing meshes. C01-10 does NOT weld vertices or modify the C01-15–19 source models. Mesh fixes belong to those owners, independent topology gate to C01-02.

## Actual deliverables

- `mesh-source-gallery.html`: interactive comparison of two **real** FBX / GLB / embedded glTF source exports. Two synchronized viewports, actual triangulation wireframe, original materials in Shaded, mixed Shaded+Wireframe, shared camera controls, screenshot export. Direct local file upload **and two exact embedded source glTF files from C01-17 PR #23** (P17-04/P17-05) for immediate before-mesh viewing. No reconstructed sample geometry.
- `p0_original_source_inventory.json`: six authoritative source file paths/PRs, Git LFS binary SHA-256 and size for FBX, two genuine embedded glTF source metrics read from PR #23. Explicit status: SOURCE_LOCATORS_ONLY_NOT_QA.
- `PASS03_INTEGRATION_STATUS.csv`: no falsely completed mesh/Blender/Unity test; original source availability separated from repair and QA approval.

**Only six P0 assets are enabled:** P17-04, P17-05, P18-04, P18-05, P19-07, P19-08. Do not switch to the remaining 30 until the original six have a real per-model before/after topology audit and independent C01-02 review. Source owners edit their existing PRs, not this gallery PR.

## Using the interactive viewer

1. Download the `mesh-source-gallery.html` file from [this branch](https://github.com/C8LyNn/Model-Test/blob/c01/props-10-showcase-integration/C01InteriorProps/Viewer/mesh-source-gallery.html), choose **Raw** or download the file. Open it in Chrome/Edge.
2. Network access to [esm.sh](https://esm.sh) is needed **only** for Three.js modules (FBXLoader, GLTFLoader, OrbitControls). The uploaded model file content is read locally in your browser, not uploaded to an external server.
3. Download the **real original assets**, not Git pointer text, from owner branches: PR #23 `c01/props-17-wave02`, PR #26 `c01/props-18-cargo-wave02`, PR #29 `c01/props-19-furniture-wave02`. Use `git lfs pull` after checking out each owner branch or use real verified CI artifacts.
4. Select P17-04 or P17-05 and click **Otwórz prawdziwy glTF P17-04/05 (BEFORE)** to immediately load the exact original glTF source bytes included in the viewer (Git blob SHAs in inventory); or upload the original BEFORE from disk. For P18-04/05 and P19-07/08, obtain full original FBX via Git LFS and use the BEFORE file selector. Upload AFTER only when the owner has produced and identified the actual topology repair.
5. Rotate/zoom left canvas (right canvas tracks same camera), choose Shaded/Wireframe/Both, optionally save both screenshots. Downloads end in `VIEWER_NOT_QA.png` intentionally.
6. If a producer export is `*.gltf`, it must be glTF 2.0 with data URIs embedded; GLB also works. A standalone `*.gltf` referencing external `.bin` is rejected, to avoid silently rendering a partial model.
7. Gallery metrics are exported mesh parts, triangle counts, vertex attribute entries, normals and UV0 presence. **Not proof of manifoldness**, weld or source Blender vertex count (UV seams and sharp edges may duplicate exporter vertex entries).

## Original source priority inventory

| Model | Producer source | Real source file verified by GitHub text inspection | FBX download state in C01-10 |
|---|---|---|---|
| P17-04 | PR #23 | Embedded glTF 29 mesh parts / 348 tris / UV0+normal present | LFS pointer only; 87,308 B expected |
| P17-05 | PR #23 | Embedded glTF 20 mesh parts / 240 tris / UV0+normal present | LFS pointer only; 65,500 B expected |
| P18-04 | PR #26 | FBX locator SHA-256 pinned | LFS pointer only; 41,660 B expected |
| P18-05 | PR #26 | FBX locator SHA-256 pinned | LFS pointer only; 41,356 B expected |
| P19-07 | PR #29 | FBX locator SHA-256 pinned | LFS pointer only; 48,668 B expected |
| P19-08 | PR #29 | FBX locator SHA-256 pinned | LFS pointer only; 44,444 B expected |

Each source/branch/path/hash is in `p0_original_source_inventory.json`. Git blob SHA is *not* equivalent to the SHA-256 of LFS binary content.

## WHAT IS NOT DONE

- Actual source mesh editing / topology repair: **0/6**, NOT RUN (model owners C01-17,18,19).
- Actual before/after file comparisons and rendered screenshot evidence: **NOT RUN** (AFTER files not confirmed).
- Blender `.blend` topology audit and FBX roundtrip: **NOT RUN by C01-10**. Producers may have older export QA for original versions; that is not PASS03 repair evidence.
- Unity 6 URP prefab import, visual QA and PlayMode: **NOT RUN**.
- Independent C01-02 TECHNICAL_TOPOLOGY_GATE: **PENDING**.
- Browser interaction rendering: **NOT RUN here** (no browser/Three.js CDN in runner). Inline JavaScript syntax/static controls, original P17 embedded-glTF JSON structure and source links were inspected. This is not a recorded before/after image proof.

## Acceptance gates for a repaired model

Require BEFORE and AFTER actual file hashes, native Blender counts (verts/edges/faces/tris *per mesh*), defects with proofs, intentional exceptions, native Blender FBX roundtrip, exact source hierarchy/pivots/material preservation and independent C01-02 QA. The viewer never labels a model repaired based on appearance alone.

**No geometry of ship, corridor or level modified. No merge. No Wave 03.**
