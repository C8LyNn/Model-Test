using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class BridgeEdgeV72RegressionTests
{
    [Serializable] class Delta { public Placement[] added, changed; public string[] removed; public Lift[] lifts; }
    [Serializable] class Placement { public string id, model, category, parent; public float x,y,z,yaw; }
    [Serializable] class Lift { public string id; public float x,z; public float[] bounds; }
    ShipExplorerV5 explorer;

    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v72",LoadSceneMode.Single);
        yield return null;
        explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null); explorer.SetWalking(true); explorer.enabled=false;
    }
    void Place(Vector3 p)
    {
        var cc=explorer.player;cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms();
    }
    void MoveTo(float x,float z)
    {
        var cc=explorer.player;var target=new Vector3(x,cc.transform.position.y,z);
        for(int i=0;i<8000;i++)
        {
            var delta=Vector3.ProjectOnPlane(target-cc.transform.position,Vector3.up);
            if(delta.magnitude<.08f)return;
            cc.Move(Vector3.ClampMagnitude(delta,.08f)+Vector3.down*.015f);
        }
        Assert.Fail("Passage blocked toward "+target+" at "+cc.transform.position);
    }
    [UnityTest] public IEnumerator SceneMatchesLayoutAndRetainsEditableModules()
    {
        var plan=JsonUtility.FromJson<Delta>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV71/Data/bridge_delta.json")));
        var markers=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true)
            .Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
        foreach(var id in plan.removed) Assert.That(markers.ContainsKey(id),Is.False,id);
        foreach(var item in plan.added)
        {
            Assert.That(markers.TryGetValue(item.id,out var instance),Is.True,item.id);
            Assert.That(instance.modelId,Is.EqualTo(item.model),item.id);
            Assert.That(Vector3.Distance(instance.transform.position,new Vector3(item.x,item.y,item.z)),Is.LessThan(.002f),item.id);
            Assert.That(Vector3.Distance(instance.transform.lossyScale,Vector3.one),Is.LessThan(.002f),item.id);
            Assert.That(instance.GetComponentsInChildren<Collider>(true).Length,Is.GreaterThan(0),item.id);
        }
        foreach(var item in plan.lifts)
        {
            var lift=explorer.lifts.Single(x=>x.id==item.id);
            Assert.That(lift.car.position.x,Is.EqualTo(item.x).Within(.001f));
            Assert.That(lift.car.position.z,Is.EqualTo(item.z).Within(.001f));
            Assert.That(lift.footprint.x,Is.EqualTo(item.bounds[0]).Within(.001f));
            Assert.That(lift.footprint.w,Is.EqualTo(item.bounds[3]).Within(.001f));
        }
        Assert.That(plan.lifts.Sum(x=>x.z),Is.EqualTo(87).Within(.001f));
        yield return null;
    }
    [UnityTest] public IEnumerator PlayerCanReachBothLiftEntrancesOnEveryDeck()
    {
        foreach(float y in new[]{-3.4f,0f,3.4f})
        foreach(float z in new[]{22.5f,64.5f})
        {
            Place(new Vector3(-4.5f,y+.04f,43.5f));
            MoveTo(-13.4f,43.5f); MoveTo(-13.4f,z);
            Assert.That(Mathf.Abs(explorer.player.transform.position.z-z),Is.LessThan(.1f));
        }
        yield return null;
    }
    [UnityTest] public IEnumerator BothLiftsOpenAndCarryPlayerFromDeckOneToTwo()
    {
        foreach(string id in new[]{"BRIDGE_PASSENGER","BRIDGE_PASSENGER_N"})
        {
            var lift=explorer.lifts.Single(l=>l!=null&&l.id==id);
            lift.ResetToFloor(1);lift.RequestFloor(1);var landing=lift.landings[1];
            float deadline=Time.time+6;
            while(!landing.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(landing.IsOpen,Is.True,id+" failed to open");
            Place(landing.transform.position+new Vector3(-1,.05f,1.5f));
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
            {explorer.player.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That(explorer.player.transform.position.x,Is.GreaterThan(landing.transform.position.x+.65f),id+" entry");
            var y=explorer.player.transform.position.y;lift.RequestFloor(2);deadline=Time.time+25;
            while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(lift.currentFloor,Is.EqualTo(2),id);
            Assert.That(explorer.player.transform.position.y-y,Is.EqualTo(3.4f).Within(.25f),id+" rider");
        }
    }
    [UnityTest] public IEnumerator LiftLandingButtonsAreUsableOnAllDecks()
    {
        foreach(string id in new[]{"BRIDGE_PASSENGER","BRIDGE_PASSENGER_N"})
        {
            var lift=explorer.lifts.Single(l=>l!=null&&l.id==id);
            for(int floor=0;floor<3;floor++)
            {
                lift.ResetToFloor(floor);
                var gate=lift.landings[floor];
                var button=explorer.buttons.First(b=>b!=null&&b.lift==lift&&b.floor==floor&&b.gate==gate);
                var target=button.GetComponentsInChildren<Collider>()
                    .OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
                var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
                Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,id+" button "+floor);
                float deadline=Time.time+6;
                while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();
                Assert.That(gate.IsOpen,Is.True,id+" landing "+floor);
            }
        }
    }
    [UnityTest] public IEnumerator BridgeStationsDoNotIntersectOtherColliders()
    {
        var stations=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>p.zoneId=="L1_BRIDGE"&&p.category=="CoreStations").ToArray();
        Assert.That(stations.Length,Is.EqualTo(24)); Physics.SyncTransforms();
        foreach(var station in stations)foreach(var part in station.GetComponentsInChildren<BoxCollider>(true))
        {
            var center=part.transform.TransformPoint(part.center);var half=Vector3.Scale(part.size*.5f,part.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,part.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==part||other.transform.IsChildOf(explorer.player.transform))continue;
                if(Physics.ComputePenetration(part,part.transform.position,part.transform.rotation,other,other.transform.position,other.transform.rotation,out var direction,out var depth))
                    Assert.That(depth,Is.LessThan(.002f),station.placementId+"/"+part.name+" intersects "+other.name);
            }
        }
        yield return null;
    }
}
