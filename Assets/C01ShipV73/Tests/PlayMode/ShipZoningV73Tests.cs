using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipZoningV73Tests
{
    [Serializable] class Plan { public Swap[] swaps;public Relabel[] relabels;public Move[] moves; }
    [Serializable] class Swap { public string original,replacement,label; }
    [Serializable] class Relabel { public string id,label; }
    [Serializable] class Move { public string id,model,zone;public float fromX,toX,y,z; }
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v73",LoadSceneMode.Single);
        yield return null;explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p){var c=explorer.player;c.enabled=false;c.transform.position=p;c.enabled=true;Physics.SyncTransforms();}
    void MoveTo(float x,float z)
    {
        var c=explorer.player;var target=new Vector3(x,c.transform.position.y,z);
        for(int i=0;i<5000;i++){var d=Vector3.ProjectOnPlane(target-c.transform.position,Vector3.up);if(d.magnitude<.08f)return;
            c.Move(Vector3.ClampMagnitude(d,.08f)+Vector3.down*.015f);}
        Assert.Fail("Passage blocked toward "+target+" at "+c.transform.position);
    }
    IEnumerator PressGate(string id)
    {
        var gate=explorer.gates.Single(g=>g!=null&&g.id==id);var button=explorer.buttons.First(b=>b!=null&&b.gate==gate);
        var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
        var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
        Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,id+" button");
        float deadline=Time.time+8;while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();
        Assert.That(gate.IsOpen,Is.True,id+" failed to open");
    }
    [UnityTest] public IEnumerator ZonesAndEquipmentMatchSharedPlan()
    {
        var p=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV73/Data/zoning.json")));
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
        foreach(var s in p.swaps){Assert.That(zones[s.replacement].label,Is.EqualTo(s.label));Assert.That(zones[s.replacement].GetComponentInChildren<TextMesh>(true).text,Is.EqualTo(s.label));}
        foreach(var s in p.relabels){Assert.That(zones[s.id].label,Is.EqualTo(s.label));Assert.That(zones[s.id].GetComponentInChildren<TextMesh>(true).text,Is.EqualTo(s.label));}
        var a=zones["L0_CARGO"].transform.position;var b=zones["L1_CARGO"].transform.position;
        Assert.That(a.x,Is.EqualTo(b.x).Within(.001f));Assert.That(a.z,Is.EqualTo(b.z).Within(.001f));
        foreach(var m in p.moves){var item=all[m.id];Assert.That(item.zoneId,Is.EqualTo(m.zone));Assert.That(item.modelId,Is.EqualTo(m.model));
            Assert.That(item.transform.position.x,Is.EqualTo(m.toX).Within(.001f));Assert.That(item.transform.position.z,Is.EqualTo(m.z).Within(.001f));
            Assert.That(Vector3.Distance(item.transform.lossyScale,Vector3.one),Is.LessThan(.001f));Assert.That(item.GetComponentsInChildren<Collider>(true).Length,Is.GreaterThan(0));}
        yield return null;
    }
    [UnityTest] public IEnumerator CargoAndTechnicalSectorEntrancesAreUsable()
    {
        yield return PressGate("G_L1_S_BRANCH_6_L1_TECH");Place(new Vector3(115.5f,.04f,35));MoveTo(115.5f,31.4f);
        Assert.That(explorer.player.transform.position.z,Is.LessThan(31.6f));
        yield return PressGate("G_L1_CARGO_L1_S_BRANCH_2");Place(new Vector3(31.5f,.04f,35));MoveTo(31.5f,31.4f);
        Assert.That(explorer.player.transform.position.z,Is.LessThan(31.6f));
    }
    [UnityTest] public IEnumerator CargoOfficeAndWorkshopAreAccessible()
    {
        yield return PressGate("G_L1_S_BRANCH_6_L1_S_SUPPORT_11");Place(new Vector3(115,.04f,37.5f));MoveTo(112.3f,37.5f);
        Assert.That(explorer.player.transform.position.x,Is.LessThan(112.5f));
        yield return PressGate("G_L1_S_BRANCH_2_L1_S_SUPPORT_03");Place(new Vector3(31,.04f,37.5f));MoveTo(28.3f,37.5f);
        Assert.That(explorer.player.transform.position.x,Is.LessThan(28.5f));
    }
    [UnityTest] public IEnumerator MovedEquipmentDoesNotPenetrateOtherColliders()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV73/Data/zoning.json")));
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
        Physics.SyncTransforms();
        foreach(var m in plan.moves)foreach(var part in all[m.id].GetComponentsInChildren<BoxCollider>(true))
        {
            var center=part.transform.TransformPoint(part.center);var half=Vector3.Scale(part.size*.5f,part.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,part.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==part||other.transform.IsChildOf(explorer.player.transform))continue;
                if(Physics.ComputePenetration(part,part.transform.position,part.transform.rotation,other,other.transform.position,other.transform.rotation,out var dir,out var depth))
                    Assert.That(depth,Is.LessThan(.002f),m.id+"/"+part.name+" intersects "+other.name);
            }
        }
        yield return null;
    }
}
