using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipSystemsV76RegressionTests
{
    ShipExplorerV5 explorer;
    [UnitySetUp] public IEnumerator Setup()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v76",LoadSceneMode.Single);
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
    [UnityTest] public IEnumerator CommandAndAftWorkAreasAreReachable()
    {
        Place(new Vector3(-4.5f,.04f,43.5f));MoveTo(-20,43.5f);MoveTo(-20,41.5f);MoveTo(-27,41.5f);
        Assert.That(explorer.player.transform.position.x,Is.LessThan(-26.8f),"helm access blocked");
        Place(new Vector3(127.5f,.04f,43.5f));MoveTo(135,43.5f);MoveTo(135,39);MoveTo(136.5f,39);
        Assert.That(explorer.player.transform.position.x,Is.GreaterThan(136.3f),"aft operations access blocked");
        yield return null;
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
