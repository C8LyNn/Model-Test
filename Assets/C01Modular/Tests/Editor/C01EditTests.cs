using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace C01.Tests {
    public class C01EditTests {
        [Test] public void ImportedPackageKeepsQaInsideTargetProject(){
            string project=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"C01_Isolated_Import_Project");
            Assert.AreEqual(System.IO.Path.Combine(project,"C01_QA"),C01.Editor.C01Builder.ResolveQaPath(project));
        }
        [Test] public void CompleteScenePassesGeometryPhysicsAndImportAudit() {
            EditorSceneManager.OpenScene(C01.Editor.C01Builder.ScenePath);
            Assert.DoesNotThrow(()=>C01.Editor.C01Validation.Run());
        }
        [Test] public void MissingNestedFrameIsRejected() {
            EditorSceneManager.OpenScene(C01.Editor.C01Builder.ScenePath);
            var door=Object.FindFirstObjectByType<C01Door>();Object.DestroyImmediate(door.transform.Find("Frame").gameObject);
            Assert.Throws<System.Exception>(()=>C01.Editor.C01Validation.Run("unity_negative_missing_frame.json"));
            EditorSceneManager.OpenScene(C01.Editor.C01Builder.ScenePath);
        }
        [TestCase("W01_Wall_3m")][TestCase("W02_Wall_3m_Variant")][TestCase("W05_Wall_3m_Service")][TestCase("W04_DoorWall_3m")]
        public void WallVariantsHaveUnchangedGraphSocketTransforms(string id) {
            var go=PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01Modular/Prefabs/"+id+".prefab")) as GameObject;
            try {
                var expectedEnds=new[]{new Vector3(6,0,6),new Vector3(3,0,3),new Vector3(0,0,6),new Vector3(3,0,9)};
                var expectedHinges=new[]{new Vector3(3.66f,.02f,6),new Vector3(3,.02f,5.34f),new Vector3(2.34f,.02f,6),new Vector3(3,.02f,6.66f)};
                int quadrant=0;
                foreach(float yaw in new[]{0,90,180,270}){
                    go.transform.SetPositionAndRotation(new Vector3(3,0,6),Quaternion.Euler(0,yaw,0));
                    var start=go.transform.Find("Socket_Start");var end=go.transform.Find("Socket_End");Assert.AreEqual(Vector3.zero,start.localPosition);Assert.AreEqual(new Vector3(3,0,0),end.localPosition);Assert.AreEqual(3,Vector3.Distance(start.position,end.position),.0001);
                    Assert.That(Vector3.Distance(end.position,expectedEnds[quadrant]),Is.LessThan(.0001));
                    if(id=="W04_DoorWall_3m"){var d=go.GetComponent<C01Door>();Assert.AreEqual(new Vector3(.66f,.02f,0),d.hinge.localPosition);Assert.That(Vector3.Distance(d.hinge.position,expectedHinges[quadrant]),Is.LessThan(.0001));Assert.That(Vector3.Distance(go.transform.Find("Frame").position,new Vector3(3,0,6)),Is.LessThan(.0001));}
                    quadrant++;
                }
            } finally {Object.DestroyImmediate(go);}
        }
    }
}
