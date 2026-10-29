# C01-16 — LIGHTING & SIGNALS, WAVE 01

Target [issue #4](https://github.com/C8LyNn/Model-Test/issues/4) in [master issue #2](https://github.com/C8LyNn/Model-Test/issues/2). Three real modular assets P16-01/02/03 and three beacon visual states via prefab material variants. **No alterations to ship layout, hull, walls, levels, doors, elevators or main scene.**

- Assets/C01InteriorProps/Lighting/Meshes: native Unity serialized mesh assets (Y-up, meters; typed vertices, UV, normals, triangles, material submeshes).
- Assets/C01InteriorProps/Lighting/Materials: URP Lit material with emission, 6 shared materials total, <=3 per prefab.
- Assets/C01InteriorProps/Lighting/Prefabs: 5 native Unity YAML prefab assets with MeshFilter + MeshRenderer + BoxCollider, root scale 1.
- C01Source/Lighting/FBX: experimental **FBX 7.4 ASCII** mesh export, **Unity/Blender import NOT RUN**.
- C01Source/Lighting/OBJ: actual OBJ+MTL triangle meshes.
- C01Source/Lighting/Blender: geometry spec and Blender Python generator; execute to create **genuine .blend and binary FBX** files (not available in current environment).

**Mount orientation:** P16-01 top plane Y=0 facing down into room; P16-02/P16-03 back plane Z=0 facing +Z into room. No dynamic Light components. Emission alone is not a realtime light source. Do not place at door or stair clearance until C01-02 tests.

**Import status:** native Unity YAML and FBX ASCII untested in actual Unity 6 URP. See QA_HANDOFF.md. Local downloadable ZIP has GLB/preview PNG and numerical verification results.
