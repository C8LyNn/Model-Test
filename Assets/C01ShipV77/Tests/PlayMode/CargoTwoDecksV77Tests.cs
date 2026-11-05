using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V6.Cargo;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class CargoTwoDecksV77Tests
{
    [UnityTest] public IEnumerator CargoLiftCarriesDynamicCrateWithDeletedFloorZero()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v77",LoadSceneMode.Single);yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);
        var lift=explorer.lifts.First(l=>l.id=="STERN_CARGO_S");
        var controller=explorer.master.GetComponentsInChildren<CargoLiftController>(true).Single(c=>c.Lift==lift);
        Assert.That(controller.allowMissingDeckZero,Is.True);Assert.That(controller.RequestFloor(0),Is.False);
        lift.ResetToFloor(1);var box=GameObject.CreatePrimitive(PrimitiveType.Cube);box.name="QA_DynamicCargo";
        box.transform.localScale=Vector3.one*.4f;box.transform.position=new Vector3((lift.footprint.x+lift.footprint.y)*.5f,.21f,(lift.footprint.z+lift.footprint.w)*.5f);
        var body=box.AddComponent<Rigidbody>();Physics.SyncTransforms();yield return new WaitForFixedUpdate();
        var start=body.position.y;Assert.That(controller.RequestFloor(2),Is.True);float deadline=Time.time+25;
        while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();
        Assert.That(lift.currentFloor,Is.EqualTo(2));Assert.That(body.position.y-start,Is.EqualTo(3.4f).Within(.2f));
        Object.Destroy(box);
    }
}
