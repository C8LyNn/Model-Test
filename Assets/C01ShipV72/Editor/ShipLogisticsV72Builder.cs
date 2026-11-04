using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipLogisticsV72Builder
{
    const string Root="Assets/C01ShipV72";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Multideck_v72.unity";
    public const string MasterPath=Root+"/Prefabs/C01_SHIP_MASTER_V72.prefab";
    const string PreviousScene="Assets/C01ShipV71/Scenes/C01_Ship_Multideck_v71.unity";
    [Serializable] class Plan { public Swap[] swaps; public Move[] moves; }
    [Serializable] class Swap { public string original,replacement,label; }
    [Serializable] class Move { public string id,model,zone; public float fromX,toX,y,z; }

    [MenuItem("Tools/C01 Ship v7.2/Improve deck zero logistics")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Stop play mode first");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/logistics.json"));
        if(plan==null || plan.swaps.Length!=4 || plan.moves.Length!=14)throw new Exception("Invalid logistics plan");
        foreach(var folder in new[]{"Scenes","Prefabs"}) Directory.CreateDirectory(Root+"/"+folder);
        AssetDatabase.Refresh();
        var scene=EditorSceneManager.OpenScene(PreviousScene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null || explorer.master==null)throw new Exception("Missing previous master");
        var master=explorer.master;
        var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var swaps=plan.swaps.ToDictionary(s=>s.original);
        var moves=plan.moves.ToDictionary(m=>m.id);
        var instances=master.GetComponentsInChildren<ShipInstanceV5>(true);
        var moved=0;var remapped=0;
        foreach(var instance in instances)
        {
            if(moves.TryGetValue(instance.placementId??"",out var move))
            {
                if(instance.modelId!=move.model || instance.zoneId!=move.zone ||
                   Mathf.Abs(instance.transform.position.x-move.fromX)>.001f ||
                   Mathf.Abs(instance.transform.position.y-move.y)>.001f ||
                   Mathf.Abs(instance.transform.position.z-move.z)>.001f)
                    throw new Exception("Unexpected item: "+move.id);
                var pos=instance.transform.position;pos.x=move.toX;instance.transform.position=pos;
                PrefabUtility.RecordPrefabInstancePropertyModifications(instance.transform);
                moved++;
            }
            else if(instance.zoneId!=null && swaps.TryGetValue(instance.zoneId,out var swap))
            {
                instance.zoneId=swap.replacement;
                PrefabUtility.RecordPrefabInstancePropertyModifications(instance);
                remapped++;
            }
        }
        if(moved!=plan.moves.Length)throw new Exception("Missing moved items: "+moved);
        int zones=0;
        foreach(var zone in master.GetComponentsInChildren<ShipZoneV5>(true))
        {
            if(!swaps.TryGetValue(zone.zoneId,out var swap))continue;
            zone.zoneId=swap.replacement;zone.label=swap.label;zone.gameObject.name=swap.replacement;
            var text=zone.GetComponentInChildren<TextMesh>(true);if(text!=null)text.text=swap.label;
            PrefabUtility.RecordPrefabInstancePropertyModifications(zone);
            PrefabUtility.RecordPrefabInstancePropertyModifications(zone.gameObject);
            if(text!=null)PrefabUtility.RecordPrefabInstancePropertyModifications(text);
            zones++;
        }
        if(zones!=4)throw new Exception("Wrong sector count: "+zones);
        if(signage!=null)signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)
            throw new Exception("Could not save master prefab");
        EditorSceneManager.MarkSceneDirty(scene);
        if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))
            EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();
        Debug.Log("C01 V7.2 logistics built: moved="+moved+" zoneMarkers="+remapped+" zones="+zones);
    }
}
