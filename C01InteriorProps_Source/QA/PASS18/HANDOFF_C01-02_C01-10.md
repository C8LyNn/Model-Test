# C01-17 / DETAIL PASS18 — PHYSICAL NATIVE QA + P17-03 MOTION P0

**Existing Draft PR #17; source models UNCHANGED; no new parts, no ship changes, no merge.**

## Real native producer binary confirmation
- True Blender4.0.2 [run #41347796593](https://github.com/C8LyNn/Model-Test/actions/runs/41347796593), original artifact **#13099877855** (ZIP CRC PASS; SHA256 `2ddab5c829475d29a8e22cdde37861de43e4e2eaf9f67f2dc46c25f86afccd51`).
- Re-read 3 real `BLENDER-v400` files + 3 real `Kaydara FBX Binary 7400` files; full byte SHA256 of each equals current producer Git LFS OID; NOT historical 20-part exports.
- Independent direct binary indexed audit **83/83 mesh instances and 1,340 triangles**, 0 bad indices, 0 degenerate faces, 0 boundary/nonmanifold/winding errors, all UV0 and per-corner normal indices valid. Actual Blender-source↔FBX audit in producer workflow shows exact triangle parity. Breakdown **P17-01 25/380**, **P17-02 38/536**, **P17-03 20/424**.
- Actual 3D triangle-edge crossing mechanical mounts from hydrated FBX: **P17-01 7/7** tested (2 guides, Backbone, 4 screen bolts); **P17-02 7/7** tested (4 screws, Keybed, 2 clamp reinforcements). Original P17-01 repaired guides and 4 P17-02 screws remain physically seated.

## NEW VERIFIED P0 DYNAMIC HOLD — P17-03
- Binary FBX real Model hierarchy **PASS**: `LeverPivot` parents `LeverShaft`, `LeverGrip`, `PivotAnchorVisual`, while all PASS15 new fasteners are stationary children of ROOT. No change of pivot or original geometry.
- Executed independent kinematic sweep using exact hydrated FBX triangle vertices, pivot world `[0, 0.35, -0.015]m`, world +X rotation **−45°..+45° every 5°**. **456** moving part / new stationary fixture AABB pair checks, **0** overlap candidates.
- However the existing `LeverShaft` **physically intersects actual faces of solid `TopCap` and `LeverSocket`**. Actual edge/triangle narrowphase: at **0°** shaft–TopCap **26 crossings**, shaft–LeverSocket **52 crossings**; **45°** 26 and 46. At −45° 24 and 46. The pivot visual also cuts TopCap at rest (10 triangle crossings).
- **Not an imaginary AABB overlap:** source physical world intersection witnesses near `[0.014,0.361,-0.015]m` (TopCap) and `[0.014,0.3865,-0.015]m` (LeverSocket). This may be an *intended visually concealed embedding* at rest, but with animated sweep and solid geometry it requires explicit mechanical clearance review and likely hole/slot geometry before genuine Unity motion acceptance.
- P17-03 **STATIC SOURCE/FBX PASS; DYNAMIC P0 HOLD**. Do **not** label 3/3 FINAL APPROVED or merge.

## Artifact, preview and next gate
Download physical `C01-17_PASS18_NATIVE_MOTION_QA_DELIVERY.zip` **5,810,998B**, SHA256 `eea3b0df2af64e8a0df74ceb3d1306ef907062419825a64034b90b6d70f2b55c`, ZIP CRC PASS. Contains all 6 actual latest Blender-origin binaries, independently measured JSON QA, reproducible Python motion/test scripts, exact current FBX 3D interactive shaded/wireframe HTML (slider −45 to +45, not old FBX), real Blender BEFORE/AFTER PNG comparisons and actual-triangle collision diagram. Viewer JavaScript syntax check PASS; full Chromium GUI smoke NOT RUN (headless launch timeout); neither view is Unity.

**Next action C01-17:** produce a purpose-designed through-clearance / slot for the moving shaft in existing TopCap + LeverSocket if C01-02 agrees; preserve fasteners/pivot and all existing parts. Re-run Blender4 native save/export/roundtrip, 5° sweep and C01-02 full independent SHA review. **C01-10:** do not activate P17-03 movable gameplay prefab until clearance resolved; actual Unity6 URP import/material/collider/PlayMode **NOT RUN**. C01-02 should independently confirm fixture contacts and evaluate intended internal intersections. Only C01-02 and C01-10 may advance final release gates.
