using System.Collections;
using C01.Ship.V5;
using C01.Ship.V6.Cargo;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

public class CargoLiftPlayTests
{
    GameObject root, playerObject, cargoObject, offCarObject;
    CargoLiftController lift;
    ShipGateV5[] gates;
    CharacterController player;
    Rigidbody cargo, offCar;

    [UnitySetUp]
    public IEnumerator SetUp()
    {
        root = new GameObject("test lift");
        var platformRoot = new GameObject("platform root");
        platformRoot.transform.SetParent(root.transform);
        var surfaces = new Collider[4];
        for (int i = 0; i < 4; i++)
        {
            var platform = GameObject.CreatePrimitive(PrimitiveType.Cube);
            platform.name = "platform module " + i;
            platform.transform.SetParent(platformRoot.transform);
            platform.transform.localPosition = new Vector3(i % 2 == 0 ? -1 : 1, -.1f, i < 2 ? -1 : 1);
            platform.transform.localScale = new Vector3(2, .2f, 2);
            surfaces[i] = platform.GetComponent<Collider>();
        }
        gates = new ShipGateV5[3];
        for (int i = 0; i < 3; i++)
        {
            var gate = new GameObject("gate " + i);
            gate.transform.SetParent(root.transform);
            gates[i] = gate.AddComponent<ShipGateV5>();
            gates[i].speed = 10;
        }
        playerObject = new GameObject("player");
        player = playerObject.AddComponent<CharacterController>();
        player.height = 2; player.center = Vector3.up;
        player.transform.position = new Vector3(-.8f, .04f, 0);
        cargoObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cargoObject.transform.position = new Vector3(.8f, .51f, .8f);
        cargo = cargoObject.AddComponent<Rigidbody>();
        offCarObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
        offCarObject.transform.position = new Vector3(5, .5f, 0);
        offCar = offCarObject.AddComponent<Rigidbody>();
        offCar.useGravity = false;
        lift = root.AddComponent<CargoLiftController>();
        lift.Configure(platformRoot.transform, surfaces, player, gates, 1, 8);
        Physics.SyncTransforms();
        player.Move(Vector3.down * .05f);
        yield return new WaitForFixedUpdate();
    }

    [UnityTearDown]
    public IEnumerator TearDown()
    {
        Object.Destroy(root); Object.Destroy(playerObject);
        Object.Destroy(cargoObject); Object.Destroy(offCarObject);
        yield return null;
    }

    [UnityTest]
    public IEnumerator CarriesCharacterAndDynamicCargoAcrossAllLandingsWithoutMovingNearbyBody()
    {
        foreach (var destination in new[] { 2, 0, 1 })
        {
            Assert.That(lift.RequestFloor(destination), Is.True);
            float deadline = Time.time + 10;
            do
            {
                yield return new WaitForFixedUpdate();
                Assert.That(Time.time, Is.LessThan(deadline), "Lift did not arrive");
                float y = lift.Lift.car.position.y;
                Assert.That(player.transform.position.y - y, Is.InRange(-.1f, .18f));
                Assert.That(cargo.position.y - y, Is.InRange(.38f, .7f));
                Assert.That(offCar.position.y, Is.EqualTo(.5f).Within(.03f));
                if (Mathf.Abs(y - new[] { -12.4f, 0f, 6.4f }[destination]) > .02f)
                    Assert.That(gates[destination].openness, Is.LessThan(.002f));
            } while (lift.IsMoving);
            Assert.That(lift.Lift.car.position.y, Is.EqualTo(new[] { -12.4f, 0f, 6.4f }[destination]).Within(.01f));
        }
    }

    [UnityTest]
    public IEnumerator CarriesCargoFromEachOfFourIndependentModules()
    {
        var modules = new Rigidbody[4];
        try
        {
            for (int i = 0; i < modules.Length; i++)
            {
                var box = GameObject.CreatePrimitive(PrimitiveType.Cube);
                box.transform.localScale = Vector3.one * .3f;
                box.transform.position = new Vector3(i % 2 == 0 ? -1.6f : 1.6f, .16f, i < 2 ? -1.6f : 1.6f);
                modules[i] = box.AddComponent<Rigidbody>();
            }
            Physics.SyncTransforms();
            yield return new WaitForFixedUpdate();
            Assert.That(lift.RequestFloor(2), Is.True);
            float deadline = Time.time + 10;
            while (lift.IsMoving)
            {
                yield return new WaitForFixedUpdate();
                Assert.That(Time.time, Is.LessThan(deadline));
                foreach (var body in modules)
                    Assert.That(body.position.y - lift.Lift.car.position.y, Is.InRange(.07f, .3f));
            }
            foreach (var body in modules)
                Assert.That(body.position.y, Is.EqualTo(6.55f).Within(.12f));
        }
        finally
        {
            foreach (var body in modules) if (body != null) Object.Destroy(body.gameObject);
        }
    }
    [UnityTest]
    public IEnumerator ClosesBeforeMovingAndRejectsDirectOpeningOfAwayLanding()
    {
        gates[1].SetImmediate(1);
        lift.RequestFloor(2);
        float initialY = lift.Lift.car.position.y;
        yield return new WaitForFixedUpdate();
        Assert.That(lift.Lift.car.position.y, Is.EqualTo(initialY).Within(.001f));
        gates[0].SetOpen(true);
        gates[0].SetImmediate(1);
        Assert.That(gates[0].target, Is.Zero);
        Assert.That(gates[0].openness, Is.Zero);
        float deadline = Time.time + 10;
        while (lift.IsMoving)
        {
            yield return new WaitForFixedUpdate();
            Assert.That(Time.time, Is.LessThan(deadline));
            if (lift.Lift.car.position.y > initialY + .01f)
                Assert.That(gates[1].openness, Is.LessThan(.002f));
        }
        gates[0].SetOpen(true);
        Assert.That(gates[0].target, Is.Zero);
        yield return new WaitForFixedUpdate();
        Assert.That(gates[2].target, Is.EqualTo(1));
    }

    [Test]
    public void RejectsInvalidFloorAndInvalidGateSetup()
    {
        Assert.That(lift.RequestFloor(-1), Is.False);
        Assert.That(lift.RequestFloor(3), Is.False);
        var other = new GameObject("bad lift");
        try
        {
            var bad = other.AddComponent<CargoLiftController>();
            Assert.Throws<System.ArgumentException>(() => bad.Configure(lift.Lift.car,
                lift.Lift.car.GetComponentInChildren<Collider>(), player, new[] { gates[0], gates[0], gates[2] }, 1, 4));
        }
        finally { Object.DestroyImmediate(other); }
    }
}





