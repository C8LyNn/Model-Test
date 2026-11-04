using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipBridgeV69Builder
{
    const string Root = "Assets/C01ShipV69";
    public const string ScenePath = Root + "/Scenes/C01_Ship_Multideck_v69.unity";
    public const string MasterPath = Root + "/Prefabs/C01_SHIP_MASTER_V69.prefab";
    const string PreviousScene = "Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity";
    [Serializable] class Layout { public Placement[] placements; }
    [Serializable] class Placement { public string id, model; public float x,y,z,yaw; public bool added; }

    [MenuItem("Tools/C01 Ship v6.9/Build bridge variant")]
    public static void Build()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Cannot build while playing");
        var layout=JsonUtility.FromJson<Layout>(File.ReadAllText(Root+"/Data/bridge_layout.json"));
        if (layout?.placements == null || layout.placements.Length != 19) throw new Exception("Bridge layout missing or incomplete");
        Directory.CreateDirectory(Root+"/Scenes"); Directory.CreateDirectory(Root+"/Prefabs"); AssetDatabase.Refresh();
        var scene=EditorSceneManager.OpenScene(PreviousScene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null || explorer.master==null) throw new Exception("Previous master missing");
        var master=explorer.master;
        var signage=master.GetComponent<ButtonSignage>();
        if(signage!=null) signage.enabled=false;
        var group=master.transform.Find("CoreStations");
        if(group==null) throw new Exception("Core station group missing");
        var existing=master.GetComponentsInChildren<ShipInstanceV5>(true)
            .Where(x=>!string.IsNullOrEmpty(x.placementId)).ToDictionary(x=>x.placementId);
        foreach(var p in layout.placements)
        {
            ShipInstanceV5 marker;
            if(p.added)
            {
                if(existing.ContainsKey(p.id)) throw new Exception("Already present: "+p.id);
                var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01ShipV68/Prefabs/Modules/"+p.model+".prefab");
                if(prefab==null) throw new Exception("Missing model "+p.model);
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group);
                instance.name=p.id;
                marker=instance.AddComponent<ShipInstanceV5>();
                marker.placementId=p.id;marker.modelId=p.model;marker.category="CoreStations";marker.zoneId="L1_BRIDGE";marker.deck=1;
            }
            else if(!existing.TryGetValue(p.id,out marker) || marker.modelId!=p.model)
                throw new Exception("Missing or incorrect existing station "+p.id);
            marker.transform.SetPositionAndRotation(new Vector3(p.x,p.y,p.z),Quaternion.Euler(0,p.yaw,0));
            marker.transform.localScale=Vector3.one;
            PrefabUtility.RecordPrefabInstancePropertyModifications(marker.transform);
        }
        if(signage!=null) signage.enabled=true;
        explorer.InvalidateSceneCache();explorer.SetWalking(true);
        var saved=PrefabUtility.SaveAsPrefabAssetAndConnect(master,MasterPath,InteractionMode.AutomatedAction);
        if(saved==null)throw new Exception("Could not save master variant");
        EditorSceneManager.MarkSceneDirty(scene);
        if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new Exception("Could not save scene variant");
        if(!EditorBuildSettings.scenes.Any(s=>s.path==ScenePath))
            EditorBuildSettings.scenes=EditorBuildSettings.scenes.Concat(new[]{new EditorBuildSettingsScene(ScenePath,true)}).ToArray();
        AssetDatabase.SaveAssets();
        Debug.Log("C01 V6.9 bridge variant built with "+layout.placements.Length+" stations and displays");
    }

    public static void CaptureAndExport()
    {
        const string qa="C01ShipV69_QA";
        Directory.CreateDirectory(qa+"/Screenshots");
        EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        explorer.SetWalking(true);
        var signage=explorer.master.GetComponent<ButtonSignage>();
        if(signage!=null)signage.Synchronize();
        var camera=new GameObject("BridgeCapture").AddComponent<Camera>();
        camera.enabled=false;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.04f,.06f);
        camera.nearClipPlane=.05f;camera.farClipPlane=300;camera.fieldOfView=70;
        Shot(camera,new Vector3(-14,2.0f,43.5f),new Vector3(-34,1.3f,43.5f),qa+"/Screenshots/bridge_entry.png");
        Shot(camera,new Vector3(-20,2.1f,50),new Vector3(-31,1.0f,42.5f),qa+"/Screenshots/bridge_command.png");
        explorer.SetWalking(false);explorer.SetDeck(1);camera.orthographic=true;camera.orthographicSize=16;
        Shot(camera,new Vector3(-25,20,43.5f),new Vector3(-25,0,43.5f),qa+"/Screenshots/bridge_plan.png");
        UnityEngine.Object.DestroyImmediate(camera.gameObject);
        var package=Path.GetFullPath(qa+"/C01_Ship_Multideck_v6.9.unitypackage");
        AssetDatabase.ExportPackage(new[]{Root,"Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},package,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(package)||new FileInfo(package).Length<1024)throw new IOException("Unity package export failed");
    }
    static void Shot(Camera camera,Vector3 pos,Vector3 target,string path)
    {
        camera.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos,Vector3.forward));
        if(Mathf.Abs(Vector3.Dot((target-pos).normalized,Vector3.up))<.99f)
            camera.transform.rotation=Quaternion.LookRotation(target-pos,Vector3.up);
        var old=RenderTexture.active;var rt=new RenderTexture(1280,720,24);camera.targetTexture=rt;
        try{camera.Render();camera.Render();RenderTexture.active=rt;var t=new Texture2D(1280,720,TextureFormat.RGB24,false);t.ReadPixels(new Rect(0,0,1280,720),0,0);t.Apply();File.WriteAllBytes(path,t.EncodeToPNG());UnityEngine.Object.DestroyImmediate(t);}
        finally{camera.targetTexture=null;RenderTexture.active=old;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
    }
}
