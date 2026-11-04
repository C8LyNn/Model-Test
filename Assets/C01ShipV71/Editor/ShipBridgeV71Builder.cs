using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipBridgeV71Builder
{
    const string Root = "Assets/C01ShipV71";
    public const string ScenePath = Root + "/Scenes/C01_Ship_Multideck_v71.unity";
    public const string MasterPath = Root + "/Prefabs/C01_SHIP_MASTER_V71.prefab";
    const string PreviousScene = "Assets/C01ShipV70/Scenes/C01_Ship_Multideck_v70.unity";
    [Serializable] class Delta { public string[] removed; public Placement[] added, changed; public Gate[] gates; public Lift[] lifts; }
    [Serializable] class Placement { public string id, model, category, zone, parent; public int deck; public float x,y,z,yaw; }
    [Serializable] class Gate { public string id; public float x,y,z,yaw; }
    [Serializable] class Lift { public string id; public float x,z; public float[] bounds; }
    [Serializable] class PreviousPolish { public string[] removedLandingButtons; }

    static GameObject Module(string id, string category, Dictionary<string, ShipInstanceV5> samples,
                             Dictionary<string, GameObject> cached)
    {
        if (cached.TryGetValue(id, out var prefab)) return prefab;
        if (category == "Walls" || category == "Nodes")
        {
            if (id.EndsWith("_V70_OneSeam") || id.EndsWith("_V70_TopSeam"))
                prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01ShipV70/Prefabs/Modules/" + id + ".prefab");
            else
            {
                if (!samples.TryGetValue(id, out var sample)) throw new Exception("No polished sample for " + id);
                var copy = UnityEngine.Object.Instantiate(sample.gameObject);
                copy.name = id;
                if (PrefabUtility.IsPartOfPrefabInstance(copy))
                    PrefabUtility.UnpackPrefabInstance(copy, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var marker = copy.GetComponent<ShipInstanceV5>();
                if (marker != null) UnityEngine.Object.DestroyImmediate(marker);
                copy.transform.SetParent(null, false);
                copy.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                copy.transform.localScale = Vector3.one;
                prefab = PrefabUtility.SaveAsPrefabAsset(copy, Root + "/Prefabs/Modules/" + id + ".prefab");
                UnityEngine.Object.DestroyImmediate(copy);
            }
        }
        else prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01ShipV68/Prefabs/Modules/" + id + ".prefab");
        if (prefab == null) throw new Exception("Missing reusable module " + id);
        cached[id] = prefab;
        return prefab;
    }

    static ShipInstanceV5 Add(Placement p, Transform parent, GameObject prefab)
    {
        var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
        go.name = p.id;
        go.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z), Quaternion.Euler(0,p.yaw,0));
        go.transform.localScale = Vector3.one;
        var marker = go.AddComponent<ShipInstanceV5>();
        marker.placementId=p.id; marker.modelId=p.model; marker.category=p.category; marker.zoneId=p.zone; marker.deck=p.deck;
        return marker;
    }

    [MenuItem("Tools/C01 Ship v7.1/Build bridge and edge lifts")]
    public static void Build()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new Exception("Stop play mode before building");
        var delta = JsonUtility.FromJson<Delta>(File.ReadAllText(Root + "/Data/bridge_delta.json"));
        var polish = JsonUtility.FromJson<PreviousPolish>(File.ReadAllText("Assets/C01ShipV68/Data/polish_v68.json"));
        if (delta == null || delta.lifts.Length != 2 || delta.gates.Length != 6) throw new Exception("Invalid bridge delta");
        foreach (string folder in new[]{"Prefabs/Modules", "Scenes"}) Directory.CreateDirectory(Root + "/" + folder);
        AssetDatabase.Refresh();
        var scene = EditorSceneManager.OpenScene(PreviousScene, OpenSceneMode.Single);
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if (explorer == null || explorer.master == null) throw new Exception("Previous master missing");
        var master = explorer.master;
        var signage = master.GetComponent<ButtonSignage>();
        if (signage != null) signage.enabled = false;
        var markers = master.GetComponentsInChildren<ShipInstanceV5>(true)
            .Where(m => !string.IsNullOrEmpty(m.placementId)).ToDictionary(m => m.placementId);
        var samples = markers.Values.Where(m=>m.category=="Walls" || m.category=="Nodes")
            .GroupBy(m=>m.modelId).ToDictionary(g=>g.Key,g=>g.First());
        var prefabs = new Dictionary<string,GameObject>();
        foreach (var p in delta.added.Where(p=>p.category=="Walls" || p.category=="Nodes"))
            Module(p.model,p.category,samples,prefabs);

        foreach (var id in delta.removed)
        {
            if (!markers.TryGetValue(id,out var marker)) throw new Exception("Missing removed module " + id);
            markers.Remove(id); UnityEngine.Object.DestroyImmediate(marker.gameObject);
        }
        foreach (var p in delta.added)
        {
            if (markers.ContainsKey(p.id)) throw new Exception("Duplicate module " + p.id);
            var parent = master.transform.Find(p.category);
            if (parent == null) throw new Exception("Missing group " + p.category);
            markers[p.id] = Add(p,parent,Module(p.model,p.category,samples,prefabs));
        }
        var intentionallyRemoved = new HashSet<string>(polish.removedLandingButtons ?? Array.Empty<string>());
        foreach (var p in delta.changed)
        {
            // Car panels and controls remain parented to the car and retain the v6.8 polish.
            if (!string.IsNullOrEmpty(p.parent)) continue;
            if (!markers.TryGetValue(p.id,out var marker))
            {
                if (intentionallyRemoved.Contains(p.id)) continue;
                throw new Exception("Missing changed module " + p.id);
            }
            if (marker.modelId != p.model)
            {
                if (p.category != "Floors") throw new Exception("Unexpected replacement " + p.id);
                var parent=marker.transform.parent;
                UnityEngine.Object.DestroyImmediate(marker.gameObject);
                markers[p.id] = Add(p,parent,Module(p.model,p.category,samples,prefabs));
            }
            else
            {
                marker.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));
                PrefabUtility.RecordPrefabInstancePropertyModifications(marker.transform);
            }
        }
        foreach (var p in delta.gates)
        {
            var gate = explorer.gates.Single(g=>g!=null && g.id==p.id);
            gate.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));
            // Closed positions were serialized in v7.0 and must be recached at their new location.
            var serial = new SerializedObject(gate);
            serial.FindProperty("cachedLeaves").ClearArray(); serial.FindProperty("closedPositions").ClearArray();
            serial.ApplyModifiedPropertiesWithoutUndo(); gate.openness=gate.target=0;
            PrefabUtility.RecordPrefabInstancePropertyModifications(gate.transform);
            PrefabUtility.RecordPrefabInstancePropertyModifications(gate);
        }
        foreach (var p in delta.lifts)
        {
            var lift=explorer.lifts.Single(l=>l!=null && l.id==p.id);
            var pos=lift.car.position; pos.x=p.x; pos.z=p.z; lift.car.position=pos;
            lift.footprint=new Vector4(p.bounds[0],p.bounds[1],p.bounds[2],p.bounds[3]);
            PrefabUtility.RecordPrefabInstancePropertyModifications(lift.car);
            PrefabUtility.RecordPrefabInstancePropertyModifications(lift);
        }
        if(signage!=null) signage.enabled=true;
        explorer.InvalidateSceneCache(); explorer.SetWalking(true); Physics.SyncTransforms();
        if(PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction)==null)
            throw new Exception("Failed to save master prefab");
        EditorSceneManager.MarkSceneDirty(scene);
        if(!EditorSceneManager.SaveScene(scene,ScenePath)) throw new Exception("Failed to save scene");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))
            EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();
        Debug.Log("C01 V7.1 bridge built: " + delta.removed.Length + " removed, " + delta.added.Length + " added, " + delta.changed.Length + " changed");
    }
}
