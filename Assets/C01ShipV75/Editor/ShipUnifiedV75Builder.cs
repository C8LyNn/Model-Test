using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipUnifiedV75Builder
{
    public const string ScenePath="Assets/C01ShipV75/Scenes/C01_Ship_Multideck_v75.unity";
    public const string MasterPath="Assets/C01ShipV75/Prefabs/C01_SHIP_MASTER_V75.prefab";
    [Serializable] class Pair { public string upper,owner; }
    [Serializable] class Plan { public Pair[] mapping; }
    [Serializable] class Platforms { public string[] removed;public PlacementDataV5[] added;public GateDataV5[] gates; }


    static void AddPlatforms(GameObject master,ShipExplorerV5 explorer)
    {
        var p=JsonUtility.FromJson<Platforms>(File.ReadAllText("Assets/C01ShipV75/Data/platforms.json"));
        if(p==null||p.removed.Length!=6||p.gates.Length!=6)throw new Exception("Invalid platforms");
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true).ToDictionary(m=>m.placementId);
        foreach(var id in p.removed)
        {
            if(!markers.TryGetValue(id,out var wall)||wall.modelId!="W3_H3000")throw new Exception("Missing upper opening "+id);
            UnityEngine.Object.DestroyImmediate(wall.gameObject);
        }
        var added=new Dictionary<string,ShipInstanceV5>();
        foreach(var item in p.added)
        {
            var directory=item.model.StartsWith("G_V74_")?"Assets/C01ShipV74/Prefabs/Modules/":item.model.StartsWith("W3_H")?"Assets/C01ShipV71/Prefabs/Modules/":"Assets/C01ShipV68/Prefabs/Modules/";
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(directory+item.model+".prefab");if(prefab==null)throw new Exception("Missing module "+item.model);
            var group=master.transform.Find(item.category);
            if(group==null){var go=new GameObject(item.category);group=go.transform;group.SetParent(master.transform,false);}
            var obj=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group);obj.name=item.id;
            obj.transform.SetPositionAndRotation(new Vector3(item.x,item.y,item.z),Quaternion.Euler(0,item.yaw,0));obj.transform.localScale=Vector3.one;
            var marker=obj.AddComponent<ShipInstanceV5>();marker.placementId=item.id;marker.modelId=item.model;marker.category=item.category;marker.zoneId=item.zone;marker.deck=item.deck;added[item.id]=marker;
        }
        var gateRoot=master.transform.Find("GateControllers");if(gateRoot==null)throw new Exception("Gate controllers missing");
        var gates=new Dictionary<string,ShipGateV5>();
        foreach(var g in p.gates)
        {
            var obj=new GameObject(g.id);obj.transform.SetParent(gateRoot,false);obj.transform.SetPositionAndRotation(new Vector3(g.x,g.y,g.z),Quaternion.Euler(0,g.yaw,0));
            var gate=obj.AddComponent<ShipGateV5>();gate.id=g.id;gate.leaves=g.leaves.Select(id=>added[id].transform).ToArray();
            gate.travel=g.leaves.Select(id=>{var v=p.added.Single(i=>i.id==id).travel;return new Vector3(v[0],v[1],v[2]);}).ToArray();
            gate.SetImmediate(1);gates[g.id]=gate;
        }
        var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");var buttons=new List<ShipButtonV5>();
        foreach(var item in p.added.Where(i=>!string.IsNullOrEmpty(i.buttonGate)))
        {
            var button=added[item.id].gameObject.AddComponent<ShipButtonV5>();button.gateId=item.buttonGate;button.gate=gates[item.buttonGate];button.floor=item.buttonFloor;
            var sign=new GameObject("Button_Label");sign.transform.SetParent(button.transform,false);sign.transform.localPosition=new Vector3(.11f,.14f,.112f);sign.transform.localRotation=Quaternion.Euler(0,180,0);
            var text=sign.AddComponent<TextMesh>();text.font=font;text.fontSize=40;text.characterSize=.02f;text.anchor=TextAnchor.MiddleCenter;text.text="BRAMA";text.color=Color.white;sign.GetComponent<MeshRenderer>().sharedMaterial=font.material;buttons.Add(button);
        }
        explorer.gates=explorer.gates.Concat(gates.Values).ToArray();explorer.buttons=explorer.buttons.Concat(buttons).ToArray();
    }

    [MenuItem("Tools/C01 Ship v7.5/Unify two-level sectors")]
    public static void Build()
    {
        if(EditorApplication.isPlayingOrWillChangePlaymode)throw new Exception("Stop play mode first");
        var plan=JsonUtility.FromJson<Plan>(File.ReadAllText("Assets/C01ShipV75/Data/sectors.json"));
        if(plan==null||plan.mapping==null||plan.mapping.Length!=6)throw new Exception("Invalid sector mapping");
        Directory.CreateDirectory("Assets/C01ShipV75/Scenes");Directory.CreateDirectory("Assets/C01ShipV75/Prefabs");
        var scene=EditorSceneManager.OpenScene("Assets/C01ShipV74/Scenes/C01_Ship_Multideck_v74.unity",OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null||explorer.master==null)throw new Exception("Missing master");
        var master=explorer.master;
        int layers=0;
        while(PrefabUtility.IsPartOfPrefabInstance(master))
        {
            if(++layers>20)throw new Exception("Cannot unpack inherited master prefab layers");
            PrefabUtility.UnpackPrefabInstance(master,PrefabUnpackMode.OutermostRoot,InteractionMode.AutomatedAction);
        }
        var signage=master.GetComponent("ButtonSignage") as Behaviour;if(signage!=null)signage.enabled=false;
        AddPlatforms(master,explorer);
        var zones=master.GetComponentsInChildren<ShipZoneV5>(true).ToDictionary(z=>z.zoneId);
        var markers=master.GetComponentsInChildren<ShipInstanceV5>(true);int moved=0;
        foreach(var pair in plan.mapping)
        {
            if(!zones.TryGetValue(pair.owner,out var owner)||!zones.TryGetValue(pair.upper,out var upper))throw new Exception("Missing paired zones "+pair.owner+" "+pair.upper);
            if(owner.deck!=1||Math.Abs(owner.height-6)>.001f||upper.deck!=2)throw new Exception("Unexpected zone height");
            owner.spansDecks=true;
            var contents=new GameObject("Moduly_Poziom_1_i_2");contents.transform.SetParent(owner.transform,false);
            foreach(var marker in markers.Where(m=>m.zoneId==pair.owner||m.zoneId==pair.upper))
            {
                marker.transform.SetParent(contents.transform,true);
                if(marker.transform.parent!=contents.transform)throw new Exception("Could not move module "+marker.placementId);
                marker.zoneId=pair.owner;moved++;
            }
            UnityEngine.Object.DestroyImmediate(upper.gameObject);
        }
        if(signage!=null)signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)throw new Exception("Could not save master");
        EditorSceneManager.MarkSceneDirty(scene);if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();Debug.Log("C01 V7.5 unified sectors="+plan.mapping.Length+" modules="+moved);
    }
}
