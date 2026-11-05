using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V5.Editor;
using C01.Ship.V6.Cargo;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipTwoDecksV77Builder
{
    const string Root="Assets/C01ShipV77";
    public const string ScenePath=Root+"/Scenes/C01_Ship_Multideck_v77.unity";
    public const string MasterPath=Root+"/Prefabs/C01_SHIP_MASTER_V77.prefab";
    [Serializable] class Move {public string oldId,newId,model,zone;public float[] before,after;}
    [Serializable] class Label {public string id,label;}
    [Serializable] class Plan {public string[] removed,removedGates,removedZones;public Move[] moves;public Label[] labels;public PlacementDataV5[] added;public ModelDataV5[] models;public GateDataV5 gate;public ZoneDataV5 exitZone;}
    public static void InspectPrevious()
    {
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/two_decks.json"));
        EditorSceneManager.OpenScene("Assets/C01ShipV76/Scenes/C01_Ship_Multideck_v76.unity",OpenSceneMode.Single);
        var master=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>().master;
        var markers=new HashSet<string>(master.GetComponentsInChildren<ShipInstanceV5>(true).Select(m=>m.placementId));
        var missing=plan.removed.Where(id=>!markers.Contains(id)).ToArray();
        Debug.Log("C01 V7.7 prior-missing="+missing.Length+" "+string.Join(",",missing));
    }
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
    [MenuItem("Tools/C01 Ship v7.7/Remove deck zero")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Stop play mode");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText(Root+"/Data/two_decks.json"));
        if(plan==null||plan.moves.Length!=30||plan.removedGates.Length!=39||plan.added.Length!=36)throw new Exception("Invalid plan");
        foreach(var path in new[]{"Scenes","Prefabs/Modules","Meshes"})Directory.CreateDirectory(Root+"/"+path);
        AssetDatabase.Refresh();var prefabs=plan.models.ToDictionary(m=>m.id,CreateModel);
        var scene=EditorSceneManager.OpenScene("Assets/C01ShipV76/Scenes/C01_Ship_Multideck_v76.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null||explorer.master==null)throw new Exception("Missing master");
        var master=explorer.master;int layers=0;
        while(PrefabUtility.IsPartOfPrefabInstance(master)){if(++layers>20)throw new Exception("Cannot unpack master layers");PrefabUtility.UnpackPrefabInstance(master,PrefabUnpackMode.OutermostRoot,InteractionMode.AutomatedAction);}
        var signage=master.GetComponent<ButtonSignage>();if(signage!=null)signage.enabled=false;
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).Where(m=>!string.IsNullOrEmpty(m.placementId)).ToDictionary(m=>m.placementId);
        var zones=master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        var movedIds=new HashSet<string>();
        foreach(var move in plan.moves)
        {
            if(!markers.TryGetValue(move.oldId,out var m)||m.modelId!=move.model||Vector3.Distance(m.transform.position,new Vector3(move.before[0],move.before[1],move.before[2]))>.002f)throw new Exception("Unexpected item "+move.oldId);
            var owner=zones[move.zone].transform.Find("Moduly_Poziom_1_i_2");if(owner==null)throw new Exception("Missing shared sector "+move.zone);
            m.transform.SetParent(owner,true);if(m.transform.parent!=owner)throw new Exception("Unable to move "+move.oldId);
            m.transform.SetPositionAndRotation(new Vector3(move.after[0],move.after[1],move.after[2]),Quaternion.Euler(0,move.after[3],0));
            m.gameObject.name=move.newId;m.placementId=move.newId;m.zoneId=move.zone;m.deck=1;movedIds.Add(move.oldId);
            PrefabUtility.RecordPrefabInstancePropertyModifications(m);PrefabUtility.RecordPrefabInstancePropertyModifications(m.transform);
        }
        var removedGateSet=new HashSet<string>(plan.removedGates);
        foreach(var lift in explorer.lifts)
        {
            if(lift==null||lift.landings.Length<3)throw new Exception("Missing lift landings");
            lift.landings[0]=null;lift.currentFloor=1;lift.targetFloor=1;
            PrefabUtility.RecordPrefabInstancePropertyModifications(lift);
        }
        foreach(var cargo in master.GetComponentsInChildren<CargoLiftController>(true))
        {cargo.allowMissingDeckZero=true;PrefabUtility.RecordPrefabInstancePropertyModifications(cargo);}
        foreach(var gate in explorer.gates.Where(g=>g!=null&&removedGateSet.Contains(g.id)).ToArray())UnityEngine.Object.DestroyImmediate(gate.gameObject);
        explorer.gates=explorer.gates.Where(g=>g!=null).ToArray();
        foreach(var air in master.GetComponentsInChildren<ShipAirlockV5>(true))if(air.gateA==null||air.gateB==null)UnityEngine.Object.DestroyImmediate(air.gameObject);
        int removed=0;
        // V7.6 intentionally has only one physical button for each lift landing;
        // the source manifest retains the unused second-side placement IDs.
        var absentLandingButtons=new HashSet<string>(plan.removedGates.Where(id=>id.EndsWith("_LANDING_0")).Select(id=>id+"_BUTTON_1"));
        foreach(var id in plan.removed)
        {
            if(movedIds.Contains(id))continue;
            if(!markers.TryGetValue(id,out var marker))
            {if(absentLandingButtons.Contains(id)){removed++;continue;}throw new Exception("Missing removed module "+id);}
            // Some landing buttons are children of the gate controller and have
            // already been removed together with their parent.
            if(marker==null){removed++;continue;}
            UnityEngine.Object.DestroyImmediate(marker.gameObject);removed++;
        }
        foreach(var id in plan.removedZones)
        {if(!zones.TryGetValue(id,out var zone)||zone==null)throw new Exception("Missing removed zone "+id);UnityEngine.Object.DestroyImmediate(zone.gameObject);}
        explorer.buttons=explorer.buttons.Where(b=>b!=null).ToArray();
        foreach(var label in plan.labels)
        {
            var zone=zones[label.id];zone.label=label.label;
            var text=zone.GetComponentsInChildren<TextMesh>(true).FirstOrDefault(t=>t.GetComponentInParent<ShipInstanceV5>()==null);
            if(text!=null)text.text=label.label;
        }
        var added=new Dictionary<string,ShipInstanceV5>();
        foreach(var p in plan.added)
        {
            if(!prefabs.TryGetValue(p.model,out var prefab))
            {
                var dir=p.model.StartsWith("G76_")?"Assets/C01ShipV76/Prefabs/Modules/":"Assets/C01ShipV68/Prefabs/Modules/";
                prefab=AssetDatabase.LoadAssetAtPath<GameObject>(dir+p.model+".prefab");if(prefab==null)throw new Exception("Missing module "+p.model);prefabs[p.model]=prefab;
            }
            var group=p.zone=="L1_CARGO"?zones["L1_CARGO"].transform.Find("Moduly_Poziom_1_i_2"):master.transform.Find(p.category);
            if(group==null){var go=new GameObject(p.category);group=go.transform;group.SetParent(master.transform,false);}
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group);instance.name=p.id;
            instance.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));instance.transform.localScale=Vector3.one;
            var marker=instance.AddComponent<ShipInstanceV5>();marker.placementId=p.id;marker.modelId=p.model;marker.category=p.category;marker.zoneId=p.zone;marker.deck=p.deck;added[p.id]=marker;
        }
        var g=plan.gate;var gateRoot=master.transform.Find("GateControllers");if(gateRoot==null)throw new Exception("Missing gate controllers");
        var gateObj=new GameObject(g.id);gateObj.transform.SetParent(gateRoot,false);gateObj.transform.SetPositionAndRotation(new Vector3(g.x,g.y,g.z),Quaternion.Euler(0,g.yaw,0));
        var gateNew=gateObj.AddComponent<ShipGateV5>();gateNew.id=g.id;gateNew.leaves=g.leaves.Select(id=>added[id].transform).ToArray();
        gateNew.travel=g.leaves.Select(id=>{var p=plan.added.Single(a=>a.id==id);return new Vector3(p.travel[0],p.travel[1],p.travel[2]);}).ToArray();gateNew.SetImmediate(0);
        var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");var buttons=new List<ShipButtonV5>();
        foreach(var p in plan.added.Where(p=>!string.IsNullOrEmpty(p.buttonGate)))
        {
            var button=added[p.id].gameObject.AddComponent<ShipButtonV5>();button.gateId=p.buttonGate;button.gate=gateNew;button.floor=1;
            var sign=new GameObject("Button_Label");sign.transform.SetParent(button.transform,false);sign.transform.localPosition=new Vector3(.11f,.14f,.112f);sign.transform.localRotation=Quaternion.Euler(0,180,0);
            var text=sign.AddComponent<TextMesh>();text.font=font;text.fontSize=40;text.characterSize=.02f;text.anchor=TextAnchor.MiddleCenter;text.text="WYLOT";text.color=Color.white;sign.GetComponent<MeshRenderer>().sharedMaterial=font.material;buttons.Add(button);
        }
        var zroot=master.transform.Find("Zones");if(zroot==null)throw new Exception("Missing zones");
        var exit=new GameObject(plan.exitZone.id);exit.transform.SetParent(zroot,false);exit.transform.position=new Vector3(plan.exitZone.waypoint[0],plan.exitZone.waypoint[1],plan.exitZone.waypoint[2]);
        var markerExit=exit.AddComponent<ShipZoneV5>();markerExit.zoneId=plan.exitZone.id;markerExit.label=plan.exitZone.label;markerExit.kind=plan.exitZone.kind;markerExit.deck=1;markerExit.floor=0;markerExit.height=3;
        explorer.gates=explorer.gates.Concat(new[]{gateNew}).ToArray();explorer.buttons=explorer.buttons.Concat(buttons).ToArray();explorer.minDeck=1;explorer.selectedDeck=1;
        if(signage!=null)signage.enabled=true;explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Could not save master");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.7 two decks: removed="+removed+" moved="+plan.moves.Length+" added="+plan.added.Length);
    }
}
