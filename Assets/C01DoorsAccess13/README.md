# C01-13 — Gate / Access accessory clearance preflight (WAVE 02)

**Ownership:** C01-13 (doors & access), *integration-only helper*. No P15–P19 asset was assigned to C01-13. Do **not** treat this package as a seventeenth model or as a replacement for P17-02/P16-07.

## Verified existing source integration (branch `codex/c01-ship-integration`)

- Existing ship gates use `C01.Ship.V4.ShipGateV4` with **sliding** `leaves[]`, `travel[]` in world space and `openness` in [0,1]. They are NOT the legacy hinged D01/D02 prototypes.
- `ShipButtonV4.Press()` handles gate, lift and optional airlock; visual replacement of P17-02 should be bound by integrator without bypassing interlocks.
- Existing `P_Button.prefab` contains a `0.22×0.28×0.09m` body collider; this is not the `0.18×0.07×0.28m` replacement P17-02. P16-07 is future visual indicator (owner C01-16).
- All new props must mount to **fixed surfaces**, never moving gate leaves. Do not alter ship geometry or placement in this PR.

## How to run in Unity 6 URP (not yet executed)

1. Checkout this branch within the Unity 6 ship project; allow Editor compilation.
2. Open an **isolated test scene** with actual ShipGateV4 sliding gates and supplier P17-02 / P16-07. To audit just one prefab hierarchy, select its root; with no selection, the tool inspects the active scene.
3. Use `Tools > C01 > Doors & Access > Audit Gate-Accessory Clearance`.
4. Inspect `Library/C01Doors13/access_sweep_audit.json` and Console. Commit report and screenshots to C01-02's QA branch only **after running** the tool; do not commit fabricated evidence.
5. If `POSSIBLE_SWEEP_INTERSECTION`, inspect exact colliders at gate openness 0, .25, .5, .75, 1.0 in Unity. The broadphase computes the translated collider **AABB union** expanded by 0.02m on each side. It does not determine actual contact, pathfinding, accessible button reach, airlock interlock behavior, or Unity runtime physics.
6. If `INCOMPLETE_*`, supply active colliders, complete `travel[]` or actual suppliers; never turn `INCOMPLETE` into PASS. `INFO_UNVERIFIED_BINDING` requires integrator to confirm wiring to an existing ShipButtonV4 or equivalent interaction.
7. Test 3m corridors, player capsule traversal, gate slide and access button interactability in PlayMode **separately**. Request C01-02 independent QA before merge.

**Known limitation:** if a gate leaf was manually moved without updating its serialized `openness`, sweep coordinates can be wrong. Always validate scene at a known gate state. `Collider.bounds` is conservative for rotated boxes, and diagonal sliding travel produces a conservative bounding region (can raise false positives). The tool intentionally never writes to a prefab or scene.

## Scope / Evidence

- C# Editor utility is real source code. No mesh, .blend, FBX or Unity prefab is authored by C01-13 in this wave, because all 20 Wave02 props belong to C01-15–19.
- Python tests are deterministic synthetic geometry fixtures, **not Unity or asset QA**.
- Unity import, code compilation, PlayMode and independent QA: **NOT RUN** from this ChatGPT runtime.
- Parent #2: 0/16 formally accepted at last checked QA status; do not merge this PR before independent review.
- Refer issues #2, #4 (P16-07), #5 (P17-02), #8 (C01-02 QA), #9 (C01-10 integrator).

**Result classification:** `SOURCE_DELIVERED / UNITY_NOT_RUN / QA_PENDING`.

## DETAIL PASS12 — real P17-02 mesh envelope guard

- **Implemented in existing Editor audit**: the gate/access sweep now combines actual **enabled Collider.bounds AND Renderer.bounds**, not just nominal root BoxCollider bounds. For a P17-02 it also separately compares renderer against collider and reports `ERROR_READER_VISUAL_COLLIDER_MISMATCH` if any world-AABB edge exceeds the collision envelope by more than 30 mm. `STATIC_BROADPHASE_CLEAR` is suppressed when a mismatch exists; the report includes `visualColliderMismatches`. This is a conservative screen (rotated meshes can make AABBs too large); never interpret it as exact physical collision or Blender topology PASS.
- **Why**: at historical P17-02 source Git SHA `79d8dcd3c7a4e39a7a3bcb3c88551642bf52d191`, source glTF expanded detail had four enormous visual screws (decoded POSITION ±1 m) while a nominal reader box collider remained 0.18×0.28×0.07 m. That historical defect was subsequently reduced by producer edits. Always pin the exact glTF SHA.
- Current later P17-02 glTF blob `7f183922dab2b5e416af7a8dc30a46c1b6990286`: reader full AABB is back to 0.180×0.280×0.070m. Separate source check finds each screw ~0.81×1.26×0.048mm and **0.976mm off the mount backing**, while Keybed is **0.5mm off the Housing**. These remaining tiny-gap issues are **not** detectable by the oversized-envelope check; C01-17 must seat the actual nodes and re-export native files. No fake Unity PASS.
- Legacy 9 broadphase fixtures + 4 new P17-02 source-snapshot envelope regression fixtures are included in the existing Python reference suite. **13/13 local math-mirror checks PASS** as of PASS12; Unity Editor compilation and real 3D mesh inspection remain **NOT RUN** here.
- C01-13 did not edit C01-17 producer meshes and did not modify any ship geometry. These are producer findings and a fail-closed integration guard, not formal independent C01-02 acceptance. The P17-02 producer handoff is in [PR #17](https://github.com/C8LyNn/Model-Test/pull/17#issuecomment-6532042326) and [detail issue #36](https://github.com/C8LyNn/Model-Test/issues/36#issuecomment-6532043776).
