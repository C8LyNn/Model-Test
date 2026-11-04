using System;
using System.IO;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipSurfaceV70Delivery
{
    const string QA="C01ShipV70_QA";
    public static void CaptureAndExport()
    {
        Directory.CreateDirectory(QA+"/Screenshots");
        Capture("Assets/C01ShipV69/Scenes/C01_Ship_Multideck_v69.unity","before");
        Capture(ShipSurfaceV70Builder.ScenePath,"after");
        var path=Path.GetFullPath(QA+"/C01_Ship_Multideck_v7.0.unitypackage");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV70","Assets/C01ShipV69","Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},path,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(path)||new FileInfo(path).Length<1024)throw new IOException("Package export failed");
    }
    static void Capture(string scene,string tag)
    {
        EditorSceneManager.OpenScene(scene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null)throw new Exception("Explorer missing");
        explorer.SetWalking(true);var signage=explorer.master.GetComponent<ButtonSignage>();if(signage!=null)signage.Synchronize();
        var cam=new GameObject("SurfaceCapture").AddComponent<Camera>();cam.enabled=false;cam.clearFlags=CameraClearFlags.SolidColor;
        cam.backgroundColor=new Color(.025f,.04f,.06f);cam.nearClipPlane=.05f;cam.farClipPlane=600;cam.fieldOfView=70;
        Shot(cam,new Vector3(28.5f,2.4f,63),new Vector3(28.5f,3.0f,54),QA+"/Screenshots/sector_"+tag+".png");
        Shot(cam,new Vector3(-10.5f,2.0f,38),new Vector3(-10.5f,3.3f,33),QA+"/Screenshots/lift_wall_"+tag+".png");
        Shot(cam,new Vector3(61.5f,8.7f,59),new Vector3(61.5f,6.4f,52),QA+"/Screenshots/roof_"+tag+".png");
        UnityEngine.Object.DestroyImmediate(cam.gameObject);
    }
    static void Shot(Camera cam,Vector3 from,Vector3 to,string path)
    {
        cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(to-from,Vector3.up));
        var old=RenderTexture.active;var rt=new RenderTexture(1280,720,24);cam.targetTexture=rt;
        try{cam.Render();cam.Render();RenderTexture.active=rt;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();File.WriteAllBytes(path,tex.EncodeToPNG());UnityEngine.Object.DestroyImmediate(tex);}
        finally{cam.targetTexture=null;RenderTexture.active=old;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
    }
}
