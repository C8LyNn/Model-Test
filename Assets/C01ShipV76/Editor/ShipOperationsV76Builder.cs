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

public static class ShipOperationsV76Builder
{
    public const string ScenePath="Assets/C01ShipV76/Scenes/C01_Ship_Multideck_v76.unity";
    public const string MasterPath="Assets/C01ShipV76/Prefabs/C01_SHIP_MASTER_V76.prefab";
    const string Root="Assets/C01ShipV76";
    [Serializable] class Move { public string id,model,fromZone,toZone;public float[] before,after; }
    [Serializable] class Label { public string id,fromLabel,label; }
    [Serializable] class Plan { public Label[] labels;public Move[] moves;public string[] removed;public PlacementDataV5[] added;public GateDataV5 gate;public ModelDataV5[] models;public ZoneDataV5 exitZone; }
    static T Asset<T>(string path,T value) where T:UnityEngine.Object
    {
        var old=AssetDatabase.LoadAssetAtPath<T>(path);if(old==null){AssetDatabase.CreateAsset(value,path);return value;}
        EditorUtility.CopySerialized(value,old);UnityEngine.Object.DestroyImmediate(value);EditorUtility.SetDirty(old);return old;
    }
    static GameObject CreateModel(ModelDataV5 model)
    {
        var root=new GameObject(model.id);
        try
        {
            for(int i=0;i<model.parts.Length;i++)
            {
                var p=model.parts[i];var go=new GameObject(model.id+"__"+i.ToString("D2")+"_"+p.role);go.transform.SetParent(root.transform,false);
                var solid=go.AddComponent<ShipSolidV5>();solid.modelId=model.id;solid.partIndex=i;solid.role=p.role;
                var mesh=Asset(Root+"/Meshes/"+model.id+"__"+i.ToString("D2")+".asset",ShipV68Builder.Prism(p));go.AddComponent<MeshFilter>().sharedMesh=mesh;
                var mat=AssetDatabase.LoadAssetAtPath<Material>("Assets/C01ShipV68/Materials/"+p.role+".mat");if(mat==null)throw new Exception("Missing material "+p.role);
                go.AddComponent<MeshRenderer>().sharedMaterial=mat;
                if(ShipV68Builder.Rectangle(p)){var col=go.AddComponent<BoxCollider>();col.center=mesh.bounds.center;col.size=mesh.bounds.size;}
                else{var col=go.AddComponent<MeshCollider>();col.sharedMesh=mesh;col.convex=true;}
            }
            var prefab=PrefabUtility.SaveAsPrefabAsset(root,Root+"/Prefabs/Modules/"+model.id+".prefab");if(prefab==null)throw new Exception("Missing prefab "+model.id);return prefab;
        }
        finally {UnityEngine.Object.DestroyImmediate(root);}
    }
    [MenuItem("Tools/C01 Ship v7.6/Improve operational layout")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Stop play mode");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/operations.json"));
        if(plan==null||plan.moves.Length!=15||plan.labels.Length!=6||plan.removed.Length!=3||plan.added.Length!=24)throw new Exception("Invalid plan");
        foreach(var path in new[]{"Scenes","Prefabs/Modules","Meshes"})Directory.CreateDirectory(Root+"/"+path);
        AssetDatabase.Refresh();var prefabs=plan.models.ToDictionary(m=>m.id,CreateModel);
        var scene=EditorSceneManager.OpenScene("Assets/C01ShipV75/Scenes/C01_Ship_Multideck_v75.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null||explorer.master==null)throw new Exception("Missing master");
        var master=explorer.master;var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        foreach(var m in plan.moves)
        {
            if(!markers.TryGetValue(m.id,out var p)||p.modelId!=m.model||p.zoneId!=m.fromZone||Vector3.Distance(p.transform.position,new Vector3(m.before[0],m.before[1],m.before[2]))>.001f)throw new Exception("Unexpected placement "+m.id);
            p.transform.SetPositionAndRotation(new Vector3(m.after[0],m.after[1],m.after[2]),Quaternion.Euler(0,m.after[3],0));p.zoneId=m.toZone;
            PrefabUtility.RecordPrefabInstancePropertyModifications(p.transform);PrefabUtility.RecordPrefabInstancePropertyModifications(p);
        }
        foreach(var id in plan.removed)
        {
            if(!markers.TryGetValue(id,out var m))throw new Exception("Missing launch wall "+id);
            markers.Remove(id);UnityEngine.Object.DestroyImmediate(m.gameObject);
        }
        var zones=master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        foreach(var l in plan.labels)
        {
            if(!zones.TryGetValue(l.id,out var z)||z.label!=l.fromLabel)throw new Exception("Unexpected room "+l.id);
            z.label=l.label;var text=z.GetComponentInChildren<TextMesh>(true);if(text!=null){text.text=l.label;PrefabUtility.RecordPrefabInstancePropertyModifications(text);}
            PrefabUtility.RecordPrefabInstancePropertyModifications(z);
        }
        var added=new Dictionary<string,ShipInstanceV5>();
        foreach(var p in plan.added)
        {
            if(!prefabs.TryGetValue(p.model,out var prefab))
            {
                var path="Assets/C01ShipV68/Prefabs/Modules/"+p.model+".prefab";prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);if(prefab==null)throw new Exception("Missing "+path);prefabs[p.model]=prefab;
            }
            var group=master.transform.Find(p.category);if(group==null){var go=new GameObject(p.category);group=go.transform;group.SetParent(master.transform,false);}
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group);instance.name=p.id;
            instance.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));instance.transform.localScale=Vector3.one;
            var marker=instance.AddComponent<ShipInstanceV5>();marker.placementId=p.id;marker.modelId=p.model;marker.category=p.category;marker.zoneId=p.zone;marker.deck=p.deck;added[p.id]=marker;
        }
        var g=plan.gate;var gateRoot=master.transform.Find("GateControllers");if(gateRoot==null)throw new Exception("Missing gate controllers");
        var gateObj=new GameObject(g.id);gateObj.transform.SetParent(gateRoot,false);gateObj.transform.SetPositionAndRotation(new Vector3(g.x,g.y,g.z),Quaternion.Euler(0,g.yaw,0));
        var gate=gateObj.AddComponent<ShipGateV5>();gate.id=g.id;gate.leaves=g.leaves.Select(id=>added[id].transform).ToArray();
        gate.travel=g.leaves.Select(id=>{var p=plan.added.Single(a=>a.id==id);return new Vector3(p.travel[0],p.travel[1],p.travel[2]);}).ToArray();gate.SetImmediate(0);
        var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");var buttons=new List<ShipButtonV5>();
        foreach(var p in plan.added.Where(p=>!string.IsNullOrEmpty(p.buttonGate)))
        {
            var button=added[p.id].gameObject.AddComponent<ShipButtonV5>();button.gateId=p.buttonGate;button.gate=gate;button.floor=0;
            var sign=new GameObject("Button_Label");sign.transform.SetParent(button.transform,false);sign.transform.localPosition=new Vector3(.11f,.14f,.112f);sign.transform.localRotation=Quaternion.Euler(0,180,0);
            var text=sign.AddComponent<TextMesh>();text.font=font;text.fontSize=40;text.characterSize=.02f;text.anchor=TextAnchor.MiddleCenter;text.text="WYLOT";text.color=Color.white;sign.GetComponent<MeshRenderer>().sharedMaterial=font.material;buttons.Add(button);
        }
        var zroot=master.transform.Find("Zones");if(zroot==null)throw new Exception("Missing zones");
        var exit=new GameObject(plan.exitZone.id);exit.transform.SetParent(zroot,false);exit.transform.position=new Vector3(plan.exitZone.waypoint[0],plan.exitZone.waypoint[1],plan.exitZone.waypoint[2]);
        var markerExit=exit.AddComponent<ShipZoneV5>();markerExit.zoneId=plan.exitZone.id;markerExit.label=plan.exitZone.label;markerExit.kind=plan.exitZone.kind;markerExit.deck=0;markerExit.floor=-3.4f;markerExit.height=3;
        explorer.gates=explorer.gates.Concat(new[]{gate}).ToArray();explorer.buttons=explorer.buttons.Concat(buttons).ToArray();
        if(signage!=null)signage.enabled=true;explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Could not save master");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.6 operations built: moved="+plan.moves.Length+" rooms="+plan.labels.Length+" added="+plan.added.Length);
    }
}
