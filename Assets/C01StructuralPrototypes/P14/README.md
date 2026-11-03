# C01-14 — STAIRS & STRUCTURES / optional reference assets

**Status: PROTOTYPE / UNASSIGNED IN INTERIOR PROPS WAVE 02 — NOT APPROVED.**
Two real, small structural mesh prototypes are authored separately from the 16+20 props assigned to C01-15–19.
Do not count RMP-01/RAI-01 toward the Interior Props release gate. This PR must remain draft until a separate C01-00/C01-01 scope + interface decision.

## Deliverables
- RMP-01, straight 4×1 m maintenance ramp, 1 m rise (25% grade). Y-up reference bbox [0,-0.2,0]–[4,1,1]. Source geometry: 60 visual triangles including yellow top markings. Dedicated collision deck mesh.
- RAI-01, level platform guardrail, 2m long × 1.10m high, 0.10m width. Bbox [0,0,-0.05]–[2,1.10,0.05]. 48 visual triangles. Do not mount on RMP-01 incline.
- `Tools/C01Structures14/generate_blender.py` reproducibly authors real native .blend, binary .fbx, UVs and 3 reusable materials from Python geometry through Blender.
- `.github/workflows/c01-14-reference-blender.yml` builds and uploads downloadable binary .blend/.fbx + hashes (check Actions success before claiming these exist).
- `Assets/C01StructuralPrototypes/P14/Editor/C01Structures14PrefabBuilder.cs` authors two individual Unity 6 URP prefabs + URP Lit materials + static mesh/BoxColliders **when executed in Unity**. This PR does not contain fabricated prefabs.

## Independent test evidence (offline only)
Locally built real GLB and OBJ versions + 6 projected mesh previews are included in the separate `C01_14_STRUCTURAL_PROTO_W02.zip` user-delivered conversation artifact. Real mesh checks: watertight component meshes, positive closed volumes/winding, bounds, finite vertices, GLB read-after-write, and GLB UV streams. **These tests do not count as FBX import or Unity tests.**

## Gate
- G0/ownership: BLOCKED — C01-14 has no assignment in WAVE 02; C01-01 structural slot/socket approval missing.
- G1 source mesh: PASS locally (GLB/OBJ only).
- Blender native source / binary FBX: NOT RUN locally; check workflow run for actual status.
- Unity 6 URP prefab creation, Play Mode, corridor/door/elevator clearance: NOT RUN.
- Independent C01-02 QA / C01-10 integration: NOT RUN.
- No base ship scene, hull, layout, decks, stairs, doors, corridors or elevators modified.

**Follow-up:** only after explicit separate acceptance test, C01-02 audits Blender/FBX geometry and Unity prefabs; C01-10 tests traversal/headroom in an isolated environment. Ramp requires an elevated platform/compatible route and is not a normal stair replacement.

For Blender directly:
```sh
blender --background --python Tools/C01Structures14/generate_blender.py -- --out Assets/C01StructuralPrototypes/P14
```
To generate Unity prefabs, import generated FBX into the indicated FBX folder, open Unity 6 URP and run `Tools/C01/Structures 14/Build reference prefabs`. Do not add these objects to the live ship without authorized layout compatibility verification.
