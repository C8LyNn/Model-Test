using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V5.Editor;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipPursuitV74Builder
{
    const string Root="Assets/C01ShipV74";
    const string PreviousScene="Assets/C01ShipV73/Scenes/C01_Ship_Multideck_v73.unity";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Multideck_v74.unity";
    public const string MasterPath=Root+"/Prefabs/C01_SHIP_MASTER_V74.prefab";
    [Serializable] class Plan { public string[] removed;public PlacementDataV5[] added;public GateDataV5[] gates;public ZoneDataV5[] zones;public ModelDataV5[] models; }
    static T Asset<T>(string path,T value) where T:UnityEngine.Object
    {
        var old=AssetDatabase.LoadAssetAtPath<T>(path);if(old==null){AssetDatabase.CreateAsset(value,path);return value;}
        EditorUtility.CopySerialized(value,old);UnityEngine.Object.DestroyImmediate(value);EditorUtility.SetDirty(old);return old;
    }
    static GameObject CreateModel(ModelDataV5 model)
    {
        var obj=new GameObject(model.id);
        try
        {
            for(int i=0;i<model.parts.Length;i++)
            {
                var part=model.parts[i];var child=new GameObject(model.id+"__"+i.ToString("D2")+"_"+part.role);
                child.transform.SetParent(obj.transform,false);var solid=child.AddComponent<ShipSolidV5>();
                solid.modelId=model.id;solid.partIndex=i;solid.role=part.role;
                var mesh=Asset(Root+"/Meshes/"+model.id+"__"+i.ToString("D2")+".asset",ShipV68Builder.Prism(part));
                child.AddComponent<MeshFilter>().sharedMesh=mesh;
                var material=AssetDatabase.LoadAssetAtPath<Material>("Assets/C01ShipV68/Materials/"+part.role+".mat");
                if(material==null)throw new Exception("Missing material "+part.role);
                child.AddComponent<MeshRenderer>().sharedMaterial=material;
                if(ShipV68Builder.Rectangle(part)){var collider=child.AddComponent<BoxCollider>();collider.center=mesh.bounds.center;collider.size=mesh.bounds.size;}
                else {var collider=child.AddComponent<MeshCollider>();collider.sharedMesh=mesh;collider.convex=true;}
            }
            var prefab=PrefabUtility.SaveAsPrefabAsset(obj,Root+"/Prefabs/Modules/"+model.id+".prefab");
            if(prefab==null)throw new Exception("Could not save module "+model.id);return prefab;
        }
        finally{UnityEngine.Object.DestroyImmediate(obj);}
    }
    static GameObject ExistingModule(string model)
    {
        var path=model.StartsWith("W3_H")?"Assets/C01ShipV71/Prefabs/Modules/":"Assets/C01ShipV68/Prefabs/Modules/";
        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path+model+".prefab");
        if(prefab==null)throw new Exception("Missing module "+path+model);return prefab;
    }
    [MenuItem("Tools/C01 Ship v7.4/Build sector pursuit route")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Stop play mode first");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/pursuit.json"));
        if(plan==null||plan.removed.Length!=6||plan.gates.Length!=6||plan.models.Length!=2)throw new Exception("Invalid pursuit plan");
        foreach(var folder in new[]{"Scenes","Prefabs/Modules","Meshes"})Directory.CreateDirectory(Root+"/"+folder);
        AssetDatabase.Refresh();var prefabs=plan.models.ToDictionary(m=>m.id,CreateModel);
        var scene=EditorSceneManager.OpenScene(PreviousScene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null||explorer.master==null)throw new Exception("Missing previous master");
        var master=explorer.master;var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        foreach(var id in plan.removed)
        {
            if(!markers.TryGetValue(id,out var marker)||marker.modelId!="W3_H3000")throw new Exception("Unexpected opening "+id);
            markers.Remove(id);UnityEngine.Object.DestroyImmediate(marker.gameObject);
        }
        var added=new Dictionary<string,ShipInstanceV5>();
        foreach(var p in plan.added)
        {
            if(markers.ContainsKey(p.id))throw new Exception("Duplicate "+p.id);
            var group=master.transform.Find(p.category);
            if(group==null){var go=new GameObject(p.category);group=go.transform;group.SetParent(master.transform,false);}
            if(!prefabs.TryGetValue(p.model,out var prefab))prefabs[p.model]=prefab=ExistingModule(p.model);
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group);instance.name=p.id;
            instance.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));instance.transform.localScale=Vector3.one;
            var marker=instance.AddComponent<ShipInstanceV5>();marker.placementId=p.id;marker.modelId=p.model;marker.category=p.category;marker.zoneId=p.zone;marker.deck=p.deck;
            added[p.id]=marker;
        }
        var gates=new Dictionary<string,ShipGateV5>();var gateRoot=master.transform.Find("GateControllers");
        if(gateRoot==null)throw new Exception("Gate controller group missing");
        foreach(var g in plan.gates)
        {
            var obj=new GameObject(g.id);obj.transform.SetParent(gateRoot,false);obj.transform.SetPositionAndRotation(new Vector3(g.x,g.y,g.z),Quaternion.Euler(0,g.yaw,0));
            var gate=obj.AddComponent<ShipGateV5>();gate.id=g.id;gate.leaves=g.leaves.Select(id=>added[id].transform).ToArray();
            gate.travel=g.leaves.Select(id=>{var p=plan.added.Single(x=>x.id==id);return new Vector3(p.travel[0],p.travel[1],p.travel[2]);}).ToArray();
            gate.SetImmediate(1);gates[g.id]=gate;
        }
        var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");var buttons=new List<ShipButtonV5>();
        foreach(var p in plan.added.Where(p=>!string.IsNullOrEmpty(p.buttonGate)))
        {
            var button=added[p.id].gameObject.AddComponent<ShipButtonV5>();button.gateId=p.buttonGate;button.gate=gates[p.buttonGate];button.floor=p.buttonFloor;
            var sign=new GameObject("Button_Label");sign.transform.SetParent(button.transform,false);sign.transform.localPosition=new Vector3(.11f,.14f,.112f);
            sign.transform.localRotation=Quaternion.Euler(0,180,0);var text=sign.AddComponent<TextMesh>();text.font=font;text.fontSize=40;text.characterSize=.02f;
            text.anchor=TextAnchor.MiddleCenter;text.text="BRAMA";text.color=Color.white;sign.GetComponent<MeshRenderer>().sharedMaterial=font.material;buttons.Add(button);
        }
        foreach(var z in plan.zones)
        {
            var zone=master.GetComponentsInChildren<ShipZoneV5>(true).Single(x=>x.zoneId==z.id);zone.kind=z.kind;zone.label=z.label;
            var text=zone.GetComponentInChildren<TextMesh>(true);if(text!=null){text.text=z.label;PrefabUtility.RecordPrefabInstancePropertyModifications(text);}
            PrefabUtility.RecordPrefabInstancePropertyModifications(zone);
        }
        explorer.gates=explorer.gates.Concat(gates.Values).ToArray();explorer.buttons=explorer.buttons.Concat(buttons).ToArray();
        if(signage!=null)signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Could not save master");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))
            EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.4 sector route built: removed="+plan.removed.Length+" added="+plan.added.Length+" gates="+gates.Count);
    }
}
