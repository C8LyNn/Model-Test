using System;
using System.IO;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipV68Delivery
{
    public static void CaptureAndExport()
    {
        const string qa="C01ShipV68_QA";
        Directory.CreateDirectory(qa+"/Screenshots");
        EditorSceneManager.OpenScene("Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity",OpenSceneMode.Single);
        var e=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(e==null)throw new Exception("Explorer missing");
        e.SetWalking(true);var signage=e.master.GetComponent<ButtonSignage>();if(signage!=null)signage.Synchronize();
        var camera=new GameObject("CaptureCamera").AddComponent<Camera>();camera.enabled=false;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.04f,.06f);camera.nearClipPlane=.05f;camera.farClipPlane=600;camera.fieldOfView=70;
        var viewpoints=new[]{
            ("bridge",new Vector3(-7,5.4f,51),new Vector3(-28,1,43.5f)),
            ("bridge_walk",new Vector3(-5,1.65f,43.5f),new Vector3(-32,1.5f,43.5f)),
            ("stern",new Vector3(129,5.4f,47),new Vector3(145,1,43.5f)),
            ("stern_walk",new Vector3(137,1.65f,43.5f),new Vector3(145,1.1f,49.5f)),
            ("bridge_detail",new Vector3(-20,2.2f,50),new Vector3(-30,1,43.5f)),
            ("sector_gate",new Vector3(49,1.65f,61.5f),new Vector3(42,2.9f,61.5f)),
            ("deck0_gate",new Vector3(19.5f,-1.75f,38.5f),new Vector3(19.5f,-1.0f,42))};
        foreach(var v in viewpoints){camera.transform.SetPositionAndRotation(v.Item2,Quaternion.LookRotation(v.Item3-v.Item2,Vector3.up));Capture(camera,signage,qa+"/Screenshots/"+v.Item1+".png");}
        e.SetWalking(false);e.SetDeck(1);Capture(e.view,signage,qa+"/Screenshots/deck1_overview.png");
        var package=Path.GetFullPath(qa+"/C01_Ship_Multideck_v6.8.unitypackage");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},package,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(package) || new FileInfo(package).Length < 1024) throw new IOException("Unity package export failed: no output file");
    }
    static void Capture(Camera camera,ButtonSignage signage,string path)
    {
        var old=camera.targetTexture;var active=RenderTexture.active;var rt=new RenderTexture(1280,720,24);
        try {camera.targetTexture=rt;camera.Render();if(signage!=null)signage.Synchronize();camera.Render();RenderTexture.active=rt;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();File.WriteAllBytes(path,tex.EncodeToPNG());UnityEngine.Object.DestroyImmediate(tex);}
        finally{camera.targetTexture=old;RenderTexture.active=active;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
    }
}
