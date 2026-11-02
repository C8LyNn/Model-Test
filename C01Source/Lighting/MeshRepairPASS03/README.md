# C01-16 / PASS03 / W01

Producer direct GitHub source topology repair of P16-01, P16-02, P16-03. Real OBJ source and ASCII FBX have been modified, no redesign, same triangles, same silhouette. 

**Before / after:** one SVG and two JSON reports per model, rendered from the original GitHub OBJ vertex and indexed face data (not proxy geometry).

Source mesh: per part 8 shared vertex positions, 12 triangles, 18 edges, boundary 0. UV0 and sharp normals preserved as OBJ face-corner records. Unity Mesh render assets remain vertex-split as expected for hard edges. Blender runner at this location generates real native .blend and binary FBX **when run in Blender**, but Blender/Unity not available in producer environment: NOT RUN. Official independent C01-02 QA BLOCKED.

**Known issue:** original FBX 7.4 ASCII export was reindexed and remains unverified by actual importer. Run Blender script to generate binary FBX; for P16-06 rotor child is an animatable Empty at local Y=-0.20.

**Scope:** C01-16 ONLY; no ship scene, architecture or other producer changes.
