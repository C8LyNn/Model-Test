# T3 Unity integration review

Reviewed the T3 brief/report and Editor + EditTests change set `d7d3913577fc86b92589e1a9bc1f7784768a0d35..e8cf850`. Focused shared Runtime reads checked the builder's gate, lift, button, camera, and socket contracts. No source, index, or HEAD changes and no broad tests were performed for this review.

**Spec verdict: CHANGES REQUESTED.** The authored first-person integration retains the overview camera projection (finding 1). Otherwise the reviewed construction and audit paths substantially implement the contract.

**Quality verdict: CHANGES REQUESTED.** Fix the projection integration and strengthen the promised negative-audit navigation isolation test (finding 2).

**Actual Unity generation/import, EditMode/PlayMode execution, Physics/NavMesh/FBX checks, rendered image inspection, and package export: NOT RUN.** The compile evidence in the implementation report is reported evidence, not independent Unity verification. The primary's separate 17,214-solid source collision audit at gate values 0/.25/.5/.75/1 does not substitute for these Unity checks.

## Findings

### 1. [P1] Walking inherits a ship-scale orthographic camera

**Location:** `UnityProject/Assets/C01ShipV4/Editor/ShipV4Builder.cs:51` (integration with `Runtime/ShipExplorerV4.cs:40`).

The builder sets `camera.orthographic=true` and `orthographicSize=39`. The bound explorer's `SetWalking(true)` reparents the camera to the character and places it at eye height, but never changes the projection; no Runtime code changes `orthographic`. Consequently the actual saved scene's walking view still spans 78 metres vertically at eye height. This prevents the specified first-person walking and physical-button experience even though center-ray button tests may pass. The existing walking/overview PlayMode test checks visibility and framing positions, so it does not catch this integration defect.

**Action:** Make the bound explorer select perspective projection for walking and restore the authored orthographic overview projection when leaving walking. Verify walking FOV and overview framing after a walk/deck switch. Add assertions for both projection modes to the real-scene PlayMode test; retain this item as unverified until that test and visual inspection run in Unity.

### 2. [P2] The saved-NavMesh negative test bypasses navigation entirely

**Location:** `UnityProject/Assets/C01ShipV4/Tests/Editor/ShipV4EditTests.cs:19`, with `:23-24` and `Editor/ShipV4Validation.cs:52`.

`MissingCabinBedIsRejectedAndSavedNavMeshIsUntouched` calls `Reject`, which always invokes `Run(file,false)`. The `false` skips `Navigation`, so the byte comparison cannot detect a regression where the full failing audit overwrites a saved NavMesh during navigation. In addition, `NavAssets()` searches only for pre-existing assets and asserts no nonempty fixture, so a freshly generated scene with no saved NavMesh makes that comparison vacuous. This does not satisfy the brief's meaningful saved-NavMesh isolation test under a negative audit.

**Action:** Use a known saved sentinel NavMeshData fixture (clean it up in `finally`) and run the failing audit through the actual navigation path. Assert both the expected FAIL report and unchanged sentinel bytes, including evidence that navigation was reached. The production audit already uses temporary NavMeshData and removes its handles in `finally`; the issue is the missing regression coverage for that behavior.

## Reviewed implementation strengths and remaining execution gates

- Prism winding is correct for either source XZ orientation: caps face down/up, side normals are chosen from polygon signed area, and triangle vertices are reversed as needed before normal recalculation. Rectangular prisms get matching full-size BoxColliders; other convex prisms get the same mesh as a convex MeshCollider. Mesh updates use setters and `UploadMeshData(false)` while preserving existing asset identity.
- Placement poses are world coordinates under identity groups. Lift car reparenting preserves world pose; car roots and leaf roots receive kinematic bodies. Gate displacement is world-space, and the shared Runtime converts it to leaf-parent coordinates. Buttons resolve real controller references; landings bind their lift and floor; external player/explorer references are assigned in the saved scene.
- Validation checks exact placement/part identity, full native triangle vertex geometry, collider dimensions, prefab links, sockets, content, and control references. Missing floors/ceilings are rejected independently of collision totals through source completeness and coverage rays. Coverage samples use the declared plane and outward direction; clearance rays check actual waypoint headroom.
- The 3D collision hash admits every source collider pair, including same-instance pairs, and calls `Physics.ComputePenetration` at closed/open poses without ownership exclusions. Four explicitly reported lift TRANSPORT links are distinct from claims of continuous walking. Temporary navigation data/links are removed; rendered captures restore renderer, camera, and gate state.
- Host construction leaves existing product/pipeline/quality/color settings untouched and inserts the v4 build scene without removing existing entries. The dirty-scene guard is safe as authored and is not a finding; the primary's explicit preserve-rebuild workflow adjustment is tracked separately.
- Runner stages/failure counts/run IDs/previous scene setup use SessionState, callbacks are registered again on initialization, requests are atomically claimed, test failures block export, and only batch mode exits Unity. Actual callback continuity through PlayMode/domain reload and cancellation still requires the primary's Unity execution; static review cannot establish that result.
- Actual rendered plans, cores, rooms, gates, and lift images must be inspected before delivery. Expected image names and a render manifest are implemented, but neither filenames nor source review proves useful visual evidence.
