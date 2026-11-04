using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipSystemsV71RegressionTests
{
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v71",LoadSceneMode.Single);
        yield return null;
        explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);explorer.SetWalking(true);explorer.enabled=false;
    }
    void Place(Vector3 p) { var cc=explorer.player;cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms(); }
    void MoveTo(float x,float z)
    {
        var cc=explorer.player;var target=new Vector3(x,cc.transform.position.y,z);
        for(int i=0;i<5000;i++) { var delta=Vector3.ProjectOnPlane(target-cc.transform.position,Vector3.up);if(delta.magnitude<.08f)return;cc.Move(Vector3.ClampMagnitude(delta,.08f)+Vector3.down*.015f); }
        Assert.Fail("Passage blocked toward "+target+" at "+cc.transform.position);
    }
    [UnityTest] public IEnumerator SectorsHaveSixMetreClearanceAndCorrectCeilings()
    {
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        var sectors=zones.Where(z=>z.deck==1&&z.kind=="sector").ToArray();Assert.That(sectors.Length,Is.EqualTo(6));
        foreach(var zone in sectors)
        {
            Assert.That(zone.height,Is.EqualTo(6).Within(.001f),zone.zoneId);
            var center=zone.transform.position;bool found=false;
            for(float x=center.x-9;x<=center.x+9&&!found;x+=3)for(float z=center.z-6;z<=center.z+6&&!found;z+=3)
            {
                if(Physics.Raycast(new Vector3(x,zone.floor+.2f,z),Vector3.up,out var hit,7,Physics.DefaultRaycastLayers,QueryTriggerInteraction.Ignore)
                    && Mathf.Abs(hit.point.y-zone.floor-6)<.04f)found=true;
            }
            Assert.That(found,Is.True,zone.zoneId+" has no tested six-metre clear ceiling");
        }
        yield return null;
    }
    [UnityTest] public IEnumerator DeckZeroAdditionalGatesCanBeOperatedAndCrossed()
    {
        var names=new[]{"G_L0_MAIN_L0_N_ACCESS_0","G_L0_MAIN_L0_S_ACCESS_0","G_L0_MAIN_L0_N_ACCESS_1","G_L0_MAIN_L0_S_ACCESS_1","G_L0_MAIN_L0_N_ACCESS_2","G_L0_MAIN_L0_S_ACCESS_2","G_L0_N_ACCESS_0_L0_N_ACCESS_1","G_L0_N_ACCESS_1_L0_N_ACCESS_2","G_L0_S_ACCESS_0_L0_S_ACCESS_1","G_L0_S_ACCESS_1_L0_S_ACCESS_2"};
        foreach(var id in names)
        {
            var gate=explorer.gates.FirstOrDefault(g=>g!=null&&g.id==id);Assert.That(gate,Is.Not.Null,id);gate.SetImmediate(0);
            var button=explorer.buttons.First(b=>b!=null&&b.gate==gate);
            var target=button.GetComponentsInChildren<Collider>().OrderByDescending(c=>Vector3.Dot(c.bounds.center-button.transform.position,button.transform.forward)).First();
            var point=target.bounds.center;var facing=button.transform.forward;
            Place(new Vector3(point.x+facing.x*.9f,gate.transform.position.y+.05f,point.z+facing.z*.9f));
            explorer.player.transform.rotation=Quaternion.LookRotation(-facing,Vector3.up);
            explorer.view.transform.rotation=Quaternion.LookRotation(point-explorer.view.transform.position,Vector3.up);Physics.SyncTransforms();
            Assert.That(explorer.TryPressScreen(Vector2.zero),Is.True,id+" button from player view");
            float deadline=Time.time+6;while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(gate.IsOpen,Is.True,id);
            var center=gate.transform.position+gate.transform.right*1.5f;var across=gate.transform.forward;
            Place(center-across+Vector3.up*.05f);
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime){explorer.player.Move(across*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That(Vector3.Dot(explorer.player.transform.position-center,across),Is.GreaterThan(.65f),id+" passage blocked");
        }
    }
    [UnityTest] public IEnumerator ChaseRouteRemainsPassable()
    {
        Place(new Vector3(-34.5f,3.44f,55.5f));MoveTo(-13.5f,55.5f);MoveTo(-13.5f,43.5f);MoveTo(2,43.5f);int i=0;
        foreach(float x in new[]{9f,21f,33f,51f,63f,75f,93f,105f,117f})
        {MoveTo(x-1.3f,explorer.player.transform.position.z);MoveTo(x-1.3f,i%2==0?44.2f:42.8f);MoveTo(x+1.3f,i%2==0?44.2f:42.8f);i++;}
        MoveTo(127.5f,43.5f);MoveTo(136.5f,43.5f);MoveTo(136.5f,67.5f);MoveTo(133.5f,67.5f);MoveTo(133.5f,73.5f);
        Assert.That(explorer.player.transform.position.z,Is.GreaterThan(72.5f));yield return null;
    }
    [UnityTest] public IEnumerator BridgeAndSternStationsHaveNoColliderPenetrations()
    {
        var stations=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>p.category=="CoreStations").ToArray();
        foreach(var id in new[]{"BRIDGE_HELM_STATION","BRIDGE_NAV_STATION","STERN_PROPULSION_STATION","STERN_LOGISTICS_STATION"}) Assert.That(stations.Any(p=>p.placementId==id),Is.True,id);
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
    [UnityTest] public IEnumerator CommandAndAftWorkAreasAreReachable()
    {
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-20,43.5f);MoveTo(-20,41.5f);MoveTo(-27,41.5f);
        Assert.That(explorer.player.transform.position.x,Is.LessThan(-26.8f),"helm access blocked");
        Place(new Vector3(127.5f,.04f,43.5f));MoveTo(135,43.5f);MoveTo(135,39);MoveTo(136.5f,39);
        Assert.That(explorer.player.transform.position.x,Is.GreaterThan(136.3f),"aft operations access blocked");
        yield return null;
    }


    [UnityTest] public IEnumerator LegacyButtonLabelsStayHiddenAfterViewChanges()
    {
        var signage=explorer.master.GetComponent<ButtonSignage>();Assert.That(signage,Is.Not.Null);signage.Synchronize();
        var old=explorer.buttons.Where(b=>b!=null).Select(b=>b.transform.Find("Button_Label")).Where(t=>t!=null).Select(t=>t.GetComponent<Renderer>()).Where(r=>r!=null).ToArray();
        Assert.That(old.Length,Is.GreaterThan(20));explorer.SetWalking(false);Assert.That(old.Count(r=>r.enabled),Is.Zero);
        explorer.SetWalking(true);Assert.That(old.Count(r=>r.enabled),Is.Zero);yield return null;
    }
    [UnityTest] public IEnumerator PassengerAndCargoLiftCarryPlayer()
    {
        var representatives=new[]{explorer.lifts.First(l=>!l.id.StartsWith("STERN_CARGO")),explorer.lifts.First(l=>l.id.StartsWith("STERN_CARGO"))};
        foreach(var lift in representatives)
        {
            lift.ResetToFloor(1);lift.RequestFloor(1);var gate=lift.landings[1];float deadline=Time.time+6;
            while(!gate.IsOpen&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(gate.IsOpen,Is.True,lift.id);
            Place(gate.transform.position+new Vector3(-1,.05f,1.5f));
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime){explorer.player.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That(explorer.player.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),lift.id);
            float y=explorer.player.transform.position.y;lift.RequestFloor(2);deadline=Time.time+25;
            while(lift.IsMoving&&Time.time<deadline)yield return new WaitForFixedUpdate();Assert.That(lift.currentFloor,Is.EqualTo(2),lift.id);
            Assert.That(explorer.player.transform.position.y-y,Is.EqualTo(3.4f).Within(.25f),lift.id);
        }
    }
    [UnityTest] public IEnumerator SectorStairsVentAndLadderReachThreeMetreLanding()
    {
        var cc=explorer.player;Place(new Vector3(2.5f,.04f,59.6f));
        for(float t=0;t<5;t+=Time.fixedDeltaTime){cc.Move(Vector3.right*(7.6f/5)*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate();}
        Assert.That(cc.transform.position.y,Is.GreaterThan(2.8f),"stairs do not reach landing: "+cc.transform.position);
        Place(new Vector3(10.5f,3.04f,61.15f));
        for(float t=0;t<2;t+=Time.fixedDeltaTime){cc.Move(Vector3.right*1.5f*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate();}
        Assert.That(cc.transform.position.x,Is.GreaterThan(12.8f),"vent entrance blocked: "+cc.transform.position);
        Place(new Vector3(11.4f,.04f,62.55f));Assert.That(explorer.TryBeginClimb(),Is.True,"ladder cannot be started");
        for(int i=0;i<220&&explorer.IsClimbing;i++){explorer.MoveClimb(1,.02f);yield return new WaitForFixedUpdate();}
        Assert.That(explorer.IsClimbing,Is.False,"ladder failed to exit");Assert.That(cc.transform.position.y,Is.GreaterThan(2.95f),"ladder did not reach landing");
    }

}
