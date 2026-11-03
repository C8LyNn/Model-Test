# C01-19 PASS17 — independently fetched real Blender artifacts and interactive QA viewer

## Artifact provenance (ACTUAL CI, not offline Blender-format patches)
- W01 successful native Blender 4.0.2 run: https://github.com/C8LyNn/Model-Test/actions/runs/41346465283 ; artifact ID **13099591414**
- W02 successful native Blender 4.0.2 run: https://github.com/C8LyNn/Model-Test/actions/runs/41346471952 ; artifact ID **13099890315**
- Actually downloaded both original artifact ZIPs and checked **8/8 native BLENDER signatures, 8/8 binary FBX 7400 signatures, 8/8 exact original source SHA via local SHA256**.
- Actual producer QA receipts pinned in branch: `QA/PASS17/SUMMARY.json` and per model `PASS17_NATIVE_DETAIL_ROUNDTRIP.json`. For **P19-01, P19-02, P19-05**, independent on-disk SHA agrees byte-for-byte with actual Blender-generated .blend & FBX: full native **Blender save/export/reimport PASS 3/3** at exact run SHAs. P19-03/04/06/07/08 binary files physically present, but independent roundtrip on those five **not established by this receipt**.

## Accurate interactive viewer from actual newest binary geometry
- Reparsed **all 8 real current native FBX** using independent Kaydara FBX 7.4 reader (Object→Geometry connections + Model local translations), exported **8 new per-model OBJ** as mechanical conversions of authentic real FBX, no historical FBX/proxy cubes.
- Constructed **offline standalone HTML** with selectable models P19-01..08, shaded or wireframe, mouse orbit, zoom and scene axes. For FBX n-gons in P19-03/04/06/07/08 only the *viewer* triangulates them, without modifying the FBX/BLEND source.
- User-downloadable archive `C01-19_DETAIL_PASS17_REAL_BLENDER_FBX_OBJ_INTERACTIVE_QA.zip`: **46 files, 8,206,105 bytes, ZIP CRC PASS**, SHA-256 **`58d039c026e82c046f30825fb8a6a15b945a3445b1381bb3b0cbb28ee01793b7`**. Contains 8 original actual BLEND, 8 actual binary FBX, 8 newly-derived OBJ, 3 genuine Blender QA image sets, 8 original producer receipts / summaries, offline interactive HTML and source SHA manifest.
- Standalone HTML SHA-256 **`1b5f1aeb8a1842f0cb9d1193ca8cba83e90efd1ca8b245db14e5f87fb96ef24f`**.
- Current genuine Blender-derived detailed meshes: P19-01 **4 meshes/269V/470T** (blend `a8883117ec9e59b93cb988970c09d6cdaf496b8a73957a60aa3ca503f8be420f`, FBX `e2e0bb9e095c1daed87e407814e88f8788cf503ab705d3e34513879038bcd559`); P19-02 **5/166V/292T** (blend `ff0448b34e70ab65380889dfc1d46e426d88873684e831775306cfca28e1a99f`, FBX `b0d68ce917a938b4bdaa32f4b2d48dcab5275c752c141260cabd3d82a5c9374f`); P19-05 **7/152V/252T** (blend `7905086e87660461d46e6d633b16fc655142939ac4cbc0df0c670067da9314b2`, FBX `d07b4884cfe1de2c48a96dc9407c2eccdfbdbdf703551c71ae195bd3fd8c9d87`).
- Genuine Blender Workbench BEFORE/AFTER images and independent binary SHA checks in archive. Interactive viewer is **NOT Unity renderer**, normal/material shaders are approximated.

## Gating
- Source-native actual Blender 4.0.2 export/reimport **PASS 3/3 detailed models only**; no fabricated Unity PASS.
- Formal C01-02 independent final acceptance **PENDING**, Unity 6 URP actual import/prefab test **NOT RUN**, P19-07 historical T-junction candidates **HOLD pending current-engine visual QA**.
- Actual BLEND and FBX bytes **already exist in successful workflow artifacts and producer GitHub branch**; this QA handoff only writes a Markdown receipt. No asset overwritten; no merge; Draft PR unchanged in status.
