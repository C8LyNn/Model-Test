# C01-18 — Interior props WAVE 01

Base: codex/c01-ship-integration; change scope confined to Assets/C01InteriorProps/C01-18 (NO ship modifications). Issue #6 / global issue #2.

Deliverables: three REAL polygonal meshes OBJ/MTL, FBX ASCII 7.4, editable Unity serialized prefabs, shared URP material YAML, part specification and Blender conversion script. Blender native .blend MISSING until builder run. Import of ASCII FBX and serialized Unity prefabs NOT RUN; cannot pass independent QA yet. Corresponding downloadable external ZIP includes validated GLB geometry and 9 PNG geometry previews. Unity/Blender screenshots NOT claimed.

| Model | Bounds W/D/H m | Triangles | Mesh parts |
|---|---|---:|---:|
| P18-01 crate | .9/.9/.9 | 180 | 15 |
| P18-02 rack | 2.1/.8/2.1 | 204 | 17 |
| P18-03 cart | 1/.7/1.2 | 348 | 17 |

P18-03 has 4 wheel children at axle pivots. BoxCollider components on intended structural segments. Root position at floor Y=0 and scale (1,1,1). The scene and corridor clearance cannot be validated without Unity ship scene.

Requested C01-02 QA: Blender import, FBX binary regenerate, Unity 6000.3.14f1 URP import, normals/materials, scale/pivots/colliders, actual ship door/elevator/corridor clearance. C01-10 integration only after QA. Do not merge draft PR before these blockers are resolved.
