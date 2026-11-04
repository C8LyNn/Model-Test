using System.Collections;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class ShipGateIdleTests
{
    [UnityTest]
    public IEnumerator GateRespondsAfterIdleAndTracksMovedRotatedParent()
    {
        var root = new GameObject("gate root");
        root.transform.rotation = Quaternion.Euler(0, 90, 0);
        var leaf = GameObject.CreatePrimitive(PrimitiveType.Cube);
        leaf.transform.SetParent(root.transform, false);
        var gate = root.AddComponent<ShipGateV5>();
        gate.leaves = new[] { leaf.transform };
        gate.travel = new[] { Vector3.right * 2f };
        gate.speed = 50f;
        yield return null;
        gate.SetImmediate(0);
        for (int i=0; i<5; i++) yield return new WaitForFixedUpdate();
        root.transform.position = new Vector3(5, 2, 3);
        Physics.SyncTransforms();
        var closed = leaf.transform.position;
        gate.target = 1;
        for (int i=0; i<5; i++) yield return new WaitForFixedUpdate();
        Assert.That(gate.IsOpen, Is.True, "A direct target change must wake an idle gate.");
        Assert.That(Vector3.Distance(leaf.transform.position, closed + Vector3.right * 2f), Is.LessThan(.01f));
        gate.SetImmediate(0);
        Assert.That(Vector3.Distance(leaf.transform.position, closed), Is.LessThan(.01f));
        Object.Destroy(root);
    }
}
