# C01-10 / PASS 03 — source-mesh viewer static verification

**Date:** 2026-10-30  
**Issue:** #30 (mesh topology repair, P0 six-model gallery), coordinator C01-00, independent QA C01-02.  
**Branch:** `c01/props-10-showcase-integration`, existing draft PR #11.  
**Result:** **20/20 STATIC CHECKS PASS**. These checks are program-code/content inspections; browser rendering, native Blender geometry, FBX roundtrip, Unity import and mesh repairs **NOT RUN**.

## Static assertions executed against actual GitHub source
1. Gallery inline JS parses as an ES-module body after removing three static import lines for syntax checking.
2. Three.js FBXLoader and GLTFLoader imports present.
3. Shaded, Wireframe and combined modes selectable.
4. Wireframe derives from actual imported geometry attributes.
5. Original source material references preserved in shading mode.
6. Camera synchronization between BEFORE / AFTER viewports.
7. Both before and after file inputs present.
8. Verified embedded original glTF activation for P17-04 and P17-05.
9. Original embedded glTF streams have non-empty real meshes and data URI buffers.
10. Exactly six P0 model IDs with source owner paths.
11. All six FBX entries have valid 64-digit SHA256 LFS object identifiers and declared binary sizes.
12. Git LFS pointer explicitly rejected as model data.
13. Bin FBX Kaydara file signature validation present.
14. Browser SHA256 of local selected file present.
15. No parametric Box/Cylinder/Sphere mesh creation.
16. Exported triangle and mesh-part statistics derive from parsed mesh buffers.
17. All six model repair/Blender/Unity/QA entries remain NOT RUN/PENDING.
18. Complete PR diff path scope is only C01InteriorProps; ship layout untouched.
19. PR #11 is still open draft.
20. PR #11 still targets `codex/c01-ship-integration`, not `main`.

## Source provenance verified
- P17-04 actual PR #23 embedded glTF: Git blob `7df38b63670d34bfc9bb516632346dcba04e1920`, 29 mesh parts, **348 exported triangles**, UV0+normal attributes on all parts.
- P17-05 actual PR #23 embedded glTF: Git blob `4a6d45a0d84086e2bec964545346e150e2137fe2`, 20 mesh parts, **240 exported triangles**, UV0+normal attributes on all parts.
- FBX exports P17-04/05, P18-04/05 and P19-07/08: original owner branches contain Git LFS pointers with model content SHA256. Connector returned pointer text, not FBX binary payload; native binary content **NOT inspected by C01-10**. Exact object SHA and sizes in `p0_original_source_inventory.json`.

## Important distinctions
- **VIEWER_RECONSTRUCTION_DEFECT:** historical six-model gallery used parametric reconstructions. It cannot be used to diagnose original FBX topology. Current viewer never constructs substitute meshes.
- **SOURCE_MESH_TOPOLOGY_DEFECT:** must be proven by mesh source / topology before-after evidence and reviewed by C01-02. No C01-10 source defect falsely inferred from old viewer.
- **Viewer-ready source glTF:** valid stream structure and stats above, but Blender mesh connectivity, non-manifold edges, accidental doubles and T-junctions **NOT AUDITED** by this viewer. Exported vertices may split at UV seams and sharp edges.
- **Browser rendering:** **NOT RUN**; Three.js modules are retrieved from esm.sh at user-browser runtime.
- **Repair count:** 0/6 by C01-10 (owner restriction); 0 signed QA acceptances claimed.
- **W01/W02 accepted-only Unity master:** remains gated; no changes to ship, no new models or merges.

**Final:** SOURCE VIEWER IMPLEMENTED / STATIC PASS / REAL SOURCE IMPORT IN BROWSER NOT RUN / BLENDER NOT RUN / UNITY NOT RUN / INDEPENDENT QA PENDING.
