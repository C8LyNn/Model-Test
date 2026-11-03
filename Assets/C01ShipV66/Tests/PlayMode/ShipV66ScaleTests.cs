using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV66ScaleTests
{
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v66", LoadSceneMode.Single);
        yield return null;
        explorer = Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer, Is.Not.Null);
        explorer.SetWalking(true);
        explorer.enabled = false;
    }

    [UnityTest] public IEnumerator PlayerAndCameraUseHumanScale()
    {
        var p = explorer.player;
        Assert.That(p.height, Is.EqualTo(1.8f).Within(.001f));
        Assert.That(p.radius, Is.EqualTo(.28f).Within(.001f));
        Assert.That(p.center.y, Is.EqualTo(.9f).Within(.001f));
        Assert.That(explorer.view.transform.parent, Is.EqualTo(p.transform));
        Assert.That(explorer.view.transform.localPosition.y, Is.EqualTo(1.65f).Within(.001f));
        Assert.That(explorer.walkSpeed, Is.EqualTo(2.5f).Within(.001f));
        Assert.That(explorer.walkSpeed * explorer.sprintMultiplier, Is.EqualTo(5f).Within(.001f));
        Assert.That(explorer.view.orthographic, Is.False);
        Assert.That(explorer.view.fieldOfView, Is.EqualTo(75f).Within(.001f));
        Assert.That(explorer.view.nearClipPlane, Is.EqualTo(.05f).Within(.001f));
        Physics.SyncTransforms();
        var overlapping = Physics.OverlapCapsule(p.transform.position + Vector3.up * (p.radius + .03f), p.transform.position + Vector3.up * (p.height - p.radius - .03f), p.radius - .03f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore).Where(c => c.gameObject != p.gameObject).ToArray();
        Assert.That(overlapping, Is.Empty, "player starts inside geometry: " + string.Join(", ", overlapping.Select(c => c.name)));
        yield return null;
    }

    [UnityTest] public IEnumerator OverviewWheelChangesScaleAndWalkingRestoresCamera()
    {
        var position = explorer.player.transform.position;
        explorer.SetWalking(false);
        Assert.That(explorer.view.orthographic, Is.True);
        var cameraPosition = explorer.view.transform.position;
        float before = explorer.view.orthographicSize;
        float panBefore = explorer.OverviewPanSpeed();
        explorer.ApplyOverviewScroll(120);
        Assert.That(explorer.view.orthographicSize, Is.LessThan(before));
        Assert.That(explorer.OverviewPanSpeed(), Is.LessThanOrEqualTo(panBefore));
        Assert.That(Vector3.Distance(cameraPosition, explorer.view.transform.position), Is.LessThan(.001f));
        explorer.ApplyOverviewScroll(-120);
        Assert.That(explorer.view.orthographicSize, Is.EqualTo(before).Within(.01f));
        explorer.ApplyOverviewScroll(100000);
        Assert.That(explorer.view.orthographicSize, Is.EqualTo(4.5f).Within(.001f));
        explorer.SetWalking(true);
        Assert.That(explorer.view.fieldOfView, Is.EqualTo(75f).Within(.001f));
        Assert.That(Vector3.Distance(position, explorer.player.transform.position), Is.LessThan(.001f));
        yield return null;
    }

    [UnityTest] public IEnumerator PlayerCanUseButtonsAndRidePassengerAndCargoLifts()
    {
        var representatives = new[] { explorer.lifts.First(l => !l.id.StartsWith("STERN_CARGO")), explorer.lifts.First(l => l.id.StartsWith("STERN_CARGO")) };
        var cc = explorer.player;
        foreach (var lift in representatives)
        {
            lift.ResetToFloor(1); lift.RequestFloor(1); var gate = lift.landings[1];
            float deadline = Time.time + 6;
            while (!gate.IsOpen && Time.time < deadline) yield return new WaitForFixedUpdate();
            Assert.That(gate.IsOpen, Is.True, lift.id);
            cc.enabled = false; cc.transform.position = gate.transform.position + new Vector3(-1, .05f, 1.5f); cc.enabled = true; Physics.SyncTransforms();
            for (float t = 0; t < 2.5f; t += Time.fixedDeltaTime) { cc.Move(Vector3.right * (2.2f / 2.5f) * Time.fixedDeltaTime + Vector3.down * .025f); yield return new WaitForFixedUpdate(); }
            Assert.That(cc.transform.position.x, Is.GreaterThan(gate.transform.position.x + .65f), lift.id + " entry");
            var button = lift.car.GetComponentsInChildren<ShipButtonV5>(true).First(b => b.floor == 2);
            var target = button.GetComponentsInChildren<Collider>().OrderByDescending(c => Vector3.Dot(c.bounds.center - button.transform.position, button.transform.forward)).First();
            var point = target.bounds.center; var forward = button.transform.forward; Physics.SyncTransforms();
            float start = cc.transform.position.y; float cameraStart = explorer.view.transform.position.y;
            Assert.That(explorer.TryPressRay(new Ray(point + forward * .5f, -forward), 1), Is.True, lift.id + " control");
            deadline = Time.time + 25;
            while (lift.IsMoving && Time.time < deadline) yield return new WaitForFixedUpdate();
            Assert.That(lift.currentFloor, Is.EqualTo(2), lift.id);
            Assert.That(cc.transform.position.y - start, Is.EqualTo(3.4f).Within(.25f), lift.id + " rider");
            Assert.That(explorer.view.transform.position.y - cameraStart, Is.EqualTo(3.4f).Within(.25f), lift.id + " camera");
        }
    }

    [UnityTest] public IEnumerator PlayerCanClimbSectorStairs()
    {
        var cc = explorer.player; cc.enabled = false; cc.transform.position = new Vector3(2.5f, .04f, 59.6f); cc.enabled = true; Physics.SyncTransforms();
        for (float t = 0; t < 5; t += Time.fixedDeltaTime) { cc.Move(Vector3.right * (7.6f / 5) * Time.fixedDeltaTime + Vector3.down * .04f); yield return new WaitForFixedUpdate(); }
        Assert.That(cc.transform.position.y, Is.GreaterThan(2.8f), "stairs do not reach landing: " + cc.transform.position);
    }
}
