# P16-02 PASS03 topology repair

Source before GitHub blob: `8cab93e986aabaf2f910cda17eb4a350f433a602`.

Changes: welded 80 duplicate geometric POSITION indices **within** 5 individual components; preserved all source coordinates, triangle faces, face winding, original UV indices and hard-normal directions at individual corners. Independent material parts remain separate. No moving parts.

|Metric|Before|After|
|---|---:|---:|
|vertices|120|40|
|edges|150|90|
|faces|60|60|
|triangles|60|60|
|connected_components|30|5|
|boundary_edges|120|0|
|nonmanifold_edges|0|0|
|degenerate_faces|0|0|
|duplicate_faces|0|0|
|winding_conflicts|0|0|

FBX: original ASCII FBX vertex/index records updated to welded source positions with all source face-corner UV/normal/material layers intact. FBX 7.4 ASCII **NOT NATIVE BINARY BLENDER FBX**. Blender source native .blend MISSING; roundtrip and Unity 6 URP NOT RUN. Unity serialized Mesh assets retain split normals/UV vertex buffers (expected renderer behavior, not independent source topology proof). Inter-part coincident faces/intersections still require scene review. Static face geometry and material/UV loops preserved; not final QA PASS.
