# C01-19 — Independent QA Handoff

- Owner: C01-19; scope: P19-01, P19-02, P19-03, P19-04 only.
- External geometry: four candidate OBJ furniture models as 37 mesh parts, with exact analytic dimensions and three SVG views each.
- Blender: **NOT RUN**; the .blend and FBX are not currently in this PR.
- Unity 6 URP: **NOT RUN**; run `Tools/C01/Build furniture prefabs` in Editor to generate and then commit .prefab files.
- Static local test: mesh extents, floor Y=0, watertight per part, positive volume, finite vertices, four material families, part identity: PASS for all four models. This is not independent QA.
- Required C01-02: Import 4 models, validate normals and scale 1, door hinge, collider layer, non-blocking 3m corridors and elevator/door clearance; inspect shaders and meshes; report PASS/FAIL.
- Required C01-10: Integrate in separate C01_InteriorProps_Showcase scene and one small cabin; don't edit the ship scene or master prefab.
- Production ship layout: **unchanged**.
