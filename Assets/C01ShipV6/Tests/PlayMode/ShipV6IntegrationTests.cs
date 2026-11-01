using System.Collections;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V6.Cargo;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV6IntegrationTests
{
    ShipExplorerV5 explorer;

    [UnitySetUp]
    public IEnumerator Load()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v6", LoadSceneMode.Single);
        yield return null;
        explorer = Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer, Is.Not.Null);
        explorer.SetWalking(true);
        explorer.enabled = false;
    }

    [UnityTest]
    public IEnumerator AllGatesHaveReachablePanels()
    {
        Assert.That(explorer.gates.Length, Is.GreaterThan(100));
        foreach (var button in explorer.buttons.Where(b => b.gate != null))
        {
            var surface = button.GetComponentsInChildren<Collider>().OrderByDescending(c =>
                Vector3.Dot(c.bounds.center - button.transform.position, button.transform.forward)).First();
            var point = surface.bounds.center;
            Assert.That(Physics.Raycast(point + button.transform.forward*.65f, -button.transform.forward,
                out var hit, 1f) && hit.collider.GetComponentInParent<ShipButtonV5>() == button,
                Is.True, button.name + " blocked from the approach side");
        }
        yield return null;
    }

    [UnityTest]
    public IEnumerator BothCargoLiftsCarryRealPlayerAndCrateAcrossThreeDecks()
    {
        var cargos = Object.FindObjectsByType<CargoLiftController>(FindObjectsSortMode.None);
        Assert.That(cargos.Length, Is.EqualTo(2));
        foreach (var cargo in cargos)
        {
            var lift = cargo.Lift;
            Assert.That(lift, Is.Not.Null);
            var surfaces = lift.car.GetComponentsInChildren<ShipInstanceV5>()
                .Where(p => p.modelId == "P_CargoLiftTile")
                .Select(p => p.GetComponentInChildren<Collider>()).ToArray();
            Assert.That(surfaces.Length, Is.EqualTo(4));
            lift.ResetToFloor(0);
            var cc = explorer.player;
            cc.enabled = false;
            var playerTile = surfaces[3].bounds;
            cc.transform.position = new Vector3(playerTile.center.x, lift.elevations[0]+.03f, playerTile.center.z);
            cc.enabled = true;
            var crate = GameObject.CreatePrimitive(PrimitiveType.Cube);
            crate.name = "TestCargo";
            crate.transform.localScale = Vector3.one*.5f;
            var cargoTile=surfaces[0].bounds;
            crate.transform.position=new Vector3(cargoTile.center.x, lift.elevations[0]+.25f, cargoTile.center.z);
            var body=crate.AddComponent<Rigidbody>();
            yield return new WaitForFixedUpdate();
            for (int floor=1;floor<=2;floor++)
            {
                float startY=lift.car.position.y, startPlayer=cc.transform.position.y, startCargo=body.position.y;
                cargo.RequestFloor(floor);
                float deadline=Time.time+25;
                while ((lift.IsMoving || lift.currentFloor!=floor) && Time.time<deadline) yield return new WaitForFixedUpdate();
                Assert.That(lift.currentFloor, Is.EqualTo(floor), cargo.name+" did not reach deck");
                float delta=lift.car.position.y-startY;
                Assert.That(cc.transform.position.y-startPlayer, Is.EqualTo(delta).Within(.2f), "Player did not ride lift");
                Assert.That(body.position.y-startCargo, Is.EqualTo(delta).Within(.25f), "Cargo did not ride lift");
            }
            Object.Destroy(crate);
            yield return null;
        }
    }

    [UnityTest]
    public IEnumerator BothPassengerLiftsCarryRealPlayerAcrossThreeDecks()
    {
        var lifts=explorer.lifts.Where(l => !l.id.StartsWith("STERN_CARGO")).ToArray();
        Assert.That(lifts.Length, Is.EqualTo(2));
        foreach (var lift in lifts)
        {
            lift.ResetToFloor(0);
            var cc=explorer.player;
            cc.enabled=false;
            cc.transform.position=lift.car.position+Vector3.up*.03f;
            cc.enabled=true;
            yield return new WaitForFixedUpdate();
            for (int floor=1;floor<=2;floor++)
            {
                float start=cc.transform.position.y, carStart=lift.car.position.y;
                lift.RequestFloor(floor);
                float deadline=Time.time+25;
                while ((lift.IsMoving || lift.currentFloor!=floor) && Time.time<deadline) yield return new WaitForFixedUpdate();
                Assert.That(lift.currentFloor, Is.EqualTo(floor), lift.id);
                Assert.That(cc.transform.position.y-start, Is.EqualTo(lift.car.position.y-carStart).Within(.2f), lift.id);
            }
        }
    }

    [UnityTest]
    public IEnumerator RealCabinButtonOpensGateFromReticle()
    {
        var button=explorer.buttons.First(b=>b.gate!=null && b.airlock==null && b.lift==null &&
                                             b.gate.id.Contains("CABIN"));
        button.gate.SetImmediate(0);
        var target=button.GetComponentsInChildren<Collider>().First().bounds.center;
        var forward=button.transform.forward;
        var cc=explorer.player;
        cc.enabled=false;
        cc.transform.position=new Vector3(target.x+forward.x,button.transform.position.y-1.05f,target.z+forward.z);
        cc.transform.rotation=Quaternion.LookRotation(-forward,Vector3.up);
        cc.enabled=true;
        explorer.view.transform.rotation=Quaternion.LookRotation(target-explorer.view.transform.position,Vector3.up);
        Physics.SyncTransforms();
        Assert.That(explorer.TryPressScreen(new Vector2(5,Screen.height-5)),Is.True);
        float deadline=Time.time+5;
        while (!button.gate.IsOpen && Time.time<deadline) yield return null;
        Assert.That(button.gate.IsOpen,Is.True);
    }

    [UnityTest]
    public IEnumerator TrainingSectorStairsVentAndLadderCarryPlayer()
    {
        var cc=explorer.player;
        void Place(Vector3 p) { cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms(); }
        Place(new Vector3(2.5f,.04f,59.6f));
        for(float t=0;t<8;t+=Time.fixedDeltaTime)
        { cc.Move(Vector3.right*(13.1f/8)*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate(); }
        Assert.That(cc.transform.position.y,Is.GreaterThan(5.8f),"Stairs are not walkable");
        Place(new Vector3(15.5f,6.04f,61.15f));
        for(float t=0;t<2;t+=Time.fixedDeltaTime)
        { cc.Move(Vector3.left*1.5f*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate(); }
        Assert.That(cc.transform.position.x,Is.LessThan(13.2f),"Ventilation entrance is blocked");
        Place(new Vector3(17.4f,.04f,62.55f));
        Assert.That(explorer.TryBeginClimb(),Is.True);
        for(int i=0;i<260&&explorer.IsClimbing;i++){explorer.MoveClimb(1,.02f);yield return new WaitForFixedUpdate();}
        Assert.That(explorer.IsClimbing,Is.False);
        Assert.That(cc.transform.position.y,Is.GreaterThan(5.95f));
        Assert.That(explorer.TryBeginClimb(),Is.True);
        for(int i=0;i<260&&explorer.IsClimbing;i++){explorer.MoveClimb(-1,.02f);yield return new WaitForFixedUpdate();}
        Assert.That(explorer.IsClimbing,Is.False);
        Assert.That(cc.transform.position.y,Is.LessThan(.2f));
    }

    [UnityTest]
    public IEnumerator OverviewFramesEntireShip()
    {
        explorer.SetWalking(false);
        explorer.SetDeck(-1);
        explorer.ResetView();
        var all=explorer.master.GetComponentsInChildren<Renderer>(true);
        Assert.That(all.Length,Is.GreaterThan(0));
        var bounds=all[0].bounds;
        foreach(var renderer in all) bounds.Encapsulate(renderer.bounds);
        for(int x=0;x<2;x++) for(int y=0;y<2;y++) for(int z=0;z<2;z++)
        {
            var p=new Vector3(x==0?bounds.min.x:bounds.max.x,
                              y==0?bounds.min.y:bounds.max.y,
                              z==0?bounds.min.z:bounds.max.z);
            var v=explorer.view.WorldToViewportPoint(p);
            Assert.That(v.x,Is.InRange(.005f,.995f),"Ship clipped horizontally");
            Assert.That(v.y,Is.InRange(.005f,.995f),"Ship clipped vertically");
            Assert.That(v.z,Is.GreaterThan(0));
        }
        yield return null;
    }

    [UnityTest]
    public IEnumerator CanEnterEachLiftFromEveryLanding()
    {
        var cc=explorer.player;
        foreach(var lift in explorer.lifts)
        {
            for(int floor=0;floor<3;floor++)
            {
                lift.ResetToFloor(floor);
                lift.RequestFloor(floor);
                var gate=lift.landings[floor];
                float deadline=Time.time+6;
                while(!gate.IsOpen && Time.time<deadline) yield return new WaitForFixedUpdate();
                Assert.That(gate.IsOpen,Is.True,lift.id+" gate did not open");
                cc.enabled=false;
                cc.transform.position=gate.transform.position+new Vector3(-1,.05f,1.5f);
                cc.enabled=true;
                Physics.SyncTransforms();
                float startY=cc.transform.position.y;
                for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
                {
                    cc.Move(Vector3.right*(2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);
                    yield return new WaitForFixedUpdate();
                }
                Assert.That(cc.transform.position.x,Is.GreaterThan(gate.transform.position.x+.65f),
                    lift.id+" entrance blocked at deck "+floor+" pos="+cc.transform.position);
                Assert.That(cc.transform.position.y,Is.EqualTo(startY).Within(.3f),
                    lift.id+" floor discontinuity at deck "+floor);
            }
        }
    }
}
