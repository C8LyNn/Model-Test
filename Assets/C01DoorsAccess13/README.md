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
