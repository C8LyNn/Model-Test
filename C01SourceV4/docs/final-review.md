# Final feature review — C01 v4.0

Reviewed 2026-10-29. Source scope: the complete feature through `7510ab3` on `codex/multideck-v4`, including the integration corrections in `10142a6` and `956f494`. Read `spec.md`, `contract.md`, `README_PL.md`, prior reviews/re-reviews, every Python file in `Tools`, the Python tests, and all v4 Runtime, Editor and test sources/assemblies. This reviewer did not modify implementation, assets, Git index or HEAD, launch Unity, or repeat broad tests. Only this document was written.

## Verdict

**Spec verdict: APPROVE the reviewed feature source. Quality verdict: APPROVE. No outstanding actionable findings.** The confirmed dimensions are consistently interpreted as counts of 3 m squares, and the three-deck geometry, editable delivery sources, physical gate controls and moving elevators implement the accepted scope. Final packaging, upload and the primary's verification of the last cosmetic commit remain delivery work, rather than source defects.

## Assessment

- The generator provides 24 nominal 9×9 m cabins, each with four separate beds, eight lockers and a 6×3 m bathroom. The residential corridor plan repeats on deck 2; deck elevations are −12.4/0/6.4 m, cabin/corridor clear heights are 6 m, and sector clear heights are 12 m. The 12 m stern, enlarged polygonal bow, upper galleries, five exterior engines, lower machinery/purification/plants/hangar and editable escape craft are present.
- Walls merge vertical ownership before gate envelopes are subtracted. Separate nodes own intersections; slabs exclude crossing structure and elevator shafts. Shared structural floors supply ceilings where appropriate. The independent Python surface audit derives its target regions from the accepted plan rather than placement identifiers or generated coverage metadata. Prior focused mutation evidence establishes detection of empty, shortened and deleted slabs in residential, bow, core-roof and exterior-pad regions.
- Actual first-hit button raycasts dispatch interactions; hitting a gate leaf does not operate it. Eight staggered leaves retract while frames remain stationary. Airlocks close the opposite gate before opening and handle cancelled/repeated requests. Both three-stop lifts shut landings before motion, reject away-landings, move their platforms continuously, and carry a grounded CharacterController using car displacement. The enabled walking/gravity regression fills the earlier controlled-test coverage gap.
- The saved scene records lift/player overrides after creating the master prefab; runtime binding supplies the same relationship at startup. FBX validation now preserves the imported asset's axis-correction root transform. The passage regression uses the aperture midpoint rather than the frame origin. Missing keyboards gate input reads without preventing gravity.
- Native module prefabs retain separate source parts, matching colliders and nominal sockets. The Blender pipeline retains editable source models and assembly instances and creates actual FBX, OBJ, BLEND and complete GLB outputs. The Unity builder keeps the host rendering configuration and existing build scenes. The asynchronous runner restores saved scene setup, preserves explicitly requested dirty-scene snapshots, and exports only after successful checks.

## Findings resolved during this review

1. Zone TextMesh floor labels were enabled by generic renderer restoration, so `L` hid only the GUI copy. `7510ab3` keeps editor floor labels disabled during runtime while preserving physical button labels. Capture explicitly enables the selected floor labels for plan images. The walking regression now separately requires non-zone renderers enabled and zone text renderers disabled; this avoids the previous all-renderers assertion conflicting with the correction.
2. The documented complete-project Python test command originally looked only under a nested `UnityProject`. `7510ab3` imports the shared `PROJECT` resolver, supporting the standalone source tree and `Model Test/C01SourceV4` with parent `Assets` consistently.

Both corrections are approved in source. No further important missing test was identified in the reviewed scope.

## Evidence inspected

These are results produced by the primary and inspected by this reviewer, not tests independently rerun by this reviewer.

| Evidence | Observed result |
|---|---|
| `QA/python_v4.log` | 8 tests PASS |
| `QA/layout_v4.json` | 2,250 independent surface regions, 0 gaps, 0 missing area; 98 connected zones |
| `QA/geometry_v4_0.json`, `geometry_v4_1.json`, `gate_intermediate_poses.json` | 17,218 source solids, 0 penetrations at gate poses 0/.25/.5/.75/1 |
| `QA/blender_v4.json` | Blender 5.2.2 LTS; 181 models and actual FBX round trips PASS; 4,304 assembly placements |
| Live `Model Test/C01ShipV4_QA/unity_v4_qa.json` | Unity 6000.3.14f1 PASS; 4,304 placements, 17,218 collider parts, 0 penetrations, 13,507 coverage rays, 98 clearance rays, 181 imported FBX models, 98 reachable zones, four labelled lift transport links |
| Live `editmode.xml`, completed 18:54:28 UTC | 8 passed, 0 failed, 0 skipped |
| Live `playmode.xml`, completed 18:56:25 UTC | 7 passed, 0 failed, 0 skipped, including enabled walking gravity on both lifts |
| Actual Unity renders inspected | `deck2_plan.png`, `bridge_vertical_core.png`, `gate_open.png`; consistent with the intended gallery, shaft and aperture geometry |

The complete Unity suite results above precede the small label/test-path commit `7510ab3`. Its source and dependent assertion were reviewed; the primary is verifying that synchronized final revision before final export. This report does not claim that later verification has already completed, or that the Drive delivery has already been uploaded.
