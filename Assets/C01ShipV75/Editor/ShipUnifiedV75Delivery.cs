using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipUnifiedV75Delivery
{
    const string QA="C01ShipV75_QA";
    public static void CaptureAndExport()
    {
        Directory.CreateDirectory(QA+"/Screenshots");
        Capture("Assets/C01ShipV74/Scenes/C01_Ship_Multideck_v74.unity","before");
        Capture(ShipUnifiedV75Builder.ScenePath,"after");
        var path=Path.GetFullPath(QA+"/C01_Ship_Multideck_v7.5.unitypackage");
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV75","Assets/C01ShipV74","Assets/C01ShipV73","Assets/C01ShipV72","Assets/C01ShipV71","Assets/C01ShipV70","Assets/C01ShipV69","Assets/C01ShipV68","Assets/C01ShipV5/Runtime","Assets/C01ShipV6/Cargo/Runtime","Assets/C01ShipV61/Signage"},path,ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        if(!File.Exists(path)||new FileInfo(path).Length<1024)throw new IOException("Package export failed");
    }
    static void Capture(string scene,string tag)
    {
        EditorSceneManager.OpenScene(scene,OpenSceneMode.Single);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();if(explorer==null)throw new Exception("Explorer missing");
        if(tag=="after")
        {
            var sectorModules=explorer.master.GetComponentsInChildren<ShipZoneV5>(true).Where(z=>z.spansDecks).SelectMany(z=>z.GetComponentsInChildren<ShipInstanceV5>(true)).ToArray();
            var linked=sectorModules.Count(m=>{var nearest=PrefabUtility.GetNearestPrefabInstanceRoot(m.gameObject);return nearest!=null&&nearest!=explorer.master;});
            Debug.Log("C01 V7.5 sector modules="+sectorModules.Length+" prefab-linked="+linked);
            if(sectorModules.Length<1000||linked<1000)throw new Exception("Sector modules lost prefab links");
        }
        explorer.SetWalking(true);var signage=explorer.master.GetComponent<ButtonSignage>();if(signage!=null)signage.Synchronize();
        var cam=new GameObject("UnifiedCapture").AddComponent<Camera>();cam.enabled=false;cam.clearFlags=CameraClearFlags.SolidColor;
        cam.backgroundColor=new Color(.025f,.04f,.06f);cam.nearClipPlane=.05f;cam.farClipPlane=600;cam.fieldOfView=70;
        Shot(cam,new Vector3(53,5,55.5f),new Vector3(73,4.5f,55.5f),QA+"/Screenshots/lab_upper_"+tag+".png");
        Shot(cam,new Vector3(11,5,31.5f),new Vector3(31,4.5f,31.5f),QA+"/Screenshots/tech_upper_"+tag+".png");
        Shot(cam,new Vector3(95,5,31.5f),new Vector3(115,4.5f,31.5f),QA+"/Screenshots/cargo_upper_"+tag+".png");
        Shot(cam,new Vector3(57,1.8f,62),new Vector3(58,4.3f,54.5f),QA+"/Screenshots/lab_lower_"+tag+".png");
        explorer.SetWalking(false);explorer.SetDeck(2);cam.orthographic=true;cam.orthographicSize=60;
        Shot(cam,new Vector3(63,90,43.5f),new Vector3(63,0,43.5f),QA+"/Screenshots/deck2_"+tag+".png");
        UnityEngine.Object.DestroyImmediate(cam.gameObject);
    }
    static void Shot(Camera cam,Vector3 from,Vector3 to,string path)
    {
        cam.transform.SetPositionAndRotation(from,Quaternion.LookRotation(to-from,Vector3.forward));
        if(Mathf.Abs(Vector3.Dot((to-from).normalized,Vector3.up))<.99f)cam.transform.rotation=Quaternion.LookRotation(to-from,Vector3.up);
        var old=RenderTexture.active;var rt=new RenderTexture(1280,720,24);cam.targetTexture=rt;
        try{cam.Render();cam.Render();RenderTexture.active=rt;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();File.WriteAllBytes(path,tex.EncodeToPNG());UnityEngine.Object.DestroyImmediate(tex);}
        finally{cam.targetTexture=null;RenderTexture.active=old;rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
    }
}
