# C01-17 — PASS06 / native Blender repair gate P17-05

**Issue:** #33 (parent #30). **Existing Draft PR:** #23. **No merge, no new models, no ship changes.**

## Actual existing geometry source correction: P17-05

- Original real Blender PASS03 render shows stippled strip under diagnostic screen, consistent with z-fighting. Exact coplanar contact from original binary FBX: DisplayBezel vs LowerDisplayRail, overlap area 0.059199984 m² on two parallel planes.
- **Actually edited** existing P17-05.gltf node LowerDisplayRail translation Z: 0.120 → 0.121 m, and synchronized P17-05.json spec. This shifts the existing rail 1 mm toward screen-front without altering any mesh buffers, UV0, normals, triangles, materials, pivots or overall AABB.
- Analytical coplanarity: original DisplayBezel Z faces -0.020/+0.260 m and original LowerDisplayRail faces -0.020/+0.260 m; corrected rail faces -0.019/+0.261 m. Thus the two exact same-plane source faces are no longer coincident. Blender and Unity rendering not yet executed on corrected source.
- **Strict blocker:** production native Blender and FBX still contain PRE-FIX geometry and MUST NOT be approved as PASS06. Their PASS03 byte SHA-256: BLEND 07be57396ccab85423745dc71db2e820eacd00f8191cb86809091c4d14a6dbbd; FBX 3fa314481f87d66f9a878936028b809cd78440d781146a058594e28f3f4e1740.

## Prepared actual native one-model execution (NOT RUN)

- C01InteriorProps_W02/Tools/pass06_native_p1705.py: opens the unchanged genuine source .blend by exact SHA; moves the existing rail object 1 mm in native Blender coordinates, writes a NEW real Blender .blend and binary FBX, captures authentic before/after renders, reimports FBX in an empty scene, verifies 20 parts/240 triangles, UV0, unchanged source meshes/materials/pivots/dimensions; writes new real file SHA to QA/PASS06/P17-05_NATIVE_REPAIR_RESULT.json.
- C01InteriorProps_W02/Tools/RUN_PASS06_NATIVE_WINDOWS.ps1: fail-closed Windows entrypoint; requires Blender 4.x and Git LFS on existing branch c01/props-17-wave02; never automatically commits/pushes/merges.
- Owner command in already-cloned repository:

    powershell -ExecutionPolicy Bypass -File .\C01InteriorProps_W02\Tools\RUN_PASS06_NATIVE_WINDOWS.ps1 -BlenderExe "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"

## Infrastructure diagnosis and status

- GitHub Actions two-OS minimal smoke #41098559165 had runner_id=0, steps=[] for both ubuntu-latest and ubuntu-22.04; exact account/platform root cause UNKNOWN. Settings/billing/runners endpoints not available through connected GitHub reader. No budgets or billing altered.
- Local container has NO Blender, NO bpy, NO owner Windows filesystem; external download.blender.org DNS fails. No native Blender execution possible here.
- New Actions may show queued; queued is not Blender PASS. Previous real PASS03 Blender runs W01 #41089779966 and W02 #41088800979 remain PASS for previous source SHA only.

## Owner-specific release gate

- Source glTF corrected: 1/7 model P17-05 (real source change). Geometry of remaining 6 unchanged because no confirmed mesh defects.
- New native .blend and FBX saved and imported in Blender PASS06: **0/7, NOT RUN**. Previous PASS03 Blender+FBX: **7/7 PASS** on old hashes.
- Independent C01-02 QA signed: **0/7**. Unity 6 URP: **0/7 NOT RUN**.
- Remaining contact candidates P17-01/03/04/06/07 are not automatically classed as defects; do not weld or redesign without visual confirmation.
- Final status: **NEEDS_OWNER_ACTION** — owner must restore GitHub runner eligibility or execute Windows Blender script. After actual results and new native SHA, request C01-02 exact-FBX audit, then C01-10 Unity.

Previous true source files, notes and renders are in QA/PASS03 of PR #23. Do not mark PR ready/merged until verified source-native synchronization and independent QA.
