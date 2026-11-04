using System;
using System.IO;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipBridgeV71Delivery
{
    const string QA="C01ShipV71_QA";
    public static void CaptureAndExport()
    {
        Directory.CreateDirectory(QA+"/Screenshots");
        Capture("Assets/C01ShipV70/Scenes/C01_Ship_Multideck_v70.unity","before");
        Capture(ShipBridgeV71Builder.ScenePath,"after");
        var package=Path.GetFullPath(QA+"/C01_Ship_Multideck_v7.1.unitypackage");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV71","Assets/C01ShipV70","Assets/C01ShipV69",
            "Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime",
            "Assets/C01ShipV61/Signage"},package,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(package)||new FileInfo(package).Length<1024)throw new IOException("Unity package export failed");
    }
    static void Capture(string scene,string tag)
    {
        EditorSceneManager.OpenScene(scene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null)throw new Exception("Missing explorer");
        explorer.SetWalking(true);var signage=explorer.master.GetComponent<ButtonSignage>();if(signage!=null)signage.Synchronize();
        var camera=new GameObject("BridgeCapture").AddComponent<Camera>();camera.enabled=false;
        camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.04f,.06f);
        camera.nearClipPlane=.05f;camera.farClipPlane=300;camera.fieldOfView=70;
        Shot(camera,new Vector3(-14,2f,43.5f),new Vector3(-34,1.3f,43.5f),QA+"/Screenshots/bridge_entry_"+tag+".png");
        Shot(camera,new Vector3(-13.5f,1.8f,27),new Vector3(-10.5f,1.3f,22.5f),QA+"/Screenshots/lift_edge_"+tag+".png");
        explorer.SetWalking(false);explorer.SetDeck(1);camera.orthographic=true;camera.orthographicSize=32;
        Shot(camera,new Vector3(-24,32,43.5f),new Vector3(-24,0,43.5f),QA+"/Screenshots/bridge_plan_"+tag+".png");
        UnityEngine.Object.DestroyImmediate(camera.gameObject);
    }
    static void Shot(Camera camera,Vector3 pos,Vector3 target,string path)
    {
        camera.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(target-pos,Vector3.forward));
        if(Mathf.Abs(Vector3.Dot((target-pos).normalized,Vector3.up))<.99f)
            camera.transform.rotation=Quaternion.LookRotation(target-pos,Vector3.up);
        var old=RenderTexture.active;var rt=new RenderTexture(1280,720,24);camera.targetTexture=rt;
        try{camera.Render();camera.Render();RenderTexture.active=rt;var t=new Texture2D(1280,720,TextureFormat.RGB24,false);
            t.ReadPixels(new Rect(0,0,1280,720),0,0);t.Apply();File.WriteAllBytes(path,t.EncodeToPNG());UnityEngine.Object.DestroyImmediate(t);}
        finally{camera.targetTexture=null;RenderTexture.active=old;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
    }
}
