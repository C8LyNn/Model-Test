using System;
using System.Collections;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace C01.Ship.V4.Tests
{
    // These are integration tests of the delivered scene, not surrogate boxes or mocked controls.
    public class ShipRuntimePlayTests
    {
        ShipExplorerV4 explorer;
        ShipDataV4 data;

        [UnitySetUp]
        public IEnumerator LoadShip()
        {
            yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck", LoadSceneMode.Single);
            yield return null;
            explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV4>();
            Assert.That(explorer, Is.Not.Null, "The built scene must contain the explorer.");
            data = JsonUtility.FromJson<ShipDataV4>(File.ReadAllText(
                Path.Combine(Application.dataPath, "C01ShipV4/Data/ship_v4.json")));
            explorer.SetWalking(false);
            explorer.enabled = false; // Tests drive the real controller explicitly.
            Time.timeScale = 1;
        }

        [UnityTearDown]
        public IEnumerator Restore()
        {
            Time.timeScale = 1;
            if (explorer != null) explorer.enabled = true;
            yield return null;
        }

        [UnityTest]
        public IEnumerator ImmediateGatePositionIsReversibleAndOnlyLeavesMove()
        {
            var gate = explorer.gates.First(g => g.interlockLift == null && g.interlockAirlock == null);
            gate.SetImmediate(0);
            var closed = gate.leaves.Select(t => t.position).ToArray();
            var other = explorer.master.GetComponentsInChildren<ShipInstanceV4>(true)
                .Where(m => !gate.leaves.Contains(m.transform)).Select(m => m.transform).ToArray();
            var stationary = other.Select(t => t.position).ToArray();
            var record = data.gates.Single(g => g.id == gate.id);
            gate.SetImmediate(.6f);
            Assert.That(gate.target, Is.EqualTo(.6f).Within(.0001f));
            for (int i = 0; i < gate.leaves.Length; i++)
            {
                var placement = data.placements.Single(p => p.id == record.leaves[i]);
                var offset = new Vector3(placement.travel[0], placement.travel[1], placement.travel[2]) * .6f;
                Assert.That(Vector3.Distance(gate.leaves[i].position, closed[i] + offset), Is.LessThan(.001f));
            }
            gate.SetImmediate(0);
            gate.SetImmediate(0);
            yield return new WaitForFixedUpdate();
            Assert.That(gate.target, Is.EqualTo(0));
            for (int i = 0; i < gate.leaves.Length; i++)
                Assert.That(Vector3.Distance(gate.leaves[i].position, closed[i]), Is.LessThan(.001f), "Leaf cache drifted.");
            for (int i = 0; i < other.Length; i++)
                Assert.That(Vector3.Distance(other[i].position, stationary[i]), Is.LessThan(.001f), "A non-leaf frame/node moved.");
        }

        [UnityTest]
        public IEnumerator PhysicalButtonOpensGate_ClosedGateBlocks_OpenGatePasses()
        {
            var record = data.gates.First(g => string.IsNullOrEmpty(g.lift) &&
                string.IsNullOrEmpty(g.airlock) && g.zones.Any(z => z.StartsWith("L1_C") && !z.EndsWith("BATH")));
            var gate = explorer.gates.Single(g => g.id == record.id);
            var button = explorer.buttons.First(b => b.gate == gate);
            var cc = explorer.player;
            var normal = Quaternion.Euler(0, record.yaw, 0) * Vector3.forward;
            var center = new Vector3(record.x, record.y, record.z) + Quaternion.Euler(0, record.yaw, 0) * Vector3.right * (record.width * .5f);
            var start = center - normal * 1.1f + Vector3.up * .05f;
            gate.SetImmediate(0);
            Place(cc, start);
            yield return Move(cc, normal * 2.2f, 1);
            Assert.That(Vector3.Dot(cc.transform.position - center, normal), Is.LessThan(.15f),
                "A closed gate must physically stop a 1.8 m CharacterController.");

            // Direct panel hits must never be interpreted as a button press.
            var panel = gate.leaves[0].GetComponentInChildren<Collider>();
            Assert.That(panel, Is.Not.Null);
            Assert.That(explorer.TryPressRay(new Ray(panel.bounds.center - normal * 1.5f, normal), 3), Is.False);
            Assert.That(gate.target, Is.EqualTo(0));
            var collider = button.GetComponentInChildren<Collider>();
            Assert.That(collider, Is.Not.Null, "A visible button needs a real collider.");
            var outward = Vector3.Dot(collider.bounds.center - center, normal) >= 0 ? normal : -normal;
            Assert.That(explorer.TryPressRay(new Ray(collider.bounds.center + outward * .65f, -outward), 1), Is.True);
            yield return WaitUntil(() => gate.IsOpen, 5, "Button did not animate the gate open.");
            Place(cc, start);
            yield return Move(cc, normal * 2.2f, 1);
            Assert.That(Vector3.Dot(cc.transform.position - center, normal), Is.GreaterThan(.65f),
                "The opened gate must leave a physically traversable opening.");
        }

        [UnityTest]
        public IEnumerator AirlockRepeatedAndCancelledRequestsNeverOpenBothGates()
        {
            var locks = UnityEngine.Object.FindObjectsByType<ShipAirlockV4>(FindObjectsSortMode.None);
            Assert.That(locks.Length, Is.GreaterThan(0));
            foreach (var airlock in locks)
            {
                airlock.gateA.SetImmediate(0);
                airlock.gateB.SetImmediate(0);
                var a = explorer.buttons.First(b => b.gate == airlock.gateA);
                var b = explorer.buttons.First(b => b.gate == airlock.gateB);
                a.Press();
                yield return WaitUntil(() => airlock.gateA.IsOpen, 5, "Airlock A did not open.");
                b.Press();
                b.Press(); // Cancel the pending request while A closes.
                for (float t = 0; t < 1; t += Time.fixedDeltaTime)
                {
                    AssertInterlocked(airlock);
                    yield return new WaitForFixedUpdate();
                }
                Assert.That(airlock.gateB.target, Is.EqualTo(0));
                b.Press();
                yield return WaitUntil(() => airlock.gateB.IsOpen, 5, "Airlock B did not open after cancellation.",
                    () => AssertInterlocked(airlock));
                a.Press();
                yield return WaitUntil(() => airlock.gateA.IsOpen, 5, "Airlock A did not reopen.",
                    () => AssertInterlocked(airlock));
            }
        }

        [UnityTest]
        public IEnumerator BothLiftsCarryRealPlayerContinuouslyToAllFloorsAndLockAwayLandings()
        {
            Assert.That(explorer.lifts.Length, Is.EqualTo(2));
            foreach (var lift in explorer.lifts)
            {
                lift.player = explorer.player;
                lift.ResetToFloor(1);
                Place(explorer.player, new Vector3(lift.car.position.x, .04f, lift.car.position.z));
                explorer.player.Move(Vector3.down * .1f);
                yield return new WaitForFixedUpdate();
                foreach (int floor in new[] { 2, 0, 1 })
                {
                    var button = explorer.buttons.First(b => b.lift == lift && b.floor == floor);
                    button.Press();
                    var previousCar = lift.car.position;
                    var previousPlayer = explorer.player.transform.position;
                    float elapsed = 0;
                    do
                    {
                        yield return new WaitForFixedUpdate();
                        elapsed += Time.fixedDeltaTime;
                        var delta = lift.car.position - previousCar;
                        var riderDelta = explorer.player.transform.position - previousPlayer;
                        Assert.That(delta.magnitude, Is.LessThanOrEqualTo(lift.speed * Time.fixedDeltaTime + .015f),
                            "Lift jumped instead of travelling continuously.");
                        Assert.That(Mathf.Abs(riderDelta.y - delta.y), Is.LessThan(.08f),
                            "The player did not ride the physical car delta.");
                        for (int i = 0; i < lift.landings.Length; i++)
                        {
                            // During the departure closing phase the aligned gate can still
                            // be retracting; actual car motion and every away gate require shut.
                            if ((lift.IsMoving && delta.sqrMagnitude > .000001f) ||
                                Mathf.Abs(lift.car.position.y - lift.elevations[i]) > .01f)
                                Assert.That(lift.landings[i].openness, Is.LessThan(.001f), "An away/moving landing opened.");
                        }
                        previousCar = lift.car.position;
                        previousPlayer = explorer.player.transform.position;
                        Assert.That(elapsed, Is.LessThan(15), "Lift failed to reach requested floor.");
                    } while (lift.IsMoving);
                    var expected = floor == 0 ? -12.4f : floor == 1 ? 0 : 6.4f;
                    Assert.That(lift.car.position.y, Is.EqualTo(expected).Within(.015f));
                    Assert.That(explorer.player.transform.position.y, Is.EqualTo(expected).Within(.12f));
                    yield return WaitUntil(() => lift.landings[floor].IsOpen, 5, "Aligned landing never opened.");
                    // Opening an away landing directly must still be rejected by the runtime interlock.
                    lift.landings[(floor + 1) % 3].SetOpen(true);
                    Assert.That(lift.landings[(floor + 1) % 3].target, Is.EqualTo(0));
                }
            }
        }

        [UnityTest]
        public IEnumerator WalkingExplorerGravityKeepsPlayerAboardBothLiftsAcrossAllFloors()
        {
            Assert.That(explorer.lifts.Length, Is.EqualTo(2));
            explorer.SetWalking(true);
            explorer.enabled = true;
            Assert.That(explorer.view.orthographic, Is.False, "Walking must use a perspective camera.");
            Assert.That(explorer.view.fieldOfView, Is.EqualTo(65).Within(.01f));
            var cc = explorer.player;
            foreach (var lift in explorer.lifts)
            {
                var record = data.lifts.Single(l => l.id == lift.id);
                lift.player = cc;
                lift.ResetToFloor(1);
                // Only test setup places the capsule. All subsequent vertical motion comes
                // from the enabled explorer's gravity and the real lift's carry movement.
                Place(cc, new Vector3(record.x, .65f, record.z));
                float settleDeadline = Time.time + 3;
                while ((!cc.isGrounded || cc.transform.position.y > .15f) && Time.time < settleDeadline)
                {
                    yield return null;
                    AssertAwayLandingsShut(lift);
                }
                Assert.That(cc.isGrounded, Is.True, "Walking gravity never settled the player onto " + lift.id);
                Assert.That(cc.transform.position.y, Is.LessThan(.15f),
                    "The enabled explorer must actually apply gravity before the ride.");

                foreach (int floor in new[] { 2, 0, 1 })
                {
                    explorer.buttons.First(b => b.lift == lift && b.floor == floor).Press();
                    float deadline = Time.time + 15;
                    var previousCar = lift.car.position;
                    do
                    {
                        // Render-frame sampling includes normal ShipExplorerV4.Update gravity,
                        // complementing the controlled test's fixed-step transport assertions.
                        yield return null;
                        Assert.That(explorer.enabled && explorer.walking, Is.True);
                        AssertAwayLandingsShut(lift);
                        Assert.That(Mathf.Abs(cc.transform.position.y - lift.car.position.y), Is.LessThan(.15f),
                            "Walking gravity separated the rider from " + lift.id + ".");
                        Assert.That(Mathf.Abs(cc.transform.position.x - record.x), Is.LessThan(.12f));
                        Assert.That(Mathf.Abs(cc.transform.position.z - record.z), Is.LessThan(.12f));
                        Assert.That(Vector3.Distance(lift.car.position, previousCar),
                            Is.LessThanOrEqualTo(lift.speed * (Time.deltaTime + Time.fixedDeltaTime) + .015f),
                            "The car jumped while the walking explorer was active.");
                        previousCar = lift.car.position;
                        Assert.That(Time.time, Is.LessThan(deadline), "Walking-mode ride did not finish.");
                    } while (lift.IsMoving || !lift.landings[floor].IsOpen);

                    float expected = floor == 0 ? -12.4f : floor == 1 ? 0 : 6.4f;
                    Assert.That(lift.currentFloor, Is.EqualTo(floor));
                    Assert.That(lift.car.position.y, Is.EqualTo(expected).Within(.015f));
                    Assert.That(cc.transform.position.y, Is.EqualTo(expected).Within(.12f));
                    Assert.That(lift.landings[floor].IsOpen, Is.True);
                    // Keep normal gravity running after arrival; a transient successful carry
                    // must not hide falling through the platform on the next few frames.
                    float holdUntil = Time.time + .3f;
                    while (Time.time < holdUntil)
                    {
                        yield return null;
                        AssertAwayLandingsShut(lift);
                        Assert.That(cc.transform.position.y, Is.EqualTo(expected).Within(.12f));
                    }
                }
            }
        }

        [UnityTest]
        public IEnumerator LiftCancellationAndResetDoNotCarryUnrelatedNearbyPlayer()
        {
            foreach (var lift in explorer.lifts)
            {
                lift.ResetToFloor(1);
                var record = data.lifts.Single(l => l.id == lift.id);
                var p = record.waypoints[1].position;
                Place(explorer.player, new Vector3(p[0], p[1] + .05f, p[2]));
                var unrelated = explorer.player.transform.position;
                lift.RequestFloor(2);
                yield return new WaitForFixedUpdate();
                lift.RequestFloor(0);
                lift.RequestFloor(0);
                yield return new WaitForFixedUpdate();
                lift.RequestFloor(1);
                yield return WaitUntil(() => !lift.IsMoving, 15, "Cancelled lift did not settle.");
                lift.RequestFloor(2);
                yield return WaitUntil(() => !lift.IsMoving, 15, "Lift did not travel after cancellation.");
                Assert.That(Vector3.Distance(explorer.player.transform.position, unrelated), Is.LessThan(.02f));
                lift.ResetToFloor(0);
                Assert.That(Vector3.Distance(explorer.player.transform.position, unrelated), Is.LessThan(.02f),
                    "QA reset moved a nearby player who was outside the car.");
            }
        }

        [UnityTest]
        public IEnumerator OverviewResetRetainsFramingAndColliders_WalkingRestoresGeometry()
        {
            explorer.SetWalking(false);
            explorer.SetDeck(0);
            explorer.ResetView();
            var p = explorer.view.transform.position;
            var q = explorer.view.transform.rotation;
            bool overviewOrthographic = explorer.view.orthographic;
            float overviewSize = explorer.view.orthographicSize;
            float overviewFov = explorer.view.fieldOfView;
            var solid = explorer.master.GetComponentsInChildren<Collider>(true);
            var enabledBefore = solid.Select(c => c.enabled).ToArray();
            explorer.view.transform.position += new Vector3(5, 2, 8);
            explorer.view.orthographic = !overviewOrthographic;
            explorer.view.orthographicSize = overviewSize * .5f;
            explorer.view.fieldOfView = 90;
            explorer.ResetView();
            Assert.That(Vector3.Distance(explorer.view.transform.position, p), Is.LessThan(.001f));
            Assert.That(Quaternion.Angle(explorer.view.transform.rotation, q), Is.LessThan(.001f));
            Assert.That(explorer.view.orthographic, Is.EqualTo(overviewOrthographic));
            Assert.That(explorer.view.orthographicSize, Is.EqualTo(overviewSize).Within(.001f));
            Assert.That(explorer.view.fieldOfView, Is.EqualTo(overviewFov).Within(.001f));
            Assert.That(explorer.selectedDeck, Is.EqualTo(0));
            Assert.That(solid.Select(c => c.enabled).ToArray(), Is.EqualTo(enabledBefore));
            var upper = explorer.master.GetComponentsInChildren<ShipInstanceV4>(true)
                .Where(m => m.deck == 2).SelectMany(m => m.GetComponentsInChildren<Renderer>(true)).ToArray();
            Assert.That(upper.Length, Is.GreaterThan(0));
            Assert.That(upper.All(r => !r.enabled), Is.True, "Upper deck leaks into a lower cutaway.");
            explorer.SetWalking(true);
            Assert.That(explorer.view.orthographic, Is.False, "The overview projection leaked into walking.");
            Assert.That(explorer.view.fieldOfView, Is.EqualTo(65).Within(.01f));
            var walkingRenderers = explorer.master.GetComponentsInChildren<Renderer>(true);
            Assert.That(walkingRenderers.Where(r => r.GetComponentInParent<ShipZoneV4>() == null).All(r => r.enabled), Is.True);
            Assert.That(walkingRenderers.Where(r => r.GetComponentInParent<ShipZoneV4>() != null).All(r => !r.enabled), Is.True,
                "Editor floor labels must stay hidden while runtime labels follow the L toggle.");
            explorer.SetWalking(true); // Repeated walking must not overwrite the saved overview.
            explorer.SetWalking(false);
            Assert.That(explorer.view.orthographic, Is.EqualTo(overviewOrthographic));
            Assert.That(explorer.view.orthographicSize, Is.EqualTo(overviewSize).Within(.001f));
            Assert.That(explorer.view.fieldOfView, Is.EqualTo(overviewFov).Within(.001f));
            Assert.That(Vector3.Distance(explorer.view.transform.position, p), Is.LessThan(.001f));
            Assert.That(Quaternion.Angle(explorer.view.transform.rotation, q), Is.LessThan(.001f));
            yield return null;
        }

        static void AssertInterlocked(ShipAirlockV4 airlock)
        {
            Assert.That(airlock.gateA.openness < .001f || airlock.gateB.openness < .001f, Is.True,
                "Both airlock gates have a nonzero opening.");
        }

        static void AssertAwayLandingsShut(ShipLiftV4 lift)
        {
            for (int floor = 0; floor < lift.landings.Length; floor++)
            {
                var gate = lift.landings[floor];
                bool aligned = Mathf.Abs(lift.car.position.y - lift.elevations[floor]) <= .01f;
                if (aligned) continue; // The aligned departure gate may still be closing.
                Assert.That(gate.openness, Is.LessThan(.001f), "Away landing opened on " + lift.id);
                Assert.That(gate.target, Is.EqualTo(0), "Away landing was commanded open on " + lift.id);
            }
        }

        static void Place(CharacterController controller, Vector3 position)
        {
            controller.enabled = false;
            controller.transform.position = position;
            controller.enabled = true;
            Physics.SyncTransforms();
        }

        static IEnumerator Move(CharacterController controller, Vector3 displacement, float duration)
        {
            for (float t = 0; t < duration; t += Time.fixedDeltaTime)
            {
                controller.Move(displacement / duration * Time.fixedDeltaTime + Vector3.down * .04f);
                yield return new WaitForFixedUpdate();
            }
        }

        static IEnumerator WaitUntil(Func<bool> condition, float timeout, string message, Action invariant = null)
        {
            float elapsed = 0;
            while (!condition() && elapsed < timeout)
            {
                invariant?.Invoke();
                elapsed += Time.fixedDeltaTime;
                yield return new WaitForFixedUpdate();
            }
            invariant?.Invoke();
            Assert.That(condition(), Is.True, message);
        }
    }
}
