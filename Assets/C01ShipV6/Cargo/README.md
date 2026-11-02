# Cargo lift integration

`CargoLiftController` composes the existing `C01.Ship.V5.ShipLiftV5` so V5 landing gates enforce their own interlock even if another script calls `SetOpen` or `SetImmediate`. Add the controller to an active object and configure it once during scene construction or runtime setup; references and configuration are serialized with the scene:

```csharp
var controller = liftObject.AddComponent<C01.Ship.V6.Cargo.CargoLiftController>();
controller.Configure(platformRoot, platformColliders, characterController,
    new[] { lowerGate, middleGate, upperGate }, initialFloor: 1, speed: 4f);
controller.RequestFloor(2);
```

`platformColliders` is a `Collider[]` of the solid top surfaces, each on `platformRoot` or a descendant; a single `Collider` overload is also available. Place the four separate floor modules under that common moving root. The root pivot's world Y must correspond to the top landing elevation; the floors are 0 = -12.4, 1 = 0, 2 = 6.4. `Configure` places the platform at the initial floor and closes the gates; call it before gameplay and before placing riders. Gates must be distinct, unbound to another lift, and not airlock controlled. Do not put gates under the moving root. A real `CharacterController` is required.

`RequestFloor` returns false for invalid floors or an unavailable controller. `CurrentFloor`, `IsMoving`, and `Lift` are available for UI and existing V5 integration. For an existing `ShipButtonV5`, set `button.lift = controller.Lift` and `button.floor` to 0, 1, or 2. The owned V5 lift's public fields should not be changed after configuration. Disabling the cargo controller pauses the owned lift; re-enabling resumes it. Keep both components enabled in normal operation.

Cargo is detected every physics step by a downward support ray from a collider's bounds to one of the specified platform surfaces, then its rigidbody receives the platform's vertical displacement without reparenting. Cargo must have an enabled non-trigger collider and rigidbody and be directly supported by a surface; stacked cargo, unusual off-center collider shapes, airborne bodies, trigger-only bodies, and collision layers excluded from `Physics.DefaultRaycastLayers` are not guaranteed to be carried. Platform surfaces should be solid and horizontal. This controller does not prevent a rider from being crushed by unrelated scene geometry.

To run the tests after the working project is free: open Unity 6000.3.14f1, choose Window > General > Test Runner > PlayMode, and run `CargoLiftPlayTests`. The tests create their own four-module platform and do not require a scene. They must be run in Unity; source compilation alone does not verify physics behavior.

