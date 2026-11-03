using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV67PlayTests
{
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v67", LoadSceneMode.Single);
        yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);
        explorer.SetWalking(true); explorer.enabled=false;
    }
    void Place(Vector3 p)
    {
        var cc=explorer.player; cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms();
    }
    void MoveTo(float x,float z)
    {
        var cc=explorer.player;var target=new Vector3(x,cc.transform.position.y,z);
        for(int i=0;i<5000;i++)
        {
            var delta=Vector3.ProjectOnPlane(target-cc.transform.position,Vector3.up);
            if(delta.magnitude<.08f)return;
            cc.Move(Vector3.ClampMagnitude(delta,.08f)+Vector3.down*.015f);
        }
        Assert.Fail("Passage blocked toward "+target+" at "+cc.transform.position);
    }
    [UnityTest] public IEnumerator ChaseRouteConnectsBridgeObstaclesAndExit()
    {
        Place(new Vector3(-43.5f,3.44f,43.5f));
        MoveTo(2,43.5f);
        int i=0;
        foreach(float x in new[]{9f,21f,33f,51f,63f,75f,93f,105f,117f})
        {
            MoveTo(x-1.3f,explorer.player.transform.position.z);
            MoveTo(x-1.3f,i%2==0?44.2f:42.8f);
            MoveTo(x+1.3f,i%2==0?44.2f:42.8f);
            i++;
        }
        MoveTo(127.5f,43.5f);
        MoveTo(136.5f,43.5f);
        MoveTo(136.5f,67.5f);
        MoveTo(133.5f,67.5f);
        MoveTo(133.5f,73.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(72.5f));
        yield return null;
    }
    [UnityTest] public IEnumerator AtriumHalfStoreyStairIsUsable()
    {
        Place(new Vector3(-14.35f,.04f,30.6f));
        MoveTo(-19.5f,30.6f);
        Assert.That(explorer.player.transform.position.y,Is.GreaterThan(1.3f));
        yield return null;
    }
    [UnityTest] public IEnumerator SizesAndSpeedsMatchRequestedGrid()
    {
        Assert.That(explorer.walkSpeed,Is.GreaterThan(2.5f));
        Assert.That(explorer.walkSpeed*explorer.sprintMultiplier,Is.GreaterThan(5f));
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        foreach(var z in zones.Where(z=>z.kind!="core" && z.kind!="void" && z.kind!="exterior"))
            Assert.That(z.height,Is.EqualTo(3).Within(.001f),z.zoneId);
        foreach(var id in new[]{"L0_BRIDGE","L0_STERN"})
            Assert.That(zones.First(z=>z.zoneId==id).height,Is.EqualTo(12).Within(.001f),id);
        foreach(var lift in explorer.lifts) CollectionAssert.AreEqual(new[]{-3.4f,0f,3.4f},lift.elevations,lift.id);
        yield return null;
    }
    [UnityTest] public IEnumerator BridgeStationsDoNotIntersectOtherColliders()
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
                if(Physics.ComputePenetration(piece,piece.transform.position,piece.transform.rotation,other,other.transform.position,other.transform.rotation,out var direction,out var depth))
                    Assert.That(depth,Is.LessThan(.002f),piece.transform.parent.name+"/"+piece.name+" intersects "+other.name+" depth="+depth);
            }
        }
        yield return null;
    }
    [UnityTest] public IEnumerator PassengerAndCargoLiftCarryPlayerAndCamera()
    {
        var reps=new[]{explorer.lifts.First(l=>!l.id.StartsWith("STERN_CARGO")),explorer.lifts.First(l=>l.id.StartsWith("STERN_CARGO"))};
        foreach(var lift in reps)
        {
            lift.ResetToFloor(1);lift.RequestFloor(1);var gate=lift.landings[1];float deadline=Time.time+6;
            while(!gate.IsOpen && Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(gate.IsOpen,Is.True,lift.id);
            Place(gate.transform.position+new Vector3(-1,.05f,1.5f));
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime){explorer.player.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That(explorer.player.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),lift.id+" entry");
            float y=explorer.player.transform.position.y;float eye=explorer.view.transform.position.y;
            var button=lift.car.GetComponentsInChildren<ShipButtonV5>(true).First(b=>b.floor==2);
            var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var p=target.bounds.center;var f=button.transform.forward;Physics.SyncTransforms();
            Assert.That(explorer.TryPressRay(new Ray(p+f*.5f,-f),1),Is.True,lift.id+" button");
            deadline=Time.time+25;while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(lift.currentFloor,Is.EqualTo(2),lift.id);
            Assert.That(explorer.player.transform.position.y-y,Is.EqualTo(3.4f).Within(.25f),lift.id);
            Assert.That(explorer.view.transform.position.y-eye,Is.EqualTo(3.4f).Within(.25f),lift.id+" camera");
        }
    }
}
