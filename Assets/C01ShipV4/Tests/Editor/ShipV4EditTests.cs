using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.AI;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace C01.Ship.V4.Tests {
    public class ShipV4EditTests {
        SceneSetup[] setup;
        [SetUp] public void Open(){setup=EditorSceneManager.GetSceneManagerSetup();Assert.That(File.Exists(Editor.ShipV4Builder.ScenePath),Is.True,"Generate the actual v4 scene first");EditorSceneManager.OpenScene(Editor.ShipV4Builder.ScenePath);Physics.SyncTransforms();}
        [TearDown] public void Restore(){EditorSceneManager.OpenScene(Editor.ShipV4Builder.ScenePath);if(setup!=null&&setup.Length>0&&setup.All(s=>!string.IsNullOrEmpty(s.path)))EditorSceneManager.RestoreSceneManagerSetup(setup);}
        [Test] public void ActualSavedSceneMatchesSourceAndGeometry(){Assert.That(Editor.ShipV4Validation.Run("editmode_source_reference.json",true).status,Is.EqualTo("PASS"));}
        [TestCase("Floors")] [TestCase("Ceilings")]
        public void MissingSurfaceIsRejectedWithFailReport(string category){var target=Editor.ShipV4Validation.Master().GetComponentsInChildren<ShipInstanceV4>().First(p=>p.category==category);UnityEngine.Object.DestroyImmediate(target.gameObject);Physics.SyncTransforms();Reject("negative_missing_"+category.ToLowerInvariant()+".json","Missing/duplicate placement");}
        [Test] public void MissingGateButtonIsRejected(){var root=Editor.ShipV4Validation.Master();var button=root.GetComponentsInChildren<ShipButtonV4>().First(b=>b.gate!=null);UnityEngine.Object.DestroyImmediate(button);Reject("negative_gate_button.json","Gate button");}
        [Test] public void MissingCabinBedIsRejectedAndSavedNavMeshIsUntouched(){
            string sentinelPath=AssetDatabase.GenerateUniqueAssetPath(Editor.ShipV4Builder.Root+"/Data/NegativeAudit_Sentinel_NavMesh.asset");
            NavMeshData sentinel=null;bool saved=false;
            try{
                var settings=NavMesh.GetSettingsByIndex(0);settings.agentHeight=1.8f;settings.agentRadius=.28f;
                var source=new NavMeshBuildSource{shape=NavMeshBuildSourceShape.Box,size=new Vector3(6,.4f,6),transform=Matrix4x4.TRS(new Vector3(1000,-.2f,1000),Quaternion.identity,Vector3.one),area=0};
                sentinel=NavMeshBuilder.BuildNavMeshData(settings,new List<NavMeshBuildSource>{source},new Bounds(new Vector3(1000,1,1000),new Vector3(10,5,10)),Vector3.zero,Quaternion.identity);
                Assert.That(sentinel,Is.Not.Null,"The saved sentinel must contain an actual built NavMesh");
                sentinel.name="NegativeAuditSavedSentinel";AssetDatabase.CreateAsset(sentinel,sentinelPath);saved=true;AssetDatabase.SaveAssetIfDirty(sentinel);
                string guid=AssetDatabase.AssetPathToGUID(sentinelPath);var before=NavAssets();
                Assert.That(before,Is.Not.Empty);Assert.That(before.ContainsKey(sentinelPath),Is.True);Assert.That(before[sentinelPath].Length,Is.GreaterThan(0));Assert.That(guid,Is.Not.Empty);
                var bed=Editor.ShipV4Validation.Master().GetComponentsInChildren<ShipInstanceV4>().First(p=>p.modelId=="P_Bed");UnityEngine.Object.DestroyImmediate(bed.gameObject);Physics.SyncTransforms();
                var report=Reject("negative_cabin_bed.json","Four cabin beds",true);
                Assert.That(report.routes.Count,Is.EqualTo(Editor.ShipV4Builder.Read().zones.Length),"The exhaustive failing audit must build its temporary NavMesh and execute every navigation route before failing");
                Assert.That(report.transportLinks,Is.EqualTo(4),"The audit must actually create its temporary lift transport links");
                var after=NavAssets();Assert.That(after.Keys,Is.EquivalentTo(before.Keys));foreach(var entry in before)Assert.That(after[entry.Key],Is.EqualTo(entry.Value),"Negative audit changed a saved navigation asset: "+entry.Key);
                Assert.That(AssetDatabase.AssetPathToGUID(sentinelPath),Is.EqualTo(guid));
            }finally{if(saved)AssetDatabase.DeleteAsset(sentinelPath);else if(sentinel!=null)UnityEngine.Object.DestroyImmediate(sentinel);}
        }
        [Test] public void ColliderMustMatchFullSourceDimensions(){var box=Editor.ShipV4Validation.Master().GetComponentInChildren<BoxCollider>();box.size*=.5f;Physics.SyncTransforms();Reject("negative_collider_geometry.json","Box geometry");}
        [Test] public void RotatedModuleSocketsPreserveWorldPositionAndNormal(){var model=Editor.ShipV4Builder.Read().models.First(m=>m.family=="wall"&&m.sockets.Length>=2);var asset=AssetDatabase.LoadAssetAtPath<GameObject>(Editor.ShipV4Builder.Root+"/Prefabs/Modules/"+model.id+".prefab");var go=(GameObject)PrefabUtility.InstantiatePrefab(asset);try{var origin=new Vector3(3,6.4f,9);var yaw=Quaternion.Euler(0,90,0);go.transform.SetPositionAndRotation(origin,yaw);foreach(var socket in model.sockets){var t=go.transform.Find(socket.name);Assert.That(t,Is.Not.Null);Assert.That(Vector3.Distance(t.position,origin+yaw*Editor.ShipV4Builder.V(socket.position)),Is.LessThan(.001f));Assert.That(Vector3.Angle(t.forward,yaw*Editor.ShipV4Builder.V(socket.normal)),Is.LessThan(.01f));Assert.That(t.GetComponents<Component>().Length,Is.EqualTo(1));}Assert.That(Vector3.Distance(go.transform.lossyScale,Vector3.one),Is.LessThan(.00001f));}finally{UnityEngine.Object.DestroyImmediate(go);}}
        [Test] public void RebuildPreservesHostSettingsAndStableAssetGuids(){var host=Editor.ShipV4Batch.HostSnapshot.Capture();var data=Editor.ShipV4Builder.Read();string path=Editor.ShipV4Builder.Root+"/Meshes/"+data.models[0].id+"__00.asset";string guid=AssetDatabase.AssetPathToGUID(path);Assert.That(guid,Is.Not.Empty);Editor.ShipV4Builder.Build();host.AssertRetained();Assert.That(AssetDatabase.AssetPathToGUID(path),Is.EqualTo(guid));Assert.That(EditorBuildSettings.scenes[0].path,Is.EqualTo(Editor.ShipV4Builder.ScenePath));Assert.That(Editor.ShipV4Validation.Master().GetComponentsInChildren<Collider>(true).All(c=>c.enabled),Is.True);}
        static Dictionary<string,byte[]> NavAssets()=>AssetDatabase.FindAssets("t:NavMeshData",new[]{Editor.ShipV4Builder.Root}).Select(AssetDatabase.GUIDToAssetPath).ToDictionary(p=>p,p=>File.ReadAllBytes(p));
        static Editor.ShipV4Validation.Report Reject(string file,string reason,bool exhaustive=false){var ex=Assert.Throws<InvalidOperationException>(()=>Editor.ShipV4Validation.Run(file,exhaustive));Assert.That(ex.Message,Does.Contain("audit FAIL"));string report=File.ReadAllText(Path.Combine(Editor.ShipV4Builder.QA,file));Assert.That(report,Does.Contain("\"status\": \"FAIL\""));Assert.That(report,Does.Contain(reason));return JsonUtility.FromJson<Editor.ShipV4Validation.Report>(report);}
    }
}
