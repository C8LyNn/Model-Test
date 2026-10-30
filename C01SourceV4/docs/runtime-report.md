# T2 runtime report

Status: initial actual Unity PlayMode run by primary **FAILED: 5 passed, 2 failed**. The keyboard-independent gravity correction below is C# compile checked; its Unity rerun is **NOT RUN** by this worker and remains with primary. This worker made no live Model Test edits.

## Runtime behavior

- `ShipGateV4`: eight independently referenced leaf transforms; world travel converted into parent-local displacement; serialized closed-position cache prevents repeat/reset drift; kinematic leaf rigidbodies; immediate setters clamp and synchronize openness/target/physics. Frames are never animated.
- `ShipButtonV4`: lift dispatch has priority, otherwise airlock cancellation/toggle or ordinary gate toggle. Buttons carry `gateId`, `liftId`, `floor`, `gate`, `lift`, `airlock` fields.
- `ShipAirlockV4`: close the opposite gate completely before opening the requested gate. Pending requests can be cancelled and replaced, including while the opposite gate closes.
- `ShipLiftV4`: closes all landings before travel, moves the car continuously at 4 m/s, and opens only the aligned landing after stopping. Ground rays must hit a car descendant before a CharacterController receives its movement delta. Upward capsule motion precedes raising the platform to avoid overlap recovery adding an extra push; downward motion follows lowering the platform. QA reset moves only the car and closes all landings. Repeated, invalid, cancelled and redirected calls cannot open away landings.
- `ShipExplorerV4`: InputSystem keys 1/2, WASD/RMB, actual button-only raycasts, R roofs, L labels, deck 0/1/2/All GUI, deterministic overview reset. Cutaways change Renderer.enabled only, use zone floor elevations, hide higher deck geometry/upper slabs/roof/ceiling/hull/shell categories. Walking restores all renderers and roofs.

## Builder integration API

Use existing contract fields unchanged. Additional runtime fields/methods:

- `ShipGateV4.interlockAirlock`, `.interlockLift`, `.landingFloor` are serialized references; ownership also binds lazily when controllers start or receive requests. Assign before scene/prefab save for immediately reviewable references.
- `ShipGateV4.SetTarget(bool)` is **internal**, for same-assembly lift/airlock controllers only. It deliberately does not call `SetOpen`, avoiding recursive controller routing; it still refuses unsafe lift opening. Editor code should use public `SetOpen`/`SetImmediate` and wire interlock references, rather than calling this internal method.
- `ShipGateV4.IsClosed`, `ShipLiftV4.CanOpenLanding(ShipGateV4)`, `ShipAirlockV4.IsRequestedOpen(ShipGateV4)` and `.CanOpenImmediately(ShipGateV4)` support the safety state machines.
- `ShipLiftV4.footprint` is a `Vector4(x0,x1,z0,z1)` in world coordinates from manifest bounds. It is an extra rider filter; actual ground contact with a car collider is always required.
- Set `car`, three `landings`, `elevations`, `player`, `footprint`, then `ResetToFloor(startFloor)`. Initial car pivot y=0 and model parts are initial world coordinates. The reset leaves aligned doors closed until summoned/selected.
- Populate explorer references and 1.8 m / radius .28 m CharacterController at L1 bridge near (-1.5,.02,22.5). Controller transform is at its feet, with center y=.9. Zone markers provide deck floors and label positions. Gate passage tests interpret manifest yaw through `Quaternion.Euler(0,yaw,0)*Vector3.forward` as the gate normal.

No shared ShipDataV4 changes were made by T2. Primary has now split the three MonoBehaviour marker classes into matching individual .cs files for Unity MonoScript serialization.

## Verification evidence

- **PASS, static C# compilation**: Unity's `DotNetSdkRoslyn/csc.dll`, invoked with dotnet `/nostdlib+ /target:library /langversion:latest`, references installed Unity 6000.3.14f1 engine modules, 4.8 API/netstandard facade, host InputSystem assembly. Compiled all runtime sources, including the shared data source, then the PlayMode assembly using installed NUnit and UnityEngine.TestRunner. Exit 0; no compiler diagnostics. This verifies C# type/API compatibility, not Unity import, asmdef resolution or physics.
- Seven scene-based tests load `C01_Ship_Multideck` from build settings and read the actual manifest, with no surrogate scene geometry or mocked controllers. Initial primary-run results are recorded below:
  1. reversible immediate leaf travel, synchronized target and stationary non-leaf instances;
  2. actual button raycast, panel-hit rejection, closed gate obstruction and open passage with the real CharacterController;
  3. paired airlock controls, repeated/cancelled requests and a both-gates-open invariant;
  4. both lifts continuously carry the real player to floors 2/0/1, correct world heights, away landing interlocks and aligned opening;
  5. midtravel redirected/repeated calls and reset leave an unrelated nearby player unmoved;
  6. selected-deck overview reset framing, collider preservation and full walking renderer restoration.
  7. enabled walking explorer applies real gravity to settle the player on each manifest-defined car, rides both shafts through floors 2/0/1 with no manual movement after setup, checks away landing openness/targets every rendered frame, verifies continuous car travel and rider contact/alignment, and keeps gravity running after each arrival to catch a delayed fall.
- Initial tests were authored before runtime implementation. Primary's first actual run now provides red evidence for walking gravity; the green rerun for the correction is pending. No passing claim is made for the full runtime suite.
- Initial legacy Mono compiler launch failed loading `System.Text.Encoding.CodePages`; the installed dotnet Roslyn compiler was used successfully instead. No source changes were needed for that tool environment issue.

## Remaining concerns

Actual scene colliders, panel pocket clearances, gate normal convention, car floor top height, rider skin-width behavior and runtime frame timing must be verified in the primary's Unity run. The tests intentionally fail on missing/incorrect scene integration rather than silently skipping it. Overview categorization expects manifest categories to contain roof/ceiling/floor/hull/shell where applicable.

Follow-up to `docs/runtime-review.md`: the enabled-explorer regression fills the walking-gravity coverage gap using the generated manifest shaft centers (-4.5/67.5,22.5). It first proves real gravity is running by requiring an elevated capsule to fall and ground, rather than merely asserting the explorer's enabled flag. That test-only follow-up did not change runtime implementation. Static C# compilation was repeated for the updated test; scene execution was pending primary integration at that stage.

Projection integration correction: the Editor builder initializes an orthographic overview, so walking now explicitly selects perspective with a 65-degree field of view. The explorer serializes the saved overview projection, orthographic size and field of view; `ResetView` restores them alongside framing, and repeated walking calls cannot replace them with walking settings. The overview-reset regression now changes projection/size/FOV before reset, verifies restoration, switches into perspective walking twice, and verifies the overview again after returning. The active walking lift regression explicitly checks perspective/FOV as well. C# compilation passed; the overview test subsequently passed primary's first actual Unity run.

## Actual Unity failure and scoped correction

Read evidence: `C:/Users/kubap/Documents/GitHub/Model Test/C01ShipV4_QA/playmode.xml`, run 2026-10-29 18:49:06–18:50:39 UTC. Airlock controls, controlled both-lift transport, immediate gate reversibility, unrelated-player/cancellation and overview reset **PASSED**. `WalkingExplorerGravityKeepsPlayerAboardBothLiftsAcrossAllFloors` **FAILED** with "Walking gravity never settled the player onto LIFT_BRIDGE". `PhysicalButtonOpensGate_ClosedGateBlocks_OpenGatePasses` independently **FAILED**, opened passage signed position -.509999216 instead of >.65; primary is diagnosing that source/test integration and this scoped correction does not touch the gate test.

Root cause for walking gravity: `ShipExplorerV4.Update` returned before gravity when `Keyboard.current` was null in the no-device Unity batch run. The correction guards only optional keyboard reads and supplies zero movement axes when no keyboard exists. Mouse controls stay independently available, and normal gravity still executes. The existing enabled-walking lift regression already reproduced this failure, so no assertions or tolerances were weakened and no redundant test was added. Fresh runtime and PlayMode C# compilation passes with installed Unity assemblies; actual Unity rerun for this correction is **NOT RUN** by this worker. No Unity process was opened or modified.
