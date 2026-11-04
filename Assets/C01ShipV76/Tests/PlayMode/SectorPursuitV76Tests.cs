using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class SectorPursuitV76Tests
{
    [Serializable] class Plan { public PlacementDataV5[] added;public GateDataV5[] gates;public string[] removed; }
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v76",LoadSceneMode.Single);
        yield return null;explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p){var c=explorer.player;c.enabled=false;c.transform.position=p;c.enabled=true;Physics.SyncTransforms();}
    void MoveTo(float x,float z)
    {
        var c=explorer.player;var target=new Vector3(x,c.transform.position.y,z);
        for(int i=0;i<7000;i++)
        {
            var d=Vector3.ProjectOnPlane(target-c.transform.position,Vector3.up);if(d.magnitude<.08f)return;
            c.Move(Vector3.ClampMagnitude(d,.08f)+Vector3.down*.015f);
        }
        Assert.Fail("Blocked toward "+target+" at "+c.transform.position);
    }
    void CrossCatwalk(float startX,float z0)
    {
        MoveTo(startX+4.8f,z0+1.5f);MoveTo(startX+4.8f,z0+2.2f);
        MoveTo(startX+7.1f,z0+2.2f);MoveTo(startX+10.8f,z0+2.2f);MoveTo(startX+10.8f,z0+.8f);
        MoveTo(startX+13.1f,z0+.8f);MoveTo(startX+16.8f,z0+.8f);MoveTo(startX+16.8f,z0+2.2f);
        MoveTo(startX+19.1f,z0+2.2f);MoveTo(startX+22.5f,z0+2.2f);MoveTo(startX+22.5f,z0+1.5f);
    }
    [UnityTest] public IEnumerator CompletePursuitPassesThroughAllThreeSectorsToExit()
    {
        var gates=explorer.gates.Where(g=>g!=null&&g.id.StartsWith("L2_ROUTE_")).ToArray();
        Assert.That(gates.Length,Is.EqualTo(6));Assert.That(gates.All(g=>g.IsOpen),Is.True,"Pursuit gates should start open");
        Place(new Vector3(-34.5f,3.44f,55.5f));MoveTo(-13.5f,55.5f);MoveTo(-13.5f,43.5f);MoveTo(2,43.5f);
        MoveTo(7.5f,44.2f);MoveTo(10.5f,44.2f);MoveTo(10.5f,55.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(54.8f));CrossCatwalk(9,54);
        MoveTo(31.5f,43.7f);MoveTo(31.5f,44.2f);MoveTo(34.2f,44.2f);MoveTo(49.5f,44.2f);
        MoveTo(49.5f,42.8f);MoveTo(52.5f,42.8f);MoveTo(52.5f,31.5f);
        Assert.That(explorer.player.transform.position.z,Is.LessThan(32.2f));CrossCatwalk(51,30);
        MoveTo(73.5f,42.8f);MoveTo(76.2f,42.8f);MoveTo(91.5f,42.8f);MoveTo(91.5f,44.2f);
        MoveTo(94.5f,44.2f);MoveTo(94.5f,55.5f);Assert.That(explorer.player.transform.position.z,Is.GreaterThan(54.8f));
        CrossCatwalk(93,54);MoveTo(115.5f,44.2f);MoveTo(118.2f,44.2f);MoveTo(127.5f,43.5f);
        MoveTo(136.5f,43.5f);MoveTo(136.5f,67.5f);MoveTo(133.5f,67.5f);MoveTo(133.5f,73.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(72.5f));yield return null;
    }
    [UnityTest] public IEnumerator CorridorBulkheadsBlockTheStraightShortcut()
    {
        foreach(float x in new[]{18f,60f,102f})
        {
            Place(new Vector3(x-1f,3.44f,43.5f));var c=explorer.player;
            for(int i=0;i<80;i++)c.Move(Vector3.right*.08f+Vector3.down*.015f);
            Assert.That(c.transform.position.x,Is.LessThan(x-.25f),"Bulkhead at "+x+" did not block the player");
        }
        yield return null;
    }
    [UnityTest] public IEnumerator EachNewGateHasUsableButtonsOnBothSides()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV74/Data/pursuit.json")));
        foreach(var g in plan.gates)
        {
            var gate=explorer.gates.Single(x=>x!=null&&x.id==g.id);
            Assert.That(gate.IsOpen,Is.True,g.id);
            foreach(int side in new[]{0,1})
            {
                var button=explorer.buttons.Single(x=>x!=null&&x.gate==gate&&x.GetComponent<ShipInstanceV5>().placementId==g.buttons[side]);
                var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
                var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
                Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,g.id+" button "+side);
                float deadline=Time.time+6;while((side==0?!gate.IsClosed:!gate.IsOpen)&&Time.time<deadline)yield return new WaitForFixedUpdate();
                Assert.That(side==0?gate.IsClosed:gate.IsOpen,Is.True,g.id+" state "+side);
            }
        }
    }
    [UnityTest] public IEnumerator NewModulesArePresentWithCollidersAndUnitScale()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV74/Data/pursuit.json")));
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
        foreach(var id in plan.removed)Assert.That(all.ContainsKey(id),Is.False,id);
        foreach(var p in plan.added)
        {
            Assert.That(all.TryGetValue(p.id,out var item),Is.True,p.id);Assert.That(item.modelId,Is.EqualTo(p.model));
            Assert.That(Vector3.Distance(item.transform.lossyScale,Vector3.one),Is.LessThan(.001f),p.id);
            Assert.That(item.GetComponentsInChildren<Collider>(true).Length,Is.GreaterThan(0),p.id);
            if(p.category!="GateLeaves")Assert.That(Vector3.Distance(item.transform.position,new Vector3(p.x,p.y,p.z)),Is.LessThan(.002f),p.id);
        }
        yield return null;
    }
}
