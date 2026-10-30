# C01-16 / Wave 01 follow-up — producer re-audit, 2026-10-30

Existing producer PR: https://github.com/C8LyNn/Model-Test/pull/12
Independent C01-02 review: https://github.com/C8LyNn/Model-Test/pull/12#pullrequestreview-5706019808

The original downloadable production ZIP was unpacked and independently re-read in Python in this producer thread (not in Blender/Unity). Actual glTF/GLB geometry was loaded by `trimesh`; all three bounding boxes matched contractual dimensions, zipped PNG previews had valid PNG signatures, prefab YAMLs had local scale (1,1,1) and BoxColliders, and every prefab mesh/material GUID resolved to a .meta file in the same package. The included Blender export script parsed with Python AST. ZIP CRC check passed.

| Asset | Measured AABB XYZ (m) | Base Unity mesh triangles | Producer static status |
|---|---|---:|---|
| P16-01 | 1.20 × 0.12 × 0.15 | 60 | PASS |
| P16-02 | 0.35 × 0.22 × 0.14 | 60 | PASS |
| P16-03 | 0.20 × 0.30 × 0.20 | 60 | PASS |

**Not claimed:** Blender native .blend files (MISSING); Blender binary FBX generated/roundtrip (NOT RUN); Unity 6 URP real import, visual emission/material QA and actual ship clearance (NOT RUN). The ASCII FBX source is not equivalent to verified binary Blender output. Independent C01-02 final acceptance still BLOCKED.

**Repair action:** no failing source mesh corrections identified by C01-02 and no speculative change to already statically passing W01 meshes. Source exporter remains available at `C01Source/Lighting/Blender/make_blend_and_binary_fbx.py`. W02 continuation is separately staged in stacked PR #28.
