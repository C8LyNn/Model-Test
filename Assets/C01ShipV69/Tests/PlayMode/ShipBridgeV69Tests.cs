using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipBridgeV69Tests
{
    [Serializable] class Layout { public Placement[] placements; }
    [Serializable] class Placement { public string id,model; public float x,y,z,yaw; }
    ShipExplorerV5 explorer;

    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v69",LoadSceneMode.Single);
        yield return null;
        explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p)
    {
        var cc=explorer.player;cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms();
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
    [UnityTest] public IEnumerator SceneUsesTheSharedBridgeLayoutAndSeparateModules()
    {
        var layout=JsonUtility.FromJson<Layout>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV69/Data/bridge_layout.json")));
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>p.zoneId=="L1_BRIDGE"&&p.category=="CoreStations").ToArray();
        Assert.That(all.Length,Is.EqualTo(19));Assert.That(layout.placements.Length,Is.EqualTo(19));
        foreach(var p in layout.placements)
        {
            var item=all.SingleOrDefault(q=>q.placementId==p.id);Assert.That(item,Is.Not.Null,p.id);
            Assert.That(item.modelId,Is.EqualTo(p.model));
            Assert.That(Vector3.Distance(item.transform.position,new Vector3(p.x,p.y,p.z)),Is.LessThan(.001f),p.id);
            Assert.That(Vector3.Distance(item.transform.lossyScale,Vector3.one),Is.LessThan(.001f),p.id);
            Assert.That(item.GetComponentsInChildren<Collider>().Length,Is.GreaterThan(0),p.id);
        }
        yield return null;
    }
    [UnityTest] public IEnumerator StationsDoNotPenetrateOtherGeometry()
    {
        var stations=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>p.zoneId=="L1_BRIDGE"&&p.category=="CoreStations").ToArray();
        Physics.SyncTransforms();
        foreach(var station in stations)foreach(var part in station.GetComponentsInChildren<BoxCollider>(true))
        {
            var center=part.transform.TransformPoint(part.center);var half=Vector3.Scale(part.size*.5f,part.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,part.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==part||other.transform.IsChildOf(explorer.player.transform))continue;
                if(Physics.ComputePenetration(part,part.transform.position,part.transform.rotation,other,other.transform.position,other.transform.rotation,out var direction,out var depth))
                    Assert.That(depth,Is.LessThan(.002f),station.placementId+"/"+part.name+" intersects "+other.name+" depth="+depth);
            }
        }
        yield return null;
    }
    [UnityTest] public IEnumerator PlayerCanReachFlightAndSideStations()
    {
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-20,43.5f);MoveTo(-20,41.5f);MoveTo(-27,41.5f);
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-20,43.5f);MoveTo(-20,45.5f);MoveTo(-27,45.5f);
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-13,43.5f);MoveTo(-13,36);MoveTo(-19.7f,36);MoveTo(-19.7f,38.1f);
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-13,43.5f);MoveTo(-13,51);MoveTo(-19.7f,51);MoveTo(-19.7f,48.9f);
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-13,43.5f);MoveTo(-13,39.6f);MoveTo(-13.8f,39.6f);
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-13,43.5f);MoveTo(-13,47.4f);MoveTo(-13.8f,47.4f);
        yield return null;
    }
    [UnityTest] public IEnumerator UpperChaseGalleryStillConnectsBridgeToExit()
    {
        Place(new Vector3(-34.5f,3.44f,55.5f));MoveTo(-13.5f,55.5f);MoveTo(-13.5f,43.5f);MoveTo(2,43.5f);int i=0;
        foreach(float x in new[]{9f,21f,33f,51f,63f,75f,93f,105f,117f})
        {MoveTo(x-1.3f,explorer.player.transform.position.z);MoveTo(x-1.3f,i%2==0?44.2f:42.8f);MoveTo(x+1.3f,i%2==0?44.2f:42.8f);i++;}
        MoveTo(127.5f,43.5f);MoveTo(136.5f,43.5f);MoveTo(136.5f,67.5f);MoveTo(133.5f,67.5f);MoveTo(133.5f,73.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(72.5f));yield return null;
    }
    [UnityTest] public IEnumerator BothPassengerLiftApproachesRemainReachable()
    {
        foreach(var z in new[]{31.5f,55.5f})
        {
            Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-13,43.5f);MoveTo(-13,z);
            Assert.That(Mathf.Abs(explorer.player.transform.position.z-z),Is.LessThan(.1f));
        }
        yield return null;
    }
    [UnityTest] public IEnumerator BridgeGateButtonAndPassengerLiftStillOperate()
    {
        var gate=explorer.gates.Single(g=>g!=null&&g.id=="G_L1_BRIDGE_L1_MAIN");
        var button=explorer.buttons.First(b=>b!=null&&b.gate==gate);
        gate.SetImmediate(0);
        var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
        var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
        Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,"Bridge gate button");
        float deadline=Time.time+6;while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();
        Assert.That(gate.IsOpen,Is.True,"Bridge gate did not open");
        var lift=explorer.lifts.Single(l=>l!=null&&l.id=="BRIDGE_PASSENGER");
        lift.ResetToFloor(1);lift.RequestFloor(1);var landing=lift.landings[1];deadline=Time.time+6;
        while(!landing.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(landing.IsOpen,Is.True);
        Place(landing.transform.position+new Vector3(-1,.05f,1.5f));
        for(float t=0;t<2.5f;t+=Time.fixedDeltaTime){explorer.player.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
        Assert.That(explorer.player.transform.position.x,Is.GreaterThan(landing.transform.position.x+.65f));
        var y=explorer.player.transform.position.y;lift.RequestFloor(2);deadline=Time.time+25;
        while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();
        Assert.That(lift.currentFloor,Is.EqualTo(2));Assert.That(explorer.player.transform.position.y-y,Is.EqualTo(3.4f).Within(.25f));
    }
}
