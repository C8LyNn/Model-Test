using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipV62Diagnostics
{
    static readonly string Output=Path.GetFullPath("C01ShipV62_QA/Screenshots");
    static Camera camera;
    static RenderTexture target;
    static void Shot(string name,Vector3 position,Vector3 look)
    {
        camera.transform.position=position;
        camera.transform.rotation=Quaternion.LookRotation(look-position,Vector3.up);
        camera.Render();RenderTexture.active=target;
        var texture=new Texture2D(1280,720,TextureFormat.RGB24,false);
        texture.ReadPixels(new Rect(0,0,1280,720),0,0);texture.Apply();
        File.WriteAllBytes(Path.Combine(Output,name+".png"),texture.EncodeToPNG());
        UnityEngine.Object.DestroyImmediate(texture);
    }
    static ShipExplorerV5 Open(string path)
    {
        EditorSceneManager.OpenScene(path);
        var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if(explorer==null) throw new Exception("Explorer missing");
        explorer.SetWalking(true);
        var signs=explorer.master.GetComponent<ButtonSignage>();if(signs!=null)signs.Synchronize();
        return explorer;
    }
    public static void Capture()
    {
        Directory.CreateDirectory(Output);
        Open("Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity");
        camera=new GameObject("C01 QA camera").AddComponent<Camera>();camera.fieldOfView=65;camera.nearClipPlane=.05f;camera.farClipPlane=500;
        target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=target;
        Shot("seams_before",new Vector3(49.5f,3,73.5f),new Vector3(42,3,73.5f));
        camera.targetTexture=null;RenderTexture.active=null;
        UnityEngine.Object.DestroyImmediate(camera.gameObject);UnityEngine.Object.DestroyImmediate(target);
        var explorer=Open(ShipV62Builder.ScenePath);
        camera=new GameObject("C01 QA camera").AddComponent<Camera>();camera.fieldOfView=65;camera.nearClipPlane=.05f;camera.farClipPlane=500;
        target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=target;
        Shot("seams_after",new Vector3(49.5f,3,73.5f),new Vector3(42,3,73.5f));
        Shot("bridge",new Vector3(-15,2.7f,45),new Vector3(-31,1.7f,45));
        var lift=explorer.lifts.First(l=>l.id=="BRIDGE_PASSENGER");lift.ResetToFloor(1);lift.landings[1].SetImmediate(1);
        Shot("lift_entrance",new Vector3(-14.5f,1.65f,25.5f),new Vector3(-10.5f,1.65f,25.5f));
        Shot("lift_interior",new Vector3(-10.4f,1.55f,25.5f),new Vector3(-9.3f,2.3f,26.3f));
        camera.targetTexture=null;RenderTexture.active=null;
        UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(camera.gameObject);
        Debug.Log("C01 V6.2 VISUAL QA COMPLETE");
    }

    [Serializable] class ModelCheck { public string name; public Vector3 expected,actual; public bool matches; }
    [Serializable] class ModelReport { public string status; public ModelCheck[] models; }
    static Bounds GeometryBounds(GameObject root)
    {
        bool has=false;var bounds=new Bounds();
        foreach(var filter in root.GetComponentsInChildren<MeshFilter>(true))
        {
            if(filter.sharedMesh==null) continue;
            foreach(var vertex in filter.sharedMesh.vertices)
            {
                var p=filter.transform.TransformPoint(vertex);
                if(!has){bounds=new Bounds(p,Vector3.zero);has=true;}else bounds.Encapsulate(p);
            }
        }
        if(!has) throw new Exception("No vertices in "+root.name);
        return bounds;
    }
    public static void VerifyModels()
    {
        var results=new System.Collections.Generic.List<ModelCheck>();
        foreach(var path in Directory.GetFiles("Assets/C01ShipV62/Models","*.fbx").OrderBy(x=>x))
        {
            var name=Path.GetFileNameWithoutExtension(path);
            var source=AssetDatabase.LoadAssetAtPath<GameObject>(path.Replace('\\','/'));
            if(source==null) throw new Exception("FBX not imported: "+path);
            var instance=UnityEngine.Object.Instantiate(source);
            var actual=GeometryBounds(instance).size;UnityEngine.Object.DestroyImmediate(instance);
            Vector3 expected;
            if(name.StartsWith("wall_"))
            {
                var mesh=AssetDatabase.LoadAssetAtPath<Mesh>("Assets/C01ShipV62/Meshes/"+name+".asset");
                if(mesh==null) throw new Exception("Missing reference wall "+name);
                expected=mesh.bounds.size;
            }
            else
            {
                var original=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01ShipV62/Prefabs/Modules/"+name+".prefab");
                if(original==null) throw new Exception("Missing reference module "+name);
                var o=UnityEngine.Object.Instantiate(original);expected=GeometryBounds(o).size;UnityEngine.Object.DestroyImmediate(o);
            }
            results.Add(new ModelCheck{name=name,expected=expected,actual=actual,matches=Vector3.Distance(expected,actual)<.005f});
        }
        var report=new ModelReport{status=results.Count==18&&results.All(x=>x.matches)?"PASS":"FAIL",models=results.ToArray()};
        Directory.CreateDirectory("C01ShipV62_QA");File.WriteAllText("C01ShipV62_QA/unity_fbx_import.json",JsonUtility.ToJson(report,true));
        Debug.Log("C01 V6.2 UNITY FBX IMPORT "+report.status+" count="+results.Count);
        if(report.status!="PASS") throw new Exception("FBX dimensions do not match native modules; see QA report");
    }
    public static void CaptureAndVerify() { Capture(); VerifyModels(); }

    [Serializable] class ProbeHit { public string name,category,owner; public float distance; public Vector3 position,size; }
    [Serializable] class GateProbe { public string scene,id;public float openness;public int leaves,activeLeaves; public ProbeHit[] visibleBounds; }
    static GateProbe Probe(ShipExplorerV5 explorer,string tag)
    {
        var gate=explorer.gates.First(g=>g!=null&&g.id=="G_L1_GYM_L1_LAB");
        var ray=new Ray(new Vector3(49.5f,3f,73.5f),Vector3.left);
        var hits=new System.Collections.Generic.List<ProbeHit>();
        foreach(var renderer in explorer.master.GetComponentsInChildren<Renderer>(true))
        {
            if(!renderer.enabled||!renderer.gameObject.activeInHierarchy||!renderer.bounds.IntersectRay(ray,out var distance)||distance>30)continue;
            var owner=renderer.GetComponentInParent<ShipInstanceV5>();
            hits.Add(new ProbeHit{name=renderer.name,owner=owner!=null?owner.placementId:"",category=owner!=null?owner.category:"",distance=distance,position=renderer.bounds.center,size=renderer.bounds.size});
        }
        int active=gate.leaves.Count(t=>t!=null && t.GetComponentsInChildren<Renderer>(true).Any(r=>r.enabled&&r.gameObject.activeInHierarchy));
        return new GateProbe{scene=tag,id=gate.id,openness=gate.openness,leaves=gate.leaves.Length,activeLeaves=active,visibleBounds=hits.OrderBy(h=>h.distance).Take(20).ToArray()};
    }
    public static void ProbeGate()
    {
        Directory.CreateDirectory(Output);
        var old=Open("Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity");
        var before=Probe(old,"v61");
        camera=new GameObject("C01 QA camera").AddComponent<Camera>();camera.fieldOfView=65;camera.nearClipPlane=.05f;camera.farClipPlane=500;
        target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=target;
        Shot("gate_before",new Vector3(49.5f,3f,73.5f),new Vector3(42,3f,73.5f));
        camera.targetTexture=null;RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(camera.gameObject);
        var current=Open(ShipV62Builder.ScenePath);var after=Probe(current,"v62");
        camera=new GameObject("C01 QA camera").AddComponent<Camera>();camera.fieldOfView=65;camera.nearClipPlane=.05f;camera.farClipPlane=500;
        target=new RenderTexture(1280,720,24,RenderTextureFormat.ARGB32);camera.targetTexture=target;
        Shot("gate_after",new Vector3(49.5f,3f,73.5f),new Vector3(42,3f,73.5f));
        File.WriteAllText("C01ShipV62_QA/gate_before.json",JsonUtility.ToJson(before,true));
        File.WriteAllText("C01ShipV62_QA/gate_after.json",JsonUtility.ToJson(after,true));
        camera.targetTexture=null;RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(camera.gameObject);
        Debug.Log("C01 V6.2 GATE PROBE COMPLETE");
    }
}
