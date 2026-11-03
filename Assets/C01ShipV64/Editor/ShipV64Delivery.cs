using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipV64Delivery
{
    static Camera camera;
    static RenderTexture target;
    static string QA=>Path.GetFullPath("C01ShipV64_QA");
    static void Shot(string name,Vector3 position,Vector3 look)
    {
        camera.orthographic=false;camera.fieldOfView=65;camera.transform.position=position;
        camera.transform.rotation=Quaternion.LookRotation(look-position,Vector3.up);camera.Render();
        RenderTexture.active=target;var image=new Texture2D(1280,720,TextureFormat.RGB24,false);
        image.ReadPixels(new Rect(0,0,1280,720),0,0);image.Apply();
        File.WriteAllBytes(Path.Combine(QA,"Screenshots",name+".png"),image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);
    }
    public static void Capture()
    {
        var scenes=EditorBuildSettings.scenes;
        foreach(var entry in scenes) if(entry.path=="Assets/C01ShipV64/Scenes/C01_Ship_Multideck_v64_base.unity") entry.enabled=false;
        EditorBuildSettings.scenes=scenes;
        Directory.CreateDirectory(Path.Combine(QA,"Screenshots"));
        EditorSceneManager.OpenScene("Assets/C01ShipV64/Scenes/C01_Ship_Multideck_v64.unity");
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null)throw new Exception("Explorer missing");
        explorer.SetWalking(true);var signs=explorer.master.GetComponent<ButtonSignage>();if(signs!=null)signs.Synchronize();
        camera=new GameObject("QA camera").AddComponent<Camera>();camera.nearClipPlane=.05f;camera.farClipPlane=600;
        target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=target;
        Shot("corridor_main",new Vector3(4.5f,1.65f,43.5f),new Vector3(40,1.65f,43.5f));
        Shot("corridor_branch",new Vector3(10.5f,1.65f,46),new Vector3(10.5f,1.65f,53));
        Shot("bridge",new Vector3(-15,2.7f,45),new Vector3(-31,1.7f,45));
        Shot("sector_access",new Vector3(1.8f,1.65f,59.6f),new Vector3(10,2.2f,60));
        var lift=explorer.lifts.First(x=>x.id=="BRIDGE_PASSENGER");lift.ResetToFloor(1);lift.landings[1].SetImmediate(1);
        Shot("lift",new Vector3(-14.5f,1.65f,25.5f),new Vector3(-10.5f,1.65f,25.5f));
        explorer.SetWalking(false);explorer.SetDeck(1);
        camera.orthographic=true;camera.orthographicSize=76;camera.transform.position=new Vector3(72,180,46);
        camera.transform.rotation=Quaternion.Euler(90,0,0);camera.Render();RenderTexture.active=target;
        var top=new Texture2D(1280,720,TextureFormat.RGB24,false);top.ReadPixels(new Rect(0,0,1280,720),0,0);top.Apply();
        File.WriteAllBytes(Path.Combine(QA,"Screenshots","deck_plan.png"),top.EncodeToPNG());UnityEngine.Object.DestroyImmediate(top);
        camera.targetTexture=null;RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(camera.gameObject);
        Debug.Log("C01 V6.4 VISUAL QA COMPLETE");
    }
    public static void Export()
    {
        Directory.CreateDirectory(QA);
        AssetDatabase.ExportPackage(new[]{"Assets/C01ShipV64","Assets/C01ShipV62","Assets/C01ShipV61","Assets/C01ShipV6","Assets/C01ShipV5/Runtime"},
            Path.Combine(QA,"C01_Ship_Multideck_v6.4.unitypackage"),ExportPackageOptions.Recurse|ExportPackageOptions.IncludeDependencies);
        Debug.Log("C01 V6.4 UNITY PACKAGE EXPORTED");
    }
    public static void CaptureAndExport(){Capture();Export();}
}
