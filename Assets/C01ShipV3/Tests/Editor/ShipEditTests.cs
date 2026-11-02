using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using System.Linq;
namespace C01.Ship.Tests {
    public class ShipEditTests {
        [Test] public void ExpandedBranchesKeepTheSameThreeMetreWidth(){
            var data=Editor.ShipBuilder.Read();CollectionAssert.AreEqual(new float[]{0,45,0,33},data.body);
            Assert.AreEqual(3,data.corridor_width);Assert.AreEqual(9,data.branch_length);
            foreach(var zone in data.zones.Where(z=>z.id.StartsWith("XN")||z.id.StartsWith("XS"))){Assert.AreEqual(3,zone.bounds[1]-zone.bounds[0]);Assert.AreEqual(9,zone.bounds[3]-zone.bounds[2]);}
            foreach(var zone in data.zones.Where(z=>z.id.StartsWith("MAIN")||z.id=="D1"||z.id=="D2"))Assert.AreEqual(3,zone.bounds[3]-zone.bounds[2]);
            EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);
            foreach(var instance in Editor.ShipValidation.Master().GetComponentsInChildren<ShipInstance>(true))Assert.That(Vector3.Distance(instance.transform.lossyScale,Vector3.one),Is.LessThan(.0001f),instance.name);
        }
        [TestCase("Floors","F_6_24")][TestCase("Ceilings","C_6_24")]
        public void MissingExtendedBranchSurfaceIsRejected(string group,string id){
            EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);var part=Editor.ShipValidation.Master().transform.Find(group+"/"+id);Assert.IsNotNull(part);
            string file="unity_negative_branch_"+group.ToLowerInvariant()+".json";
            Object.DestroyImmediate(part.gameObject);Assert.Throws<System.Exception>(()=>Editor.ShipValidation.Run(file));
            var report=JsonUtility.FromJson<Editor.ShipValidation.Report>(System.IO.File.ReadAllText(System.IO.Path.Combine(Editor.ShipBuilder.QA,file)));
            Assert.AreEqual("FAIL",report.status);Assert.IsTrue(report.errors.Any(error=>error.Contains("Missing/duplicate placement "+id)),"Missing surface must produce a diagnostic report");EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);
        }
        [Test] public void PackageQaStaysInsideIndependentTargetProject(){string project=System.IO.Path.Combine(System.IO.Path.GetTempPath(),"Ship_Imported_Project");Assert.AreEqual(System.IO.Path.Combine(project,"C01Ship_QA"),Editor.ShipBuilder.ResolveQaPath(project));}
        [Test] public void ReferenceScenePassesFullGeometryAndRoutes(){EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);Assert.DoesNotThrow(()=>Editor.ShipValidation.Run());}
        [Test] public void MissingDoorFrameIsRejected(){
            EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);var d=GameObject.Find("CABIN_01").GetComponent<C01Door>();Object.DestroyImmediate(d.transform.Find("Frame").gameObject);
            Assert.Throws<System.Exception>(()=>Editor.ShipValidation.Run("unity_negative_frame.json"));EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);
        }
        [Test] public void MissingEngineIsRejected(){
            EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);Object.DestroyImmediate(GameObject.Find("ENGINE_05"));
            Assert.Throws<System.Exception>(()=>Editor.ShipValidation.Run("unity_negative_engine.json"));EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);
        }
        [Test] public void NegativeAuditDoesNotModifyDeliveredNavmesh(){
            EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);string path=Editor.ShipBuilder.Root+"/Data/Ship_OpenDoors_NavMesh.asset";var before=System.IO.File.ReadAllBytes(path);
            Object.DestroyImmediate(GameObject.Find("CABIN_01").transform.Find("Frame").gameObject);Assert.Throws<System.Exception>(()=>Editor.ShipValidation.Run("unity_negative_isolation.json"));
            CollectionAssert.AreEqual(before,System.IO.File.ReadAllBytes(path),"Negative QA altered a delivered navigation asset");EditorSceneManager.OpenScene(Editor.ShipBuilder.ScenePath);
        }
    }
}
