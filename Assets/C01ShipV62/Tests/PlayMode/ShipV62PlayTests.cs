using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV62PlayTests
{
    ShipExplorerV5 explorer;

    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v62", LoadSceneMode.Single);
        yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);
        explorer.SetWalking(true); explorer.enabled=false;
    }

    [UnityTest] public IEnumerator CabinsHaveSidesRoofAndMoveWithEachLift()
    {
        Assert.That(explorer.lifts.Length,Is.EqualTo(4));
        foreach(var lift in explorer.lifts)
        {
            var pieces=lift.car.GetComponentsInChildren<ShipInstanceV5>(true)
                .Where(p=>p.modelId!=null && p.modelId.StartsWith("V62_CABIN_")).ToArray();
            foreach(var role in new[]{"side_s","side_n","back","front","roof"})
                Assert.That(pieces.Any(p=>p.modelId=="V62_CABIN_"+role),Is.True,lift.id+" "+role);
            foreach(var part in pieces)
            {
                Assert.That(part.GetComponent<BoxCollider>(),Is.Not.Null,part.name);
                Assert.That(Vector3.Distance(part.transform.lossyScale,Vector3.one),Is.LessThan(.0001f));
            }
            lift.ResetToFloor(1);
            var roof=pieces.First(p=>p.modelId=="V62_CABIN_roof");
            float y=roof.transform.position.y;
            lift.RequestFloor(2);float deadline=Time.time+20;
            while(lift.IsMoving && Time.time<deadline) yield return new WaitForFixedUpdate();
            Assert.That(lift.currentFloor,Is.EqualTo(2),lift.id);
            Assert.That(roof.transform.position.y-y,Is.EqualTo(6.4f).Within(.03f),lift.id);
        }
    }

    [UnityTest] public IEnumerator CanWalkIntoAllFourCabinsFromAllThreeDecks()
    {
        var cc=explorer.player;
        foreach(var lift in explorer.lifts) for(int floor=0;floor<3;floor++)
        {
            lift.ResetToFloor(floor);lift.RequestFloor(floor);
            var gate=lift.landings[floor];float deadline=Time.time+6;
            while(!gate.IsOpen && Time.time<deadline) yield return new WaitForFixedUpdate();
            Assert.That(gate.IsOpen,Is.True,lift.id+" gate "+floor);
            cc.enabled=false;cc.transform.position=gate.transform.position+new Vector3(-1,.05f,1.5f);cc.enabled=true;
            Physics.SyncTransforms();float y=cc.transform.position.y;
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
            {
                cc.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);
                yield return new WaitForFixedUpdate();
            }
            Assert.That(cc.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),lift.id+" floor "+floor);
            Assert.That(cc.transform.position.y,Is.EqualTo(y).Within(.3f),lift.id+" floor "+floor);
        }
    }

    [UnityTest] public IEnumerator InsideControlsAreNotBuriedInTheCabinWall()
    {
        foreach(var lift in explorer.lifts)
        {
            lift.ResetToFloor(1);
            var button=lift.car.GetComponentsInChildren<ShipButtonV5>(true).First(b=>b.floor==2);
            var hitTarget=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>
                Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var point=hitTarget.bounds.center;var forward=button.transform.forward;
            Physics.SyncTransforms();
            Assert.That(explorer.TryPressRay(new Ray(point+forward*.5f,-forward),1),Is.True,lift.id+" floor control blocked");
            Assert.That(lift.targetFloor,Is.EqualTo(2),lift.id);
        }
        yield return null;
    }

    [UnityTest] public IEnumerator PlayerCanRideEveryEnclosedCabinToUpperDeck()
    {
        var cc=explorer.player;
        foreach(var lift in explorer.lifts)
        {
            lift.ResetToFloor(1);lift.RequestFloor(1);var gate=lift.landings[1];
            float deadline=Time.time+6;
            while(!gate.IsOpen && Time.time<deadline) yield return new WaitForFixedUpdate();
            Assert.That(gate.IsOpen,Is.True,lift.id);
            cc.enabled=false;cc.transform.position=gate.transform.position+new Vector3(-1,.05f,1.5f);cc.enabled=true;
            Physics.SyncTransforms();
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
            {
                cc.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);
                yield return new WaitForFixedUpdate();
            }
            Assert.That(cc.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),lift.id+" entry");
            float start=cc.transform.position.y;
            lift.RequestFloor(2);deadline=Time.time+25;
            while(lift.IsMoving && Time.time<deadline) yield return new WaitForFixedUpdate();
            Assert.That(lift.currentFloor,Is.EqualTo(2),lift.id);
            Assert.That(cc.transform.position.y-start,Is.EqualTo(6.4f).Within(.25f),lift.id+" rider");
        }
    }

    [UnityTest] public IEnumerator EveryLandingRetainsAnAccessibleCallButton()
    {
        foreach(var lift in explorer.lifts) for(int floor=0;floor<3;floor++)
        {
            Assert.That(explorer.master.GetComponentsInChildren<ShipButtonV5>(true)
                .Any(b=>b.name==lift.id+"_LANDING_"+floor+"_BUTTON_1"),Is.False,lift.id+" shaft-side duplicate");
            var button=explorer.buttons.FirstOrDefault(b=>b!=null && b.lift==lift && b.floor==floor && !b.transform.IsChildOf(lift.car));
            Assert.That(button,Is.Not.Null,lift.id+" floor "+floor);
            var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>
                Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var point=target.bounds.center;var forward=button.transform.forward;
            Physics.SyncTransforms();
            Assert.That(explorer.TryPressRay(new Ray(point+forward*.5f,-forward),1),Is.True,lift.id+" floor "+floor);
            Assert.That(lift.targetFloor,Is.EqualTo(floor),lift.id);
        }
        yield return null;
    }

    [UnityTest] public IEnumerator WallBandsUseCommonWorldHeightsAndBridgeHasCommandStations()
    {
        var walls=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>p.category=="Walls").ToArray();
        Assert.That(walls.Length,Is.GreaterThan(4000));
        foreach(var wall in walls)
        {
            var mesh=wall.GetComponentsInChildren<ShipSolidV5>(true).OrderBy(p=>p.partIndex).First().GetComponent<MeshFilter>().sharedMesh;
            Assert.That(mesh,Is.Not.Null,wall.name);Assert.That(mesh.subMeshCount,Is.EqualTo(2),wall.name);
            var vertices=mesh.vertices;
            foreach(var i in mesh.GetTriangles(1))
            {
                float y=wall.transform.position.y+vertices[i].y;
                float nearest=Mathf.Round(y/3)*3;
                bool stripeEdge=Mathf.Abs(Mathf.Abs(y-nearest)-.06f)<.002f;
                bool clipped=Mathf.Abs(vertices[i].y)<.002f || Mathf.Abs(vertices[i].y-mesh.bounds.max.y)<.002f;
                Assert.That(stripeEdge||clipped,Is.True,wall.name+" y="+y);
            }
        }
        var bridge=explorer.master.transform.Find("V62_BRIDGE_COMMAND");
        Assert.That(bridge,Is.Not.Null);Assert.That(bridge.Find("COMMAND_CHAIR"),Is.Not.Null);
        Assert.That(bridge.Cast<Transform>().Count(x=>x.name.StartsWith("BRIDGE_CONSOLE_")),Is.EqualTo(6));
        Assert.That(bridge.Cast<Transform>().Count(x=>x.name.StartsWith("BRIDGE_VIEWSCREEN_")),Is.EqualTo(5));
        yield return null;
    }

    [UnityTest] public IEnumerator BridgeFurnitureDoesNotPenetrateOtherColliders()
    {
        var bridge=explorer.master.transform.Find("V62_BRIDGE_COMMAND");
        Assert.That(bridge,Is.Not.Null);
        Physics.SyncTransforms();
        foreach(var piece in bridge.GetComponentsInChildren<BoxCollider>(true))
        {
            var center=piece.transform.TransformPoint(piece.center);
            var half=Vector3.Scale(piece.size*.5f,piece.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,piece.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==piece || other.transform.IsChildOf(explorer.player.transform)) continue;
                if(Physics.ComputePenetration(piece,piece.transform.position,piece.transform.rotation,
                    other,other.transform.position,other.transform.rotation,out var direction,out var depth))
                    Assert.That(depth,Is.LessThan(.002f),piece.name+" intersects "+other.name+" depth="+depth);
            }
        }
        yield return null;
    }

    [UnityTest] public IEnumerator PlayerCanOpenAndCrossGateBetweenLargeSectors()
    {
        var gate=explorer.gates.First(g=>g!=null&&g.id=="G_L1_GYM_L1_LAB");
        gate.SetImmediate(0);
        var button=explorer.buttons.First(b=>b!=null&&b.gate==gate&&b.transform.forward.x>.5f);
        var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>
            Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
        var point=target.bounds.center;var forward=button.transform.forward;Physics.SyncTransforms();
        Assert.That(explorer.TryPressRay(new Ray(point+forward*.65f,-forward),1),Is.True,"sector gate button");
        float deadline=Time.time+6;
        while(!gate.IsOpen&&Time.time<deadline) yield return new WaitForFixedUpdate();
        Assert.That(gate.IsOpen,Is.True,"sector gate did not open");
        var cc=explorer.player;cc.enabled=false;
        cc.transform.position=gate.transform.position+new Vector3(1,.05f,1.5f);cc.enabled=true;Physics.SyncTransforms();
        for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
        {
            cc.Move(Vector3.left*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);
            yield return new WaitForFixedUpdate();
        }
        Assert.That(cc.transform.position.x,Is.LessThan(gate.transform.position.x-.65f),"sector gate passage blocked");
    }
}
