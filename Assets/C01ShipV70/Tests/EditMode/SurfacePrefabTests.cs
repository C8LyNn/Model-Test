using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public class SurfacePrefabTests
{
    [Serializable] class WallPlan { public string[] singleSeamWalls,topBandFascias; }
    [Serializable] class RoofPlan { public Roof[] roofs; }
    [Serializable] class Roof { public string id,variant; }
    [Test] public void RepairedWallsAndRoofsUseSharedModulePrefabs()
    {
        EditorSceneManager.OpenScene("Assets/C01ShipV70/Scenes/C01_Ship_Multideck_v70.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();Assert.That(explorer,Is.Not.Null);
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true).Where(p=>!string.IsNullOrEmpty(p.placementId)).ToDictionary(p=>p.placementId);
        var wall=JsonUtility.FromJson<WallPlan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV70/Data/wall_repair.json")));
        var roofs=JsonUtility.FromJson<RoofPlan>(File.ReadAllText(Path.Combine(Application.dataPath,"C01ShipV70/Data/roof_repair.json"))).roofs;
        var paths=new HashSet<string>();
        foreach(var id in wall.singleSeamWalls.Concat(wall.topBandFascias).Concat(roofs.Select(r=>r.id)))
        {
            var marker=all[id];var path=PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(marker.gameObject);
            Assert.That(path,Does.StartWith("Assets/C01ShipV70/Prefabs/Modules/"),id);
            Assert.That(AssetDatabase.LoadAssetAtPath<GameObject>(path),Is.Not.Null,id);
            paths.Add(path);
        }
        Assert.That(paths.Count,Is.EqualTo(11),"Two wall and nine roof variants should be shared");
    }
}
