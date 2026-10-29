# C01-10 — Interior Props integration / WAVE 01

**Scope:** issue #9, parent #2. Base: `codex/c01-ship-integration` (draft PR #1), not `main`.

## Current status: BLOCKED ON 16 SUPPLIER ASSETS

The integrator is real Unity Editor C# source. As of 2026-10-29, the base branch does **not** contain `Assets/C01InteriorProps` or the 16 P15-01–P19-04 supplier packages. The 16 input meshes, native Blender sources, Unity prefabs, and Unity screenshots have **not** been produced by C01-10. C01-10 must not invent replacement geometry owned by C01-15–19.

**Unity Editor / Blender not installed in the present execution environment**. Consequently, no Unity build, prefab compilation, screenshot or PlayMode result has been claimed.

## Input staging (individual supplier PRs first)

Merge/rebase individually reviewed supplier PRs #3–7 onto this integration branch. Each asset must have a stable unique prefix `P15-01`, `P15-02`, etc., and include:
- exactly one `Pxx-yy*.fbx`, **with imported actual MeshFilter**;
- exactly one `Pxx-yy*.blend`, native Blender source;
- at least three `Pxx-yy*.png` or JPG previews from distinct angles;
- supplier manifest with dimensions, Y-up origin, mount, material slots, collision, triangle count, version.
  
Recommended staging path: `Assets/C01InteriorProps/Incoming/Pxx-yy/Pxx-yy_{source.blend,export.fbx,front.png,side.png,iso.png}`. The builder scans `Assets` for **exactly** this ID prefix and will reject duplicates; it excludes its own Generated folder.

### Unity 6 URP invocation

1. Open **the project at the branch which contains all 16 supplier assets**, and allow Unity to import FBX models.
2. Menu: `C01 > Interior Props > Preflight (16 real assets)`. Read `C01InteriorProps_QA/PREFLIGHT.csv` outside Assets.
3. Fix missing/duplicate FBX and .blend, zero/invalid mesh, unusually-sized geometry, non-unit root scale and missing three-angle previews at their owner. No automatic retopology or mesh recentering is performed.
4. Run `C01 > Interior Props > Build Showcase + Cabin + Technical`.
5. Unity creates the following **only after all 16 real inputs pass preflight**:
   - `Assets/C01InteriorProps/Generated/Prefabs/P15-01.prefab` ... `P19-04.prefab`;
   - `Assets/C01InteriorProps/Generated/Prefabs/C01_InteriorProps_Showcase_MASTER.prefab`;
   - `Assets/C01InteriorProps/Generated/Scenes/C01_InteriorProps_Showcase.unity`;
   - `Assets/C01InteriorProps/Generated/Scenes/C01_InteriorProps_Cabin.unity`;
   - `Assets/C01InteriorProps/Generated/Scenes/C01_InteriorProps_TechnicalRoom.unity`.
6. Commit Unity-generated prefabs/scenes and their `.meta` files in a follow-up commit **with real Unity evidence**; do not claim these files exist before building.
7. Independently validate via C01-02 (#8), then request C01-00 acceptance.

## Implementation guarantees and limitations

- Imported FBX geometry remains unchanged: no vertex edits, no automatic change of pivot/rotation/scale.
- Every individual generated prefab keeps its FBX as a nested model prefab instance; a conservative BoxCollider is added on the wrapper as a **provisional QA candidate**. Validate final collider clearances in Unity, especially doors and moving components.
- Real-world dimensions are checked in Unity with provisional 0.20 m max deviation per axis. C01-01/C01-02 may mandate a tighter tolerance. Floor roots require mesh minimum Y within 0.05 m of zero.
- Showcase is a **standalone inspection scene**, not inserted into the ship. Layout groups are Installations/Lighting/Controls/Cargo/Furniture. Empty x=-1.5..1.5m lane is only a diagnostic 3m reference strip, **not a verification of the actual ship corridor**.
- Separate Cabin/TechnicalRoom scenes use clearly named `REFERENCE_ONLY_*` greybox floor/wall fixtures. They are not part of the sixteen supplier assets, and nothing overwrites `Assets/C01ShipV4`.
- Model mount orientation, prefabs' absolute clearances in the real ship, sliding gates and elevators, and Blender sources **require review**. Do not deliver to production without real QA.

## Owner handoff

- C01-15 (#3): P15-01..03 (pipe, grille, cabinet)
- C01-16 (#4): P16-01..03 (lightbar, emergency lamp, beacon)
- C01-17 (#5): P17-01..03 (console, keypad, lever)
- C01-18 (#6): P18-01..03 (crate, rack, cart)
- C01-19 (#7): P19-01..04 (bunk, locker, desk, chair)
- C01-02 (#8): independently test model dimension, pivot, normals, URP materials, colliders, door & corridor clearance, source file proof, and all 3 generated Unity scenes.

## Test status

- GitHub repo/PR baseline inspection: PASS (PR #1 is an open draft).
- Missing input directory in base branch: CONFIRMED.
- Builder source submitted on isolated branch: PASS.
- Unity compilation / imports / prefabs / screenshots / PlayMode: **NOT RUN**.
- Blender source roundtrip / native export: **NOT RUN**.
- Independent C01-02 QA: **NOT RUN**.
- Definition of Done: **BLOCKED**, not accepted.
