# C01-16 Wave02 / delivery and QA

Branch: c01/props-16-lighting-wave02. Depends on producer Wave01 PR #12 for final integration approval.

- P16-04: 1.8×0.85×0.12 m; 84 triangles; Steel, DarkPanel, EmissionWhite; ceiling / top Y=0
- P16-05: 0.9×0.09×0.3 m; 84 triangles; Steel, DarkPanel, EmissionWhite; wall / back Z=0
- P16-06: 0.28×0.28×0.36 m; 108 triangles; Steel, DarkPanel, EmissionRed; ceiling / top Y=0
- P16-07: 0.34×0.08×0.17 m; 60 triangles; Steel, DarkPanel, EmissionGreen; wall / back Z=0

Mesh YAML, prefab YAML, 6 URP emission materials, OBJ/MTL, ASCII FBX and mesh-derived SVG previews present in this PR. Local ZIP also contains GLB, geometry PNG views and checksums.

REAL BLEND FILES: MISSING — Blender binary is not installed. Unity runtime: NOT RUN. FBX importer roundtrip: NOT RUN. QA independent: NOT RUN.
P16-06 rotor child has local pivot Y=-.20 and is separately animatable. P16-07 material variants Green=AVAILABLE, Red=BLOCKED, Amber=FAULT.
No existing ship layout, corridor, door, engine, elevator or scene files modified. Do not merge until C01-02 validates and C01-10 checks clearance.

## Producer repair (2026-10-30): P16-06 rotor swept-envelope
Support x-coordinate moved from ±0.116m to ±0.130m; rotor top, lens and drum reduced to fit. Max rotor corner radius around Y (in XZ projection) is 0.113252m; inner support plane is 0.123000m; calculated radial clearance 9.748mm. Local ZIP rebuilt with updated geometry and static GLB checks. This is geometric preflight only; Unity swept animation and actual physics are still NOT RUN.
