using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV65DimensionsTests
{
    [UnityTest] public IEnumerator CorridorWidthsRoomHeightsAndLiftStopsMatchNewGrid()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        Assert.That(explorer,Is.Not.Null);
        explorer.enabled=false;
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        foreach(var z in zones.Where(x=>x.kind!="void" && x.kind!="exterior"))
            Assert.That(z.height,Is.EqualTo(z.deck==0 || z.kind=="sector" ? 6f:3f).Within(.001f),z.zoneId);
        foreach(var lift in explorer.lifts)
            CollectionAssert.AreEqual(new[]{-6.4f,0f,3.4f},lift.elevations,lift.id);
        Assert.That(explorer.climbHeight,Is.EqualTo(3f));
        Physics.SyncTransforms();
        foreach(float y in new[]{-6.4f,0f,3.4f})
        {
            var point=new Vector3(4.5f,y+1.5f,43.5f);
            Assert.That(Physics.Raycast(point,Vector3.forward,out var forward,2),Is.True,"main +z y="+y);
            Assert.That(Physics.Raycast(point,Vector3.back,out var back,2),Is.True,"main -z y="+y);
            Assert.That(forward.distance+back.distance,Is.EqualTo(2.7f).Within(.04f),"clear corridor y="+y);
            Assert.That(Physics.Raycast(point,Vector3.up,out var roof,6),Is.True,"ceiling y="+y);
            float height=y<0 ? 6f : 3f;
            Assert.That(roof.point.y-y,Is.EqualTo(height).Within(.04f),"ceiling y="+y);
        }
        foreach(float y in new[]{0f,3.4f})
        {
            var point=new Vector3(10.5f,y+1.5f,52.5f);
            Assert.That(Physics.Raycast(point,Vector3.right,out var right,2),Is.True,"branch +x y="+y);
            Assert.That(Physics.Raycast(point,Vector3.left,out var left,2),Is.True,"branch -x y="+y);
            Assert.That(right.distance+left.distance,Is.EqualTo(2.7f).Within(.04f),"branch y="+y);
        }
    }

    [UnityTest] public IEnumerator SectorStairsVentAndLadderReachThreeMetreLanding()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        explorer.SetWalking(true); explorer.enabled=false;
        var cc=explorer.player;
        void Place(Vector3 p) { cc.enabled=false;cc.transform.position=p;cc.enabled=true;Physics.SyncTransforms(); }
        Place(new Vector3(2.5f,.04f,59.6f));
        for(float t=0;t<5;t+=Time.fixedDeltaTime)
        {cc.Move(Vector3.right*(7.6f/5)*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate();}
        Assert.That(cc.transform.position.y,Is.GreaterThan(2.8f),"stairs do not reach landing: "+cc.transform.position);
        Place(new Vector3(10.5f,3.04f,61.15f));
        for(float t=0;t<2;t+=Time.fixedDeltaTime)
        {cc.Move(Vector3.right*1.5f*Time.fixedDeltaTime+Vector3.down*.04f);yield return new WaitForFixedUpdate();}
        Assert.That(cc.transform.position.x,Is.GreaterThan(12.8f),"vent entrance blocked: "+cc.transform.position);
        Place(new Vector3(11.4f,.04f,62.55f));
        Assert.That(explorer.TryBeginClimb(),Is.True,"ladder cannot be started");
        for(int i=0;i<220&&explorer.IsClimbing;i++){explorer.MoveClimb(1,.02f);yield return new WaitForFixedUpdate();}
        Assert.That(explorer.IsClimbing,Is.False,"ladder failed to exit");
        Assert.That(cc.transform.position.y,Is.GreaterThan(2.95f),"ladder did not reach landing");
    }

    [UnityTest] public IEnumerator CrewHasNamedAndEquippedLifeSupportSpaces()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        var zones=explorer.master.GetComponentsInChildren<ShipZoneV5>(true);
        foreach(var name in new[]{"KUCHNIA","JADALNIA","SALON ZALOGI","PRALNIA","ZAPASY MEDYCZNE","WARSZTAT","NADZOR WODY I POWIETRZA"})
            Assert.That(zones.Any(z=>z.label==name),Is.True,"missing crew service "+name);
        var placements=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);
        foreach(var id in new[]{"P_GalleyCounter","P_MessTable","P_LaundryUnit","P_ServiceRack","P_LifeSupportPanel"})
            Assert.That(placements.Any(p=>p.modelId==id),Is.True,"missing equipment "+id);
        Assert.That(explorer.lifts.Length,Is.EqualTo(6));
    }

    [UnityTest] public IEnumerator CrewServiceRoomsCanBeEnteredFromTheirBranches()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();explorer.SetWalking(true);explorer.enabled=false;
        var data=JsonUtility.FromJson<ShipDataV5>(System.IO.File.ReadAllText("Assets/C01ShipV65/Data/ship_v65.json"));
        foreach(var label in new[]{"KUCHNIA","JADALNIA","SALON ZALOGI","PRALNIA","NADZOR WODY I POWIETRZA"})
        {
            var zone=data.zones.First(z=>z.label==label);
            var opening=data.gates.First(g=>g.zones.Contains(zone.id)&&g.zones.Any(id=>id.Contains("BRANCH")));
            var gate=explorer.gates.First(g=>g.id==opening.id);gate.SetImmediate(1);
            float direction=(zone.bounds[0]+zone.bounds[1])*.5f>opening.x ? 1 : -1;
            var cc=explorer.player;cc.enabled=false;
            cc.transform.position=new Vector3(opening.x-direction,opening.y+.05f,opening.z+1.5f);
            cc.enabled=true;Physics.SyncTransforms();
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
            {cc.Move(Vector3.right*(direction*2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That((cc.transform.position.x-opening.x)*direction,Is.GreaterThan(.6f),label+" entrance obstructed");
        }
    }

    [UnityTest] public IEnumerator MirroredCabinBathroomsAreAccessible()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();explorer.SetWalking(true);explorer.enabled=false;
        var data=JsonUtility.FromJson<ShipDataV5>(System.IO.File.ReadAllText("Assets/C01ShipV65/Data/ship_v65.json"));
        foreach(var id in new[]{"L1_N_CABIN_01_BATH","L1_S_CABIN_01_BATH","L2_N_CABIN_01_BATH","L2_S_CABIN_01_BATH"})
        {
            var room=data.zones.First(z=>z.id==id);
            var opening=data.gates.First(g=>g.zones.Contains(id));
            var gate=explorer.gates.First(g=>g.id==opening.id);gate.SetImmediate(1);
            float direction=(room.bounds[2]+room.bounds[3])*.5f>opening.z ? 1 : -1;
            var cc=explorer.player;cc.enabled=false;
            cc.transform.position=new Vector3(opening.x+1.5f,opening.y+.05f,opening.z-direction);
            cc.enabled=true;Physics.SyncTransforms();
            for(float t=0;t<2.5f;t+=Time.fixedDeltaTime)
            {cc.Move(Vector3.forward*(direction*2.2f/2.5f)*Time.fixedDeltaTime+Vector3.down*.025f);yield return new WaitForFixedUpdate();}
            Assert.That((cc.transform.position.z-opening.z)*direction,Is.GreaterThan(.6f),id+" entrance obstructed");
        }
    }

    [UnityTest] public IEnumerator FreightAirlockInterlocksBothGates()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v65", LoadSceneMode.Single);
        yield return null;
        var explorer=Object.FindFirstObjectByType<ShipExplorerV5>();
        var inner=explorer.gates.First(g=>g.id=="L0_FREIGHT_INNER");
        var outer=explorer.gates.First(g=>g.id=="L0_FREIGHT_OUTER");
        Assert.That(inner.interlockAirlock,Is.Not.Null);
        Assert.That(inner.interlockAirlock,Is.SameAs(outer.interlockAirlock));
        inner.SetOpen(true);float deadline=Time.time+8;
        while(!inner.IsOpen && Time.time<deadline) yield return new WaitForFixedUpdate();
        Assert.That(inner.IsOpen,Is.True,"freight inner gate");
        Assert.That(outer.IsClosed,Is.True,"freight outer gate");
        outer.SetOpen(true);deadline=Time.time+8;
        while(!outer.IsOpen && Time.time<deadline)
        {
            Assert.That(inner.IsClosed || outer.openness<=.001f,Is.True,"both airlock gates open together");
            yield return new WaitForFixedUpdate();
        }
        Assert.That(inner.IsClosed,Is.True,"freight inner gate failed to close");
        Assert.That(outer.IsOpen,Is.True,"freight outer gate failed to open");
    }
}
