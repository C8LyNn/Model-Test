using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using C01.Ship.V5;
using C01.Ship.V5.Editor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipTallSectorsV78Builder
{
    const string Root = "Assets/C01ShipV78";
    public const string ScenePath = Root + "/Scenes/C01_Ship_Multideck_v78.unity";
    public const string MasterPath = Root + "/Prefabs/C01_SHIP_MASTER_V78.prefab";
    [Serializable] class Change { public string id,oldModel,newModel; }
    [Serializable] class Plan { public string[] roof, removed, sectors; public PlacementDataV5[] added; public ModelDataV5[] models; public Change[] ceilingChanges; }

    static GameObject CreateModel(ModelDataV5 model)
    {
        var root=new GameObject(model.id);
        try {
            for(int i=0;i<model.parts.Length;i++) {
                var p=model.parts[i];var go=new GameObject(model.id+"__"+i.ToString("D2")+"_"+p.role);go.transform.SetParent(root.transform,false);
                var solid=go.AddComponent<ShipSolidV5>();solid.modelId=model.id;solid.partIndex=i;solid.role=p.role;
                var mesh=ShipV68Builder.Prism(p);var meshPath=Root+"/Meshes/"+model.id+"__"+i.ToString("D2")+".asset";
                var existing=AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
                if(existing==null){AssetDatabase.CreateAsset(mesh,meshPath);existing=mesh;}else{EditorUtility.CopySerialized(mesh,existing);UnityEngine.Object.DestroyImmediate(mesh);EditorUtility.SetDirty(existing);}
                go.AddComponent<MeshFilter>().sharedMesh=existing;
                var mat=AssetDatabase.LoadAssetAtPath<Material>("Assets/C01ShipV68/Materials/"+p.role+".mat");if(mat==null)throw new Exception("Missing material "+p.role);
                go.AddComponent<MeshRenderer>().sharedMaterial=mat;
                if(ShipV68Builder.Rectangle(p)){var col=go.AddComponent<BoxCollider>();col.center=existing.bounds.center;col.size=existing.bounds.size;}
                else {var col=go.AddComponent<MeshCollider>();col.sharedMesh=existing;col.convex=true;}
            }
            var prefab=PrefabUtility.SaveAsPrefabAsset(root,Root+"/Prefabs/Modules/"+model.id+".prefab");if(prefab==null)throw new Exception("Cannot save model "+model.id);return prefab;
        } finally {UnityEngine.Object.DestroyImmediate(root);}
    }

    [MenuItem("Tools/C01 Ship v7.8/Raise sector roofs")]
    public static void Build()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/tall_sectors.json"));
        if(plan==null||plan.sectors.Length!=6||plan.roof.Length!=504)throw new Exception("Invalid sector plan");
        Directory.CreateDirectory(Root+"/Scenes");Directory.CreateDirectory(Root+"/Prefabs/Modules");Directory.CreateDirectory(Root+"/Meshes");
        AssetDatabase.Refresh();var models=plan.models.ToDictionary(m=>m.id,CreateModel);
        var scene=EditorSceneManager.OpenScene("Assets/C01ShipV77/Scenes/C01_Ship_Multideck_v77.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null||explorer.master==null)throw new Exception("Missing master");
        var master=explorer.master;
        int layers=0;
        while(PrefabUtility.IsPartOfPrefabInstance(master))
        {if(++layers>20)throw new Exception("Could not unpack master");PrefabUtility.UnpackPrefabInstance(master,PrefabUnpackMode.OutermostRoot,InteractionMode.AutomatedAction);}
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        var zones=master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        foreach(string id in plan.sectors){if(!zones.TryGetValue(id,out var zone)||Math.Abs(zone.height-6)>.001f)throw new Exception("Invalid sector "+id);zone.height=9;}
        foreach(string id in plan.roof)
        {
            if(!markers.TryGetValue(id,out var m)||Math.Abs(m.transform.position.y-6.2f)>.001f)throw new Exception("Invalid roof "+id);
            m.transform.position+=Vector3.up*3;PrefabUtility.RecordPrefabInstancePropertyModifications(m.transform);
        }
        foreach(string id in plan.removed)
        {if(!markers.TryGetValue(id,out var m)||m==null)throw new Exception("Missing replacement "+id);UnityEngine.Object.DestroyImmediate(m.gameObject);}
        foreach(var change in plan.ceilingChanges)
        {
            if(!markers.TryGetValue(change.id,out var old)||old==null||old.modelId!=change.oldModel)throw new Exception("Missing ceiling "+change.id);
            var obj=(GameObject)PrefabUtility.InstantiatePrefab(models[change.newModel],old.transform.parent);obj.name=old.gameObject.name;
            obj.transform.SetPositionAndRotation(old.transform.position,old.transform.rotation);obj.transform.localScale=old.transform.localScale;
            var marker=obj.AddComponent<ShipInstanceV5>();marker.placementId=old.placementId;marker.modelId=change.newModel;marker.category=old.category;marker.zoneId=old.zoneId;marker.deck=old.deck;
            UnityEngine.Object.DestroyImmediate(old.gameObject);
        }
        foreach(var p in plan.added)
        {
            if(!models.TryGetValue(p.model,out var prefab))
            {prefab=AssetDatabase.LoadAssetAtPath<GameObject>((p.model=="N_H2600"?"Assets/C01ShipV68/Prefabs/Modules/":"Assets/C01ShipV71/Prefabs/Modules/")+p.model+".prefab");if(prefab==null)throw new Exception("Missing "+p.model);models[p.model]=prefab;}
            var parent=zones[p.zone].transform.Find("Moduly_Poziom_1_i_2");if(parent==null)throw new Exception("Missing sector parent "+p.zone);
            var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,parent);go.name=p.id;
            go.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));go.transform.localScale=Vector3.one;
            var m=go.AddComponent<ShipInstanceV5>();m.placementId=p.id;m.modelId=p.model;m.category=p.category;m.zoneId=p.zone;m.deck=p.deck;
        }
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Failed prefab save");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Failed scene save");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.8 sectors="+plan.sectors.Length+" roofs="+plan.roof.Length+" replaced="+plan.removed.Length+" new="+plan.added.Length);
    }
}
