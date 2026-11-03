# C01-03 — DETAIL PASS17 / GENUINE BLENDER NATIVE INTAKE + 36-ASSET QA HOLD

**Date:** 2026-11-01  
**HQ:** https://github.com/C8LyNn/Model-Test/issues/36  
**Existing Draft:** https://github.com/C8LyNn/Model-Test/pull/27  
**Owner scope:** C01-03 Asset Library (immutable SHA registry, evidence intake, provenance, source-backed preview). **NO** edits to producer meshes, existing ship layout or active game scenes; no new IDs or merge.

## Major change since PASS16: TWO REAL Blender 4.0.2 GitHub Actions executions

**C01-15 W01:** [successful Actions #41344475164](https://github.com/C8LyNn/Model-Test/actions/runs/41344475164), final producer HEAD [`0d6452290e94e0017f6ca847afc1244fd936f7af`](https://github.com/C8LyNn/Model-Test/commit/0d6452290e94e0017f6ca847afc1244fd936f7af). Verified actual job log: Blender 4.0.2 generated and reopened 3 native `.blend`; exported 5 Kaydara binary `.fbx` (3 main plus P15-03 Body/Door); 25/25 producer roundtrip UV/normal/material/scale checks PASS; 9 real Blender three-angle AFTER PNG previews. `17/17` Git LFS file pointers (3 .blend + 5 .fbx + 9 PNG) were **actually fetched from exact new HEAD and independently compared to producer SHA256 manifest size+OID**, 0 mismatch. Source P15 `geometry_spec.json` is now **version 0.1.6**; new exact UTF-8 source SHA256 `9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3`.

**C01-18 W01:** [successful Actions #41344872313](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313), final producer HEAD [`03f97354e47645ee80422115d29c67ef48808679`](https://github.com/C8LyNn/Model-Test/commit/03f97354e47645ee80422115d29c67ef48808679). Verified actual job log: Blender 4.0.2 imported **CURRENT** source OBJ, saved P18-01/02/03 `.blend`, exported actual binary FBX 7400, reimported and reported `BLENDER_FBX_UV_NORMAL_ROUNDTRIP_PASS` for 47/59/63 individual mesh objects. Exact `6/6` new .blend/FBX LFS pointers/OIDs pinned at final HEAD. [Real six-file native export artifact](https://github.com/C8LyNn/Model-Test/actions/runs/41344872313/artifacts/13099325067) uploaded by CI, not a fake FBX or merely OBJ converted to text.

| ID | Latest OBJ parts / triangles | Latest authored OBJ SHA256 | Genuine `.blend` SHA256 | Genuine binary `.fbx` SHA256 |
| --- | --- | --- | --- | --- |
| P18-01 | 47 / 980 | `4fd8fc54e37f9941142aed85559ecef077cdfc97e2326b153dfb2ca91fa7b566` | `d8a525acdb0eb7dcfd7b37fb31117b42a53bb655a6543282adac3dff857900a1` | `f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c` |
| P18-02 | 59 / 1284 | `b7ee7803f625c2ec48901a0ad6739248e22a59ac56d7dada5e20847604e4d2fc` | `49b3697ff01efe0497f12703421f05fedb4e9a29636626bf72d1e57493a369d5` | `e962c47fc60d84fb0d06d69f7aec3eead745705be002b7eb0abf11c5da452558` |
| P18-03 | 63 / 1780 | `4446cfc77a6c4a9de4cf7c172ae06395b9dad9e39941566046d952eab0f16a6a` | `ea1b4f5cc5612f8d8ff5c3c585b9b48843659972c2371204b5d3b5c4df3a3b56` | `f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926` |

P18 latest aggregate **169 physical source mesh parts / 4044 triangles**. The previously reported PASS16 **159/3764** was superseded by newer producer source commits. All values pinned at **exact immutable Git commits**; source SHA values were recomputed from actual fetched UTF-8 bytes with SHA-256 implementation verified against both standard test vectors. Native hashes are matching Git LFS OIDs of files genuinely generated during linked Blender runs. We do **not** claim C01-03 independently hydrated/parsed full native FBX binary bytes; that is the next C01-02 gate.

### Real-geometry self-contained interactive 3D BEFORE / AFTER

[**Open source-backed viewer file**](./C01_DETAIL_PASS17_REAL_SOURCE_INTERACTIVE_VIEWER.html) (download the HTML, open locally in WebGL-enabled browser). **All geometry embedded offline and sourced from actual GitHub OBJ/glTF**, no proxy blocks, no old FBX, no external JS/CSS/CDN/network at runtime. Controls: choose asset/part, rotate, zoom, shaded, wireframe or combined. Contains **7 views**: P18-01/02/03 source BEFORE from exact PASS16 commit `60c582cc74bf1401baed4f7d46c99d75dd3efab1`, source AFTER from `03f973...`, plus P17-01 current repaired glTF from C01-17 `766432...`. 7/7 parsed data views have in-bounds original indexed vertices/triangles. No screenshot or browser/WebGL execution can be certified from this environment: **BROWSER RENDER NOT RUN**. These are independent source views, not native Blender rendered BEFORE/AFTER.

### Existing P17-01 / other restrictions

C01-17 guide source P17-01 still pinned to actual corrected glTF `e0df06d260a955fe926f7e0279068bf2a2e6a6b5`, SHA256 `77bffeffd7440c40882945e7341f659be2035eb23e67dae6329d108c74c88980`: producer and independent C01-02 previously measured KeyboardGuide_L/R same-facing overlap 190mm² each → 0, prior P16 motion/other fixes unaffected. This is source-only QA, not current native FBX release.

P16-01..07/P17-01..07/P18 W02/P19 W01/W02 native final gates remain separate; **P19-07 vertex-on-edge visual HOLD** remains. Do not replace sources with historical FBX, offline-made FBX or fake BLEND signatures.

## Pass17 deliverables on THIS branch

1. [Source SHA/native candidate 36-ID registry](./LIVE_ASSET_REGISTRY_36_NATIVE_CANDIDATES.json) — immutable exact producer SHAs and no false production releases.
2. [15/15 independently executed manifest invariant checks](./VALIDATION_AND_NATIVE_GATES.json).
3. [Self-contained source-geometry WebGL viewer](./C01_DETAIL_PASS17_REAL_SOURCE_INTERACTIVE_VIEWER.html) — 7 genuine OBJ/glTF source views (3 before/after pairs, one console).
4. This report (C01-03 handoff).

## Strict final gate / owner responsibilities

- **C01-02 independent:** hydrate the **exact latest** P15/P18 FBX LFS binaries; compare source geometry, part count, UV0/hard normals, materials, coplanar/self-intersection, assembly support, wheel ground contact, swept animation and SHA. Producer roundtrip PASS is **not** equivalent to independent release PASS.
- **C01-10 integration:** run actual Unity 6 URP import of those exact certified hashes, validate prefab hierarchy, pivot axes, URP materials, colliders and wheel/switch/hinge motion. **UNITY NOT RUN** in C01-03.
- **C01-15/18:** provide true Blender shaded+wireframe BEFORE/AFTER (at same view) on current source. P15 has genuine AFTER three-angle PNGs; native BEFORE/AFTER pair is **NOT RUN**. C01-18 genuine native binaries exist; native rendered before/after **NOT RUN**.
- **C01-17:** latest source repaired guide awaiting Blender export on its latest exact source commit.
- **C01-16/19:** continue native exports and mesh QA without changing ship or unrelated IDs.
- **C01-00:** keep Draft PRs and 36/36 release **BLOCKED**, with 0 independent exact-binary final approvals and Unity6 import runs recorded until formal QA and authorized merge.

**Do not mistake 6 genuine Blender producer export pairs for 6 released Unity assets.** Current terminal stage: native producer exports **6/36 available as new candidates**; independent final FBX QA **0/36 approved**; Unity 6 **NOT RUN**; all 36 remain release BLOCKED.
