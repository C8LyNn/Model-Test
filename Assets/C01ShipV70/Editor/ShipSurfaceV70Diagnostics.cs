using System;
using System.Linq;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipSurfaceV70Diagnostics
{
    public static void InspectPrefabLinks()
    {
        EditorSceneManager.OpenScene(ShipSurfaceV70Builder.ScenePath,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        var ids=new[]{"W_H_-12_18_-3.4","C1_0_18"};
        var all=explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);
        foreach(var id in ids)
        {
            var marker=all.Single(x=>x.placementId==id);var g=marker.gameObject;
            var original=PrefabUtility.GetCorrespondingObjectFromSource(g);
            var nearest=PrefabUtility.GetNearestPrefabInstanceRoot(g);
            Debug.Log("C01 PREFAB "+id+" model="+marker.modelId+" isInstance="+PrefabUtility.IsPartOfPrefabInstance(g)+
                      " nearest="+(nearest!=null?nearest.name:"NULL")+" path="+PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(g)+
                      " source="+(original!=null?AssetDatabase.GetAssetPath(original):"NULL"));
        }
    }
}
