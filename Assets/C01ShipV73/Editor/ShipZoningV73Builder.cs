using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipZoningV73Builder
{
    const string Root="Assets/C01ShipV73";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Multideck_v73.unity";
    public const string MasterPath=Root+"/Prefabs/C01_SHIP_MASTER_V73.prefab";
    const string PreviousScene="Assets/C01ShipV72/Scenes/C01_Ship_Multideck_v72.unity";
    [Serializable] class Plan { public Swap[] swaps;public Relabel[] relabels;public Move[] moves; }
    [Serializable] class Swap { public string original,replacement,label; }
    [Serializable] class Relabel { public string id,label; }
    [Serializable] class Move { public string id,model,zone;public float fromX,toX,y,z; }
    static void Label(ShipZoneV5 zone,string label)
    {
        zone.label=label;var text=zone.GetComponentInChildren<TextMesh>(true);if(text!=null)text.text=label;
        PrefabUtility.RecordPrefabInstancePropertyModifications(zone);
        if(text!=null)PrefabUtility.RecordPrefabInstancePropertyModifications(text);
    }
    [MenuItem("Tools/C01 Ship v7.3/Align cargo and workshop")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Stop play mode first");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/zoning.json"));
        if(plan==null||plan.swaps.Length!=2||plan.relabels.Length!=4||plan.moves.Length!=8)throw new Exception("Invalid zoning plan");
        foreach(var folder in new[]{"Scenes","Prefabs"})Directory.CreateDirectory(Root+"/"+folder);
        AssetDatabase.Refresh();var scene=EditorSceneManager.OpenScene(PreviousScene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null||explorer.master==null)throw new Exception("Missing previous master");
        var master=explorer.master;var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var swaps=plan.swaps.ToDictionary(s=>s.original);var moves=plan.moves.ToDictionary(m=>m.id);
        int moved=0,remapped=0;
        foreach(var instance in master.GetComponentsInChildren<ShipInstanceV5>(true))
        {
            if(moves.TryGetValue(instance.placementId??"",out var move))
            {
                var p=instance.transform.position;
                if(instance.modelId!=move.model||instance.zoneId!=move.zone||Mathf.Abs(p.x-move.fromX)>.001f||
                   Mathf.Abs(p.y-move.y)>.001f||Mathf.Abs(p.z-move.z)>.001f)throw new Exception("Unexpected item: "+move.id);
                p.x=move.toX;instance.transform.position=p;PrefabUtility.RecordPrefabInstancePropertyModifications(instance.transform);moved++;
            }
            else if(instance.zoneId!=null&&swaps.TryGetValue(instance.zoneId,out var swap))
            {instance.zoneId=swap.replacement;PrefabUtility.RecordPrefabInstancePropertyModifications(instance);remapped++;}
        }
        if(moved!=plan.moves.Length)throw new Exception("Missing equipment: "+moved);
        int sectorCount=0,supportCount=0;var relabels=plan.relabels.ToDictionary(r=>r.id);
        foreach(var zone in master.GetComponentsInChildren<ShipZoneV5>(true))
        {
            if(swaps.TryGetValue(zone.zoneId,out var swap))
            {zone.zoneId=swap.replacement;zone.gameObject.name=swap.replacement;Label(zone,swap.label);
             PrefabUtility.RecordPrefabInstancePropertyModifications(zone.gameObject);sectorCount++;}
            else if(relabels.TryGetValue(zone.zoneId,out var relabel)){Label(zone,relabel.label);supportCount++;}
        }
        if(sectorCount!=2||supportCount!=4)throw new Exception("Incorrect zone count");
        if(signage!=null)signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Could not save master");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))
            EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.3 zoning: moved="+moved+" zoneMarkers="+remapped+" sectors="+sectorCount+" support="+supportCount);
    }
}
