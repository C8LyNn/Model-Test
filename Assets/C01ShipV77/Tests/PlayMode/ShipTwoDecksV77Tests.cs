using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V6.Cargo;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipTwoDecksV77Tests
{
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v77",LoadSceneMode.Single);yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p){var c=explorer.player;c.enabled=false;c.transform.position=p;c.enabled=true;Physics.SyncTransforms();}
    [UnityTest] public IEnumerator DeckZeroAndItsControlsAreGone()
    {
        var markers=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        Assert.That(markers.Count(m=>m.deck==0),Is.Zero);Assert.That(zones.Count(z=>z.deck==0),Is.Zero);
        Assert.That(markers.Count(m=>m.deck==-1&&(m.category=="Walls"||m.category=="Nodes")&&m.transform.position.y<-.401f),Is.Zero);
        Assert.That(explorer.gates.All(g=>g!=null&&!g.id.Contains("L0_")),Is.True);
        Assert.That(explorer.buttons.All(b=>b!=null&&(b.lift==null||b.floor!=0)),Is.True);
        foreach(var lift in explorer.lifts){Assert.That(lift.landings[0],Is.Null,lift.id);Assert.That(lift.landings[1],Is.Not.Null,lift.id);Assert.That(lift.landings[2],Is.Not.Null,lift.id);}
        explorer.SetWalking(false);explorer.SetDeck(0);Assert.That(explorer.selectedDeck,Is.EqualTo(1));explorer.ShowAll(true);Assert.That(explorer.selectedDeck,Is.EqualTo(-1));
        Assert.That(markers.Count(m=>m.category=="ShaftBases"),Is.EqualTo(12));yield return null;
    }
    [UnityTest] public IEnumerator ServicesAreRelocatedAndShuttleGateWorks()
    {
        var markers=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);
        foreach(string id in new[]{"L1_ENGINE_REACTOR_0","L1_ENGINE_REACTOR_1","L1_LAB_PURIFIER_0","L1_CARGO_EVAC_SHUTTLE"})Assert.That(markers.Any(m=>m.placementId==id&&m.deck==1),Is.True,id);
        Assert.That(markers.Count(m=>m.modelId=="P_Plant"&&m.zoneId=="L1_LAB"),Is.EqualTo(15));
        var gate=explorer.gates.Single(g=>g!=null&&g.id=="L1_LAUNCH_GATE");Assert.That(gate.IsClosed,Is.True);
        foreach(int side in new[]{0,1})
        {
            var button=explorer.buttons.Single(b=>b!=null&&b.gate==gate&&b.GetComponent<ShipInstanceV5>().placementId=="L1_LAUNCH_BUTTON_"+side);
            var col=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var point=col.bounds.center;var facing=button.transform.forward;Physics.SyncTransforms();Assert.That(explorer.TryPressRay(new Ray(point+facing*.9f,-facing),1.5f),Is.True,"side "+side);
            var deadline=Time.time+6;while((side==0?!gate.IsOpen:!gate.IsClosed)&&Time.time<deadline)yield return new WaitForFixedUpdate();
            Assert.That(side==0?gate.IsOpen:gate.IsClosed,Is.True,"side "+side);
        }
    }
    string Sweep(GameObject shuttle,float to)
    {
        var parts=shuttle.GetComponentsInChildren<BoxCollider>(true);Assert.That(parts.Length,Is.GreaterThan(0));Physics.SyncTransforms();
        for(float d=0;d<=to+.001f;d+=.25f)foreach(var part in parts)
        {
            var shift=Vector3.back*d;var center=part.transform.TransformPoint(part.center)+shift;var half=Vector3.Scale(part.size*.5f,part.transform.lossyScale);
            foreach(var other in Physics.OverlapBox(center,half,part.transform.rotation,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore))
            {
                if(other==part||other.transform.IsChildOf(shuttle.transform)||other.transform.IsChildOf(explorer.player.transform))continue;
                if(Physics.ComputePenetration(part,part.transform.position+shift,part.transform.rotation,other,other.transform.position,other.transform.rotation,out var direction,out var depth)&&depth>.002f)
                {var m=other.GetComponentInParent<ShipInstanceV5>();return (m!=null?m.placementId:other.name)+" depth="+depth+" at "+d;}
            }
        }
        return null;
    }
    [UnityTest] public IEnumerator ShuttleFitsExitAndClosedGateBlocksIt()
    {
        var gate=explorer.gates.Single(g=>g!=null&&g.id=="L1_LAUNCH_GATE");
        var shuttle=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Single(m=>m.placementId=="L1_CARGO_EVAC_SHUTTLE").gameObject;
        gate.SetImmediate(0);Assert.That(Sweep(shuttle,18),Does.Contain("L1_LAUNCH_LEAF"));
        gate.SetImmediate(1);var hit=Sweep(shuttle,18);Assert.That(hit,Is.Null,"open launch route: "+hit);yield return null;
    }
    [UnityTest] public IEnumerator PassengerAndCargoLiftsWorkOnlyBetweenOneAndTwo()
    {
        var representatives=new[]{explorer.lifts.First(l=>!l.id.StartsWith("STERN_CARGO")),explorer.lifts.First(l=>l.id.StartsWith("STERN_CARGO"))};
        foreach(var lift in representatives)
        {
            lift.ResetToFloor(1);lift.RequestFloor(0);Assert.That(lift.targetFloor,Is.EqualTo(1),lift.id+" accepts deleted floor");
            lift.RequestFloor(1);var gate=lift.landings[1];float deadline=Time.time+6;
            while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(gate.IsOpen,Is.True,lift.id);
            Place(gate.transform.position+new Vector3(-1,.05f,1.5f));
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime){explorer.player.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That(explorer.player.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),lift.id);
            float y=explorer.player.transform.position.y;lift.RequestFloor(2);deadline=Time.time+25;
            while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(lift.currentFloor,Is.EqualTo(2),lift.id);
            Assert.That(explorer.player.transform.position.y-y,Is.EqualTo(3.4f).Within(.25f),lift.id);
            var center=new Vector3((lift.footprint.x+lift.footprint.y)*.5f,.1f,(lift.footprint.z+lift.footprint.w)*.5f);
            Assert.That(Physics.Raycast(center,Vector3.down,out var hit,1),Is.True,lift.id+" shaft bottom");
            Assert.That(hit.collider.GetComponentInParent<ShipInstanceV5>().category,Is.EqualTo("ShaftBases"),lift.id);
            var cargo=lift.GetComponent<CargoLiftController>();if(cargo!=null)Assert.That(cargo.RequestFloor(0),Is.False,lift.id);
        }
    }
    [UnityTest] public IEnumerator PreviousVersionStillSupportsDeckZero()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v76",LoadSceneMode.Single);yield return null;
        var old=Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(old,Is.Not.Null);old.SetWalking(false);old.SetDeck(0);
        Assert.That(old.selectedDeck,Is.Zero,"previous scene lost deck 0 view");
        foreach(var lift in new[]{old.lifts.First(l=>!l.id.StartsWith("STERN_CARGO")),old.lifts.First(l=>l.id.StartsWith("STERN_CARGO"))})
        {
            Assert.That(lift.landings[0],Is.Not.Null,lift.id);lift.ResetToFloor(1);lift.RequestFloor(0);var deadline=Time.time+25;
            while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(lift.currentFloor,Is.Zero,lift.id+" old floor 0");
        }
    }
}
