using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipLogisticsV72Tests
{
    [Serializable] class Plan { public Swap[] swaps; public Move[] moves; }
    [Serializable] class Swap { public string original,replacement,label; }
    [Serializable] class Move { public string id,model,zone; public float fromX,toX,fromZ,toZ,y; }
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v72",LoadSceneMode.Single);
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
        Assert.Fail("Blocked toward "+target+" at "+cc.transform.position);
    }
    IEnumerator PressGate(string id)
    {
        var gate=explorer.gates.Single(g=>g!=null && g.id==id);
        var button=explorer.buttons.First(b=>b!=null && b.gate==gate);
        var target=button.GetComponentsInChildren<Collider>()
            .OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
        var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
        Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,id+" button");
        float deadline=Time.time+8;
        while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();
        Assert.That(gate.IsOpen,Is.True,id+" did not open");
    }
    [UnityTest] public IEnumerator NewSectorNamesAndEquipmentMatchThePlan()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV72/Data/logistics.json")));
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true)
            .Where(p=>!string.IsNullOrEmpty(p.placementId)).ToDictionary(p=>p.placementId);
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        foreach(var swap in plan.swaps)
        {
            Assert.That(zones.TryGetValue(swap.replacement,out var zone),Is.True,swap.replacement);
            Assert.That(zone.label,Is.EqualTo(swap.label));
            Assert.That(zone.GetComponentInChildren<TextMesh>(true).text,Is.EqualTo(swap.label));
        }
        Assert.That(zones["L0_ENGINE_ROOM"].transform.position.x,Is.EqualTo(63).Within(.001f));
        Assert.That(zones["L0_ENGINE_ROOM"].transform.position.z,Is.EqualTo(24).Within(.001f));
        Assert.That(zones["L0_CARGO"].transform.position.x,Is.EqualTo(105).Within(.001f));
        Assert.That(zones["L0_FOOD_RESERVE"].transform.position.x,Is.EqualTo(21).Within(.001f));
        foreach(var p in plan.moves)
        {
            Assert.That(all.TryGetValue(p.id,out var item),Is.True,p.id);
            Assert.That(item.modelId,Is.EqualTo(p.model));Assert.That(item.zoneId,Is.EqualTo(p.zone));
            Assert.That(item.transform.position.x,Is.EqualTo(p.toX).Within(.001f),p.id);
            Assert.That(item.transform.position.y,Is.EqualTo(p.y).Within(.001f),p.id);
            Assert.That(item.transform.position.z,Is.EqualTo(p.toZ).Within(.001f),p.id);
            Assert.That(Vector3.Distance(item.transform.lossyScale,Vector3.one),Is.LessThan(.001f),p.id);
            Assert.That(item.GetComponentsInChildren<Collider>(true).Length,Is.GreaterThan(0),p.id);
        }
        yield return null;
    }
    [UnityTest] public IEnumerator EngineeringRoomIsAccessibleFromTheCentralPassage()
    {
        yield return PressGate("G_L0_HYDROPONICS_L0_S_ACCESS_1");
        Place(new Vector3(64.5f,-3.36f,35));MoveTo(64.5f,31.4f);
        Assert.That(explorer.player.transform.position.z,Is.LessThan(31.6f));
    }
    [UnityTest] public IEnumerator CargoConnectsToFreightDockThroughWorkingAirlock()
    {
        yield return PressGate("L0_FREIGHT_INNER");
        Place(new Vector3(124.5f,-3.36f,22.5f));MoveTo(127.8f,22.5f);
        Assert.That(explorer.player.transform.position.x,Is.GreaterThan(127.5f));
    }
    [UnityTest] public IEnumerator HydroponicsIsAccessibleFromTheServicePassage()
    {
        yield return PressGate("G_L0_ENGINE_ROOM_L0_N_ACCESS_0");
        Place(new Vector3(23.1f,-3.36f,52));MoveTo(23.1f,57.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(57.3f));
    }
    [UnityTest] public IEnumerator HydroponicsConnectsToWaterPurification()
    {
        yield return PressGate("G_L0_ENGINE_ROOM_L0_PURIFICATION");
        Place(new Vector3(40.8f,-3.36f,61.5f));MoveTo(43.5f,61.5f);
        Assert.That(explorer.player.transform.position.x,Is.GreaterThan(43.3f));
    }
}
