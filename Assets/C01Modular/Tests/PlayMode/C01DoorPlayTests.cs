using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace C01.Tests {
    public class C01DoorPlayTests {
        [UnityTest] public IEnumerator EachDoorOpensIndependentlyAndReturnsToItsSocket() {
            yield return SceneManager.LoadSceneAsync("C01_PASS02_ThreeRooms");yield return null;
            var doors=Object.FindObjectsByType<C01Door>(FindObjectsSortMode.None).OrderBy(x=>x.name).ToArray();Assert.AreEqual(3,doors.Length);
            foreach(var d in doors)d.SetAngleImmediate(0);
            for(int i=0;i<doors.Length;i++){
                doors[i].SetOpen(true);yield return new WaitForSeconds(1.15f);yield return new WaitForFixedUpdate();
                Assert.That(doors[i].Angle,Is.EqualTo(90).Within(.001));
                Assert.That(Quaternion.Angle(doors[i].hinge.localRotation,Quaternion.Euler(0,90,0)),Is.LessThan(.001));
                for(int j=0;j<doors.Length;j++)if(j!=i)Assert.That(doors[j].Angle,Is.EqualTo(0).Within(.001),"Other door moved");
                Assert.IsTrue(doors[i].hinge.GetComponent<Rigidbody>().isKinematic);
                var bottom=doors[i].transform.TransformPoint(new Vector3(1.5f,.3f,0));var top=doors[i].transform.TransformPoint(new Vector3(1.5f,1.5f,0));
                Assert.IsEmpty(Physics.OverlapCapsule(bottom,top,.299f),"Open doorway blocks human capsule");
                doors[i].Toggle();yield return new WaitForSeconds(1.15f);yield return new WaitForFixedUpdate();
                Assert.That(doors[i].Angle,Is.EqualTo(0).Within(.001));Assert.AreEqual(new Vector3(.66f,.02f,0),doors[i].hinge.localPosition);
                Assert.IsNotEmpty(Physics.OverlapCapsule(bottom,top,.299f),"Closed door collider missing");
            }
        }
    }
}
