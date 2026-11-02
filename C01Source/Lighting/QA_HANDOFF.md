# C01-16 / Issue #4 — QA & integration handoff

Three meshes and five Unity prefabs committed; raw geometry FBX 7.4 ASCII and OBJ+MTL committed; local downloadable ZIP additionally contains GLB and 3-view PNG geometry renders.

**Verified locally (static only):** AABB dimensions, 60 triangles/120 vertices per mesh, UV range 0–1, material groups <=4, OBJ/GLB generation, root scale 1, native Unity Mesh YAML syntax and .meta existence. Native .blend **MISSING** because Blender is not installed; Python Blender script provided and must be executed on Blender workstation. Native Blender binary FBX and FBX SDK/Unity FBX import **NOT RUN**. Native Unity prefab and URP Lit material import **NOT RUN**, so no assertion of Unity PASS.

**C01-02:** run Blender binary regeneration, open .blend and each FBX, compare bounds, run Unity 6000.3.14f1 URP import and preview prefabs, check 3 beacon material states, normals, collider and placement. Report defects on PR; no architecture edits.

**C01-10:** integrate *after QA* in separate Showcase. Ceiling P16-01: pivot Y=0 and body down to Y=-0.12. Wall P16-02: pivot at local wall Z=0 and protrusion 0.14m. Wall P16-03: protrusion 0.2m. No ship or scene geometry modified. A 3m corridor with P16-02 and P16-03 mounted opposite sides has at least 2.66m geometric width if both project their full depth; diagram in local ZIP is a planning illustration, NOT Unity evidence.

**Status:** Static geometry PASS; acceptance BLOCKED until native Blender sources/Unity runtime/independent QA.
