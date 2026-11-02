using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Profiling;
using C01.Ship.V5;
using Debug=UnityEngine.Debug;

public static class ShipV61Diagnostics
{
    const string V6Scene="Assets/C01ShipV6/Scenes/C01_Ship_Multideck_v6.unity";
    static string Output=>Path.GetFullPath(Path.Combine(Application.dataPath,"../C01ShipV61_QA"));

    [Serializable] class Report
    {
        public string unity,gpu,scene;
        public int renderers,colliders,lights;
        public double[] walkingToOverviewMs,overviewToWalkingMs,deckSwitchMs;
        public long[] walkingToOverviewManagedBytes,overviewToWalkingManagedBytes,deckSwitchManagedBytes;
        public View[] views;
    }
    [Serializable] class View { public string name; public double[] renderReadbackMs; public long drawCalls; }

    public static void Baseline() { Capture(V6Scene,"baseline"); }
    public static void After() { Capture("Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity","after"); }

    public static void Capture(string scene,string tag)
    {
        Directory.CreateDirectory(Output);
        var imageDir=Path.Combine(Output,tag);
        Directory.CreateDirectory(imageDir);
        EditorSceneManager.OpenScene(scene);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null) throw new Exception("Explorer missing");
        explorer.SetWalking(true);
        var report=new Report {unity=Application.unityVersion,gpu=SystemInfo.graphicsDeviceName,scene=scene,
            renderers=explorer.master.GetComponentsInChildren<Renderer>(true).Length,
            colliders=explorer.master.GetComponentsInChildren<Collider>(true).Length,
            lights=UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None).Length,
            walkingToOverviewMs=new double[4],overviewToWalkingMs=new double[4],deckSwitchMs=new double[4],
            walkingToOverviewManagedBytes=new long[4],overviewToWalkingManagedBytes=new long[4],deckSwitchManagedBytes=new long[4]};
        // Use the exact public paths used by the in-game mode and floor controls.
        for(int i=0;i<4;i++)
        {
            long b=GC.GetAllocatedBytesForCurrentThread();var sw=Stopwatch.StartNew();explorer.SetWalking(false);sw.Stop();
            report.walkingToOverviewMs[i]=sw.Elapsed.TotalMilliseconds;report.walkingToOverviewManagedBytes[i]=GC.GetAllocatedBytesForCurrentThread()-b;
            b=GC.GetAllocatedBytesForCurrentThread();sw.Restart();explorer.SetDeck(i%3);sw.Stop();
            report.deckSwitchMs[i]=sw.Elapsed.TotalMilliseconds;report.deckSwitchManagedBytes[i]=GC.GetAllocatedBytesForCurrentThread()-b;
            b=GC.GetAllocatedBytesForCurrentThread();sw.Restart();explorer.SetWalking(true);sw.Stop();
            report.overviewToWalkingMs[i]=sw.Elapsed.TotalMilliseconds;report.overviewToWalkingManagedBytes[i]=GC.GetAllocatedBytesForCurrentThread()-b;
        }
        var signage=UnityEngine.Object.FindFirstObjectByType<C01.Ship.V61.Signage.ButtonSignage>();
        if(signage!=null) signage.Synchronize();
        var cam=new GameObject("C01_QA_CAMERA").AddComponent<Camera>();
        cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.025f,.04f,.06f);
        cam.nearClipPlane=.05f;cam.farClipPlane=500;cam.fieldOfView=65;
        var target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);
        cam.targetTexture=target;
        var examples=new[]{
            (name:"corridor",position:new Vector3(10.5f,1.65f,43.5f),look:new Vector3(30,1.55f,43.5f)),
            (name:"cabin",position:new Vector3(7.4f,1.65f,48.5f),look:new Vector3(2.5f,1.3f,48.5f)),
            (name:"gym",position:new Vector3(19,1.65f,65),look:new Vector3(7,1.5f,58)),
            (name:"medical",position:new Vector3(104,1.65f,65),look:new Vector3(90,1.4f,57)),
            (name:"bridge",position:new Vector3(-5,1.65f,45),look:new Vector3(-15,1.4f,45))}.ToList();
        var button=explorer.buttons.FirstOrDefault(b=>b!=null && b.transform.Find("Button_Label")!=null);
        if(button!=null)
        {
            var center=button.transform.TransformPoint(new Vector3(.11f,.14f,.105f));
            var screen=button.GetComponentsInChildren<ShipSolidV5>(true).FirstOrDefault(p=>p.role=="SCREEN");
            var text=screen!=null?screen.transform.Find("Button_Label_V61"):null;
            if(text!=null) Debug.Log("C01 LABEL CHECK "+button.name+" enabled="+text.GetComponent<Renderer>().enabled+" bounds="+text.GetComponent<Renderer>().localBounds+" scale="+text.localScale+" pos="+text.position+" material="+text.GetComponent<Renderer>().sharedMaterial.name);
            examples.Add(("button_front",center+button.transform.forward*.55f,center));
            examples.Add(("button_back",center-button.transform.forward*.55f,center));
        }
        var views=new System.Collections.Generic.List<View>();
        foreach(var example in examples)
        {
            cam.transform.position=example.position;
            cam.transform.rotation=Quaternion.LookRotation(example.look-example.position,Vector3.up);
            cam.Render();
            var v=new View{name=example.name,renderReadbackMs=new double[4],drawCalls=-1};
            for(int i=0;i<v.renderReadbackMs.Length;i++)
            {
                var timer=Stopwatch.StartNew();
                cam.Render();
                RenderTexture.active=target;
                var image=new Texture2D(1280,720,TextureFormat.RGB24,false);
                image.ReadPixels(new Rect(0,0,1280,720),0,0);image.Apply();
                timer.Stop();v.renderReadbackMs[i]=timer.Elapsed.TotalMilliseconds;
                if(i==v.renderReadbackMs.Length-1) File.WriteAllBytes(Path.Combine(imageDir,example.name+".png"),image.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(image);
            }
            views.Add(v);
        }
        report.views=views.ToArray();
        cam.targetTexture=null;RenderTexture.active=null;
        UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(cam.gameObject);
        File.WriteAllText(Path.Combine(Output,tag+".json"),JsonUtility.ToJson(report,true));
        Debug.Log("C01 POLISH DIAGNOSTICS "+tag+" COMPLETE");
    }
}
