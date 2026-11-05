using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Prototype only: ducts do not yet form a shipwide network.
public static class ShipVentilationV79Prototype
{
    const string Root="Assets/C01ShipV79";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Ventilation_PROTOTYPE_v79.unity";
    const string MasterPath=Root+"/Prefabs/C01_SHIP_VENT_PROTOTYPE_V79.prefab";
    [Serializable] class Map { public string oldId,newId; }
    [Serializable] class Plan { public string[] removed,removedGates,removedZones,rooms;public Map[] zoneMap;public PlacementDataV5[] added; }

    public static void RegisterPrototypeForTests()
    {
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
    }

    [MenuItem("Tools/C01 Ship v7.9/Build incomplete ventilation prototype")]
    public static void Build()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/ventilation.json"));
        if(plan==null||plan.rooms.Length!=12||plan.added.Length!=24)throw new Exception("Invalid prototype plan");
        Directory.CreateDirectory(Root+"/Scenes");Directory.CreateDirectory(Root+"/Prefabs");
        var scene=EditorSceneManager.OpenScene("Assets/C01ShipV78/Scenes/C01_Ship_Multideck_v78.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null||explorer.master==null)throw new Exception("Missing master");
        var master=explorer.master;int layers=0;
        while(PrefabUtility.IsPartOfPrefabInstance(master)){if(++layers>20)throw new Exception("Cannot unpack master");PrefabUtility.UnpackPrefabInstance(master,PrefabUnpackMode.OutermostRoot,InteractionMode.AutomatedAction);}
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        var zones=master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        var removedGateSet=new HashSet<string>(plan.removedGates);
        foreach(var gate in explorer.gates.Where(g=>g!=null&&removedGateSet.Contains(g.id)).ToArray())UnityEngine.Object.DestroyImmediate(gate.gameObject);
        explorer.gates=explorer.gates.Where(g=>g!=null).ToArray();
        foreach(var id in plan.removed)
        {if(!markers.TryGetValue(id,out var m))throw new Exception("Missing removal "+id);if(m!=null)UnityEngine.Object.DestroyImmediate(m.gameObject);}
        foreach(var map in plan.zoneMap)
        {
            foreach(var m in markers.Values.Where(m=>m!=null&&m.zoneId==map.oldId)) {m.zoneId=map.newId;PrefabUtility.RecordPrefabInstancePropertyModifications(m);}
            if(!zones.TryGetValue(map.oldId,out var zone)||zone==null)throw new Exception("Missing bathroom "+map.oldId);
            UnityEngine.Object.DestroyImmediate(zone.gameObject);
        }
        foreach(var id in plan.rooms)
        {
            var zone=zones[id];zone.kind="ventilation_service";zone.label="WENTYLACJA "+id.Split('_').Last();
            var label=zone.GetComponentsInChildren<TextMesh>(true).FirstOrDefault(t=>t.GetComponentInParent<ShipInstanceV5>()==null);if(label!=null)label.text=zone.label;
        }
        explorer.buttons=explorer.buttons.Where(b=>b!=null).ToArray();
        var vent=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01ShipV68/Prefabs/Modules/P_Vent_3m.prefab");if(vent==null)throw new Exception("Missing duct module");
        var group=new GameObject("VENTILATION_PROTOTYPE_NOT_CONNECTED").transform;group.SetParent(master.transform,false);
        foreach(var p in plan.added)
        {
            var go=(GameObject)PrefabUtility.InstantiatePrefab(vent,group);go.name=p.id;go.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));
            var marker=go.AddComponent<ShipInstanceV5>();marker.placementId=p.id;marker.modelId=p.model;marker.category=p.category;marker.zoneId=p.zone;marker.deck=p.deck;
        }
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Prefab save failed");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Scene save failed");
        AssetDatabase.SaveAssets();Debug.Log("V7.9 PROTOTYPE ONLY; service rooms="+plan.rooms.Length+", duct modules="+plan.added.Length+"; network incomplete");
    }
}
