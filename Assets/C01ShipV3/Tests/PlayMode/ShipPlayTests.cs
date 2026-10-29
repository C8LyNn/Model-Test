using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
namespace C01.Ship.Tests {
    public class ShipPlayTests {
        [UnityTest] public IEnumerator NeighbourDoorsDoNotCollideAtIndependentAngles(){
            yield return SceneManager.LoadSceneAsync("C01_Ship_FromPlan");yield return null;
            var doors=Object.FindObjectsByType<C01Door>(FindObjectsSortMode.None);foreach(var d in doors)d.SetAngleImmediate(0);
            int pairs=0;int[] angles={0,25,30,45,60,65,85,90};
            for(int i=0;i<doors.Length;i++)for(int j=i+1;j<doors.Length;j++){
                var a=doors[i];var b=doors[j];if(Vector3.Distance(a.hinge.position,b.hinge.position)>3.38f)continue;pairs++;
                var ac=a.hinge.GetComponentsInChildren<Collider>();var bc=b.hinge.GetComponentsInChildren<Collider>();
                foreach(int aa in angles)foreach(int ba in angles){
                    a.SetAngleImmediate(aa);b.SetAngleImmediate(ba);Physics.SyncTransforms();
                    foreach(var x in ac)foreach(var y in bc){if(!x.bounds.Intersects(y.bounds))continue;bool hit=Physics.ComputePenetration(x,x.transform.position,x.transform.rotation,y,y.transform.position,y.transform.rotation,out var direction,out float depth);Assert.IsFalse(hit&&depth>.0005f,a.name+" @"+aa+" / "+b.name+" @"+ba+" depth="+depth);}
                }
                a.SetAngleImmediate(0);b.SetAngleImmediate(0);yield return null;
            }
            Assert.Greater(pairs,0);
        }
        [UnityTest] public IEnumerator FourAirlocksCloseOppositeDoorBeforeOpening(){
            yield return SceneManager.LoadSceneAsync("C01_Ship_FromPlan");yield return null;
            var locks=Object.FindObjectsByType<ShipAirlock>(FindObjectsSortMode.None);Assert.AreEqual(4,locks.Length);
            foreach(var airlock in locks){
                airlock.Request(airlock.doorA,true);yield return new WaitForSeconds(1.15f);Assert.AreEqual(90,airlock.doorA.Angle,.01);Assert.AreEqual(0,airlock.doorB.Angle,.01);
                airlock.Request(airlock.doorB,true);float end=Time.time+3;
                while(Time.time<end&&airlock.doorB.Angle<89.99f){Assert.IsFalse(airlock.doorA.Angle>.1f&&airlock.doorB.Angle>.1f,"Airlock opened both sides");yield return null;}
                Assert.AreEqual(0,airlock.doorA.Angle,.01);Assert.AreEqual(90,airlock.doorB.Angle,.01);airlock.Request(airlock.doorB,false);yield return new WaitForSeconds(1.15f);
            }
        }
        [UnityTest] public IEnumerator PlayerTraversesOpenMainCorridorCabinAndSternExit(){
            yield return SceneManager.LoadSceneAsync("C01_Ship_FromPlan");yield return null;
            var explorer=Object.FindFirstObjectByType<ShipExplorer>();float overviewSize=explorer.view.orthographicSize;explorer.SetWalking(true);
            foreach(var door in explorer.doors)door.SetAngleImmediate(90);Physics.SyncTransforms();yield return new WaitForFixedUpdate();
            var player=explorer.player;
            for(int i=0;i<300&&player.transform.position.x<46.3f;i++){player.Move(new Vector3(.18f,-.05f,0));yield return new WaitForFixedUpdate();}
            Assert.Greater(player.transform.position.x,46.2f,"Blocked main corridor / D1 / D2 / stern entry");Assert.That(player.transform.position.y,Is.InRange(-.02f,.15f));
            var zones=Object.FindObjectsByType<ShipZone>(FindObjectsSortMode.None).ToDictionary(z=>z.zoneId);
            player.enabled=false;player.transform.position=new Vector3(8.2f,.02f,zones["XN1"].transform.position.z);player.enabled=true;
            for(int i=0;i<25;i++){player.Move(new Vector3(-.2f,-.03f,0));yield return new WaitForFixedUpdate();}
            Assert.Less(player.transform.position.x,3.5f,"Cabin entry blocked");
            player.enabled=false;player.transform.position=new Vector3(46.5f,.02f,zones["D3"].transform.position.z-3);player.enabled=true;
            for(int i=0;i<31;i++){player.Move(new Vector3(0,-.03f,.2f));yield return new WaitForFixedUpdate();}
            Assert.Greater(player.transform.position.z,zones["EXIT_N"].transform.position.z-.2f,"Stern exit airlock blocked");Assert.That(player.transform.position.y,Is.InRange(-.02f,.15f));
            explorer.SetWalking(false);Assert.IsTrue(explorer.view.orthographic);Assert.AreEqual(overviewSize,explorer.view.orthographicSize,.001f,"Expanded overview framing changed after walking");
        }
        [UnityTest] public IEnumerator PlayerTraversesAllSixExtendedSideCorridors(){
            yield return SceneManager.LoadSceneAsync("C01_Ship_FromPlan");yield return null;
            var explorer=Object.FindFirstObjectByType<ShipExplorer>();explorer.SetWalking(true);foreach(var door in explorer.doors)door.SetAngleImmediate(90);Physics.SyncTransforms();
            var zones=Object.FindObjectsByType<ShipZone>(FindObjectsSortMode.None).ToDictionary(z=>z.zoneId);var player=explorer.player;
            float mainZ=zones["MAIN_W"].transform.position.z;
            foreach(string side in new[]{"N","S"})for(int index=1;index<=3;index++){
                string id="X"+side+index;var branch=zones[id];float direction=side=="N"?1:-1;float target=branch.transform.position.z+direction*6;
                player.enabled=false;player.transform.position=new Vector3(branch.transform.position.x,.02f,mainZ);player.enabled=true;Physics.SyncTransforms();yield return new WaitForFixedUpdate();
                for(int step=0;step<90&&direction*(target-player.transform.position.z)>.15f;step++){player.Move(new Vector3(0,-.04f,direction*.18f));yield return new WaitForFixedUpdate();}
                Assert.Less(Mathf.Abs(target-player.transform.position.z),.35f,"Blocked extended side corridor "+id);Assert.That(player.transform.position.y,Is.InRange(-.02f,.15f),id);
            }
        }
    }
}
