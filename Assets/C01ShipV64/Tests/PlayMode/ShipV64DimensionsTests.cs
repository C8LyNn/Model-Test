using System.Collections;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class ShipV64DimensionsTests
{
    [UnityTest] public IEnumerator CorridorWidthsRoomHeightsAndLiftStopsMatchNewGrid()
    {
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v64", LoadSceneMode.Single);
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
        yield return SceneManager.LoadSceneAsync("C01_Ship_Multideck_v64", LoadSceneMode.Single);
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
}
