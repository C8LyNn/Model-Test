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
            var explorer=Object.FindFirstObjectByType<ShipExplorer>();explorer.SetWalking(true);
            foreach(var door in explorer.doors)door.SetAngleImmediate(90);Physics.SyncTransforms();yield return new WaitForFixedUpdate();
            var player=explorer.player;
            for(int i=0;i<300&&player.transform.position.x<46.3f;i++){player.Move(new Vector3(.18f,-.05f,0));yield return new WaitForFixedUpdate();}
            Assert.Greater(player.transform.position.x,46.2f,"Blocked main corridor / D1 / D2 / stern entry");Assert.That(player.transform.position.y,Is.InRange(-.02f,.15f));
            player.enabled=false;player.transform.position=new Vector3(8.2f,.02f,13.5f);player.enabled=true;
            for(int i=0;i<25;i++){player.Move(new Vector3(-.2f,-.03f,0));yield return new WaitForFixedUpdate();}
            Assert.Less(player.transform.position.x,3.5f,"Cabin entry blocked");
            player.enabled=false;player.transform.position=new Vector3(46.5f,.02f,16.5f);player.enabled=true;
            for(int i=0;i<31;i++){player.Move(new Vector3(0,-.03f,.2f));yield return new WaitForFixedUpdate();}
            Assert.Greater(player.transform.position.z,22.3f,"Stern exit airlock blocked");Assert.That(player.transform.position.y,Is.InRange(-.02f,.15f));
        }
    }
}
