using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace C01.Ship.V5.Tests
{
    public class ShipInputPlayTests
    {
        Mouse mouse;
        ShipExplorerV5 explorer;

        [UnitySetUp]
        public IEnumerator Setup()
        {
            yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v5", LoadSceneMode.Single);
            yield return null;
            explorer = Object.FindFirstObjectByType<ShipExplorerV5>();
            explorer.SetWalking(true);
            mouse = InputSystem.AddDevice<Mouse>();
            yield return null;
        }

        [UnityTearDown]
        public IEnumerator Teardown()
        {
            if (mouse != null) InputSystem.RemoveDevice(mouse);
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            yield return null;
        }

        [UnityTest]
        public IEnumerator MouseLooksWithoutRightButton()
        {
            float before = explorer.player.transform.eulerAngles.y;
            InputSystem.QueueDeltaStateEvent(mouse.delta, new Vector2(80, 0));
            InputSystem.Update();
            explorer.SendMessage("Update");
            yield return null;
            yield return null;
            Assert.That(Mathf.Abs(Mathf.DeltaAngle(before, explorer.player.transform.eulerAngles.y)),
                Is.GreaterThan(1f), "Mouse motion must turn the player without holding a button.");
        }

        [UnityTest]
        public IEnumerator ClickAtReticleWorksEvenWhenPointerWasOverToolbar()
        {
            var button = explorer.buttons.First(b => b.gate != null && b.airlock == null && b.lift == null);
            var gate = button.gate;
            gate.SetImmediate(0);
            var target = button.GetComponentsInChildren<Collider>().First().bounds.center;
            var facing = button.transform.forward;
            var cc = explorer.player;
            cc.enabled = false;
            // Face the panel from its visible side, with the view at the collider's height.
            cc.transform.position = new Vector3(target.x + facing.x, button.transform.position.y - 1.05f, target.z + facing.z);
            cc.transform.rotation = Quaternion.LookRotation(-facing, Vector3.up);
            cc.enabled = true;
            explorer.view.transform.rotation = Quaternion.LookRotation(target - explorer.view.transform.position, Vector3.up);
            Physics.SyncTransforms();
            Assert.That(explorer.TryPressScreen(new Vector2(5, Screen.height - 5)), Is.True);
            Assert.That(gate.target, Is.GreaterThan(.5f), "A centered button click must not be blocked by overview GUI coordinates.");
            yield return null;
        }

        [UnityTest]
        public IEnumerator EveryGatePanelHasAReachableApproach()
        {
            var failures = new System.Collections.Generic.List<string>();
            foreach (var button in explorer.buttons.Where(b => b.gate != null))
            {
                var screen = button.GetComponentsInChildren<Collider>().OrderByDescending(c =>
                    Vector3.Dot(c.bounds.center - button.transform.position, button.transform.forward)).First();
                var target = screen.bounds.center;
                var origin = target + button.transform.forward * .65f;
                if (!Physics.Raycast(origin, -button.transform.forward, out var hit, 1f) ||
                    hit.collider.GetComponentInParent<ShipButtonV5>() != button)
                    failures.Add(button.name + (hit.collider == null ? ": no hit" : ": blocked by " + hit.collider.name));
            }
            Assert.That(failures, Is.Empty, string.Join("\n", failures));
            yield return null;
        }
    }
}
