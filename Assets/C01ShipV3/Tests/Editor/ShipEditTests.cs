using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace C01.Ship.Tests {
    public class ShipEditTests {
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
