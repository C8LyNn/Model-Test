# C01-19 / WAVE 01 — Real furniture mesh delivery

Issue #7. Original ship: PR #1; no ship scenes or structures changed.

4 models, 37 independently importable low-poly triangular OBJ pieces. Each individual OBJ contains 8 positions, 12 triangle faces (closed cube); pieces form the four detailed furniture assemblies described by Source/parts.json. SVG previews computed from these geometric recipes, not from Unity. Blender .blend/FBX and Unity .prefab are **MISSING / NOT RUN**, until their generators run on machines with installed Blender/Unity. Do not mark integration passed.

| ID | Name | Size XYZ in m | Triangles |
|---|---|---|---|
| P19-01 | Single crew bunk | 0.95 × 0.65 × 2.1 | 132 |
| P19-02 | Crew locker | 0.65 × 1.8 × 0.55 | 108 |
| P19-03 | Computer desk (without terminal) | 1.4 × 0.75 × 0.65 | 96 |
| P19-04 | Industrial chair | 0.6 × 0.95 × 0.6 | 108 |

UNITY: run Editor/C01FurniturePrefabBuilder.cs from Tools > C01 > Build furniture prefabs, then verify generated prefab assets. BLENDER: run Source/blender_export.py with Blender 4.x to create native blend and FBX, then verify them. Keep 3-meter corridors, door arcs, elevators/stairs clear; QA must independently inspect clearance.
