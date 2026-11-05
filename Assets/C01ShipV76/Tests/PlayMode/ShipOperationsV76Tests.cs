using System;
using System.Collections;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using Object=UnityEngine.Object;

public class ShipOperationsV76Tests
{
    [Serializable] class Move {public string id,model,fromZone,toZone;public float[] before,after;}
    [Serializable] class Label {public string id,fromLabel,label;}
    [Serializable] class Plan {public Move[] moves;public Label[] labels;public PlacementDataV5[] added;public GateDataV5 gate;}
    ShipExplorerV5 explorer;Plan plan;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v76",LoadSceneMode.Single);yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
        plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV76/Data/operations.json")));
    }
    void Place(Vector3 p){var c=explorer.player;c.enabled=false;c.transform.position=p;c.enabled=true;Physics.SyncTransforms();}
    [UnityTest] public IEnumerator ChangedRoomsAndEquipmentMatchPlan()
    {
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        var items=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        foreach(var l in plan.labels)Assert.That(zones[l.id].label,Is.EqualTo(l.label),l.id);
        foreach(var move in plan.moves)
        {
            var item=items[move.id];Assert.That(item.zoneId,Is.EqualTo(move.toZone),move.id);
            Assert.That(Vector3.Distance(item.transform.position,new Vector3(move.after[0],move.after[1],move.after[2])),Is.LessThan(.002f),move.id);
            Assert.That(Quaternion.Angle(item.transform.rotation,Quaternion.Euler(0,move.after[3],0)),Is.LessThan(.05f),move.id);
        }
        Assert.That(zones.ContainsKey("L0_LAUNCH_EXIT"),Is.True);yield return null;
    }
    [UnityTest] public IEnumerator LaunchGateButtonsWorkFromBothSides()
    {
        var gate=explorer.gates.Single(g=>g!=null&&g.id=="L0_LAUNCH_GATE");Assert.That(gate.IsClosed,Is.True);
        foreach(int side in new[]{0,1})
        {
            var button=explorer.buttons.Single(b=>b!=null&&b.gate==gate&&b.GetComponent<ShipInstanceV5>().placementId==plan.gate.buttons[side]);
            var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var point=target.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();
            Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,"button "+side);
            float deadline=Time.time+6;while((side==0?!gate.IsOpen:!gate.IsClosed)&&Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(side==0?gate.IsOpen:gate.IsClosed,Is.True,"gate state "+side);
        }
    }
    string Sweep(GameObject shuttle,float from,float to,float increment)
    {
        var parts=shuttle.GetComponentsInChildren<BoxCollider>(true);Assert.That(parts.Length,Is.GreaterThan(0));Physics.SyncTransforms();
        for(float distance=from;distance<=to+.001f;distance+=increment)foreach(var part in parts)
        {
            var position=part.transform.position+Vector3.forward*distance;
            var center=part.transform.TransformPoint(part.center)+Vector3.forward*distance;
            var half=Vector3.Scale(part.size*.5f,part.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,part.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==part||other.transform.IsChildOf(shuttle.transform)||other.transform.IsChildOf(explorer.player.transform))continue;
                if(Physics.ComputePenetration(part,position,part.transform.rotation,other,other.transform.position,other.transform.rotation,out var dir,out var depth)&&depth>.002f)
                {
                    var marker=other.GetComponentInParent<ShipInstanceV5>();
                    return (marker!=null?marker.placementId:other.name)+" depth="+depth+" at z+"+distance;
                }
            }
        }
        return null;
    }
    [UnityTest] public IEnumerator ShuttleFitsThroughOpenLaunchGateButNotClosed()
    {
        var gate=explorer.gates.Single(g=>g!=null&&g.id=="L0_LAUNCH_GATE");
        var shuttle=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Single(m=>m.placementId=="L0_EVAC_HANGAR_EVAC_SHUTTLE").gameObject;
        gate.SetImmediate(0);var blocked=Sweep(shuttle,0,18,.25f);Assert.That(blocked,Does.Contain("L0_LAUNCH_LEAF"),"closed gate should block the shuttle");
        gate.SetImmediate(1);var hit=Sweep(shuttle,0,18,.25f);Assert.That(hit,Is.Null,"open route collision: "+hit);yield return null;
    }
    [UnityTest] public IEnumerator MovedSupportRoomsAreReachableFromTheirBranches()
    {
        foreach(var id in new[]{"G_L2_S_BRANCH_2_L2_S_SUPPORT_03","G_L2_S_BRANCH_4_L2_S_SUPPORT_07","G_L2_N_BRANCH_4_L2_N_SUPPORT_07","G_L2_N_BRANCH_4_L2_N_SUPPORT_08","G_L2_S_BRANCH_6_L2_S_SUPPORT_11","G_L2_S_BRANCH_6_L2_S_SUPPORT_12"})
        {
            var gate=explorer.gates.Single(g=>g!=null&&g.id==id);gate.SetImmediate(1);Physics.SyncTransforms();
            var center=gate.transform.position+gate.transform.right*1.5f;var across=gate.transform.forward;
            Place(center-across+Vector3.up*.04f);
            for(int i=0;i<35;i++)explorer.player.Move(across*.08f+Vector3.down*.015f);
            Assert.That(Vector3.Dot(explorer.player.transform.position-center,across),Is.GreaterThan(.6f),id+" at "+explorer.player.transform.position);
        }
        yield return null;
    }
}
