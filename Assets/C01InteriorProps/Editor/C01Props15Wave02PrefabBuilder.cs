#if UNITY_EDITOR
using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

// C01-15 WAVE 02: execute from Tools/C01 Props15/WAVE02 Build & Audit,
// or -batchmode -executeMethod C01Props15Wave02PrefabBuilder.Build
public static class C01Props15Wave02PrefabBuilder
{
    const string Root="Assets/C01InteriorProps/P15Wave02";
    const string Models=Root+"/Models/FBX/";
    const string Prefabs=Root+"/Prefabs/";
    static readonly Dictionary<string,Color> Palette=new Dictionary<string,Color>{
        {"STEEL",new Color(.42f,.50f,.57f,1)},
        {"DARK",new Color(.09f,.12f,.16f,1)},
        {"WARN",new Color(.92f,.48f,.11f,1)},
        {"COOLANT",new Color(.09f,.40f,.54f,1)}
    };
    [Serializable] public class QAEntry {
        public string asset; public string prefab; public bool imported;
        public float minX,minY,minZ,maxX,maxY,maxZ;
        public int meshCount,uvMeshCount,normalMeshCount,colliderCount,materialCount;
        public bool scaleOne,boundsPass; public string sha256; public string status;
    }
    [Serializable] public class QAReport {
        public string engineVersion,runType,qaScope,independentQA;
        public List<QAEntry> entries=new List<QAEntry>(); public string status;
    }
    static readonly Dictionary<string,Material> materials=new Dictionary<string,Material>();
    static Material GetMaterial(string role) {
        if(materials.ContainsKey(role))return materials[role];
        var path=Root+"/Materials/C01_P15_W02_"+role+".mat";
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(m==null){
            var shader=Shader.Find("Universal Render Pipeline/Lit");
            if(shader==null)throw new Exception("URP Lit shader unavailable");
            m=new Material(shader);m.name="C01_P15_W02_"+role;
            m.SetColor("_BaseColor",Palette[role]);m.SetFloat("_Metallic",role=="STEEL"?.63f:.32f);
            m.SetFloat("_Smoothness",.32f);AssetDatabase.CreateAsset(m,path);
        }
        materials[role]=m;return m;
    }
    static GameObject Attach(GameObject parent,string id){
        var path=Models+id+".fbx";
        var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if(model==null)throw new FileNotFoundException("Actual FBX not imported",path);
        var instance=(GameObject)PrefabUtility.InstantiatePrefab(model);
        instance.name="FBX_"+id;instance.transform.SetParent(parent.transform,false);
        instance.transform.localPosition=Vector3.zero;
        instance.transform.localRotation=Quaternion.identity;
        instance.transform.localScale=Vector3.one;
        foreach(var mr in instance.GetComponentsInChildren<MeshRenderer>(true)){
            var old=mr.sharedMaterials;var newer=new Material[old.Length];
            for(int i=0;i<old.Length;i++){
                string name=old[i]!=null?old[i].name.ToUpperInvariant():"STEEL";
                string role=name.Contains("COOLANT")?"COOLANT":name.Contains("WARN")?"WARN":name.Contains("DARK")?"DARK":"STEEL";
                newer[i]=GetMaterial(role);
            }
            mr.sharedMaterials=newer;
        }
        return instance;
    }
    static void AddBox(GameObject root,Vector3 pos,Vector3 size){
        var col=root.AddComponent<BoxCollider>();col.center=pos;col.size=size;
    }
    static Bounds GeometryBounds(GameObject root){
        var renderers=root.GetComponentsInChildren<Renderer>(true);
        if(renderers.Length==0)throw new Exception("No real FBX renderers "+root.name);
        Bounds b=renderers[0].bounds;
        for(int i=1;i<renderers.Length;i++)b.Encapsulate(renderers[i].bounds);
        return b;
    }
    static void Verify(GameObject obj,string id,Vector3 min,Vector3 max,QAReport report) {
        var meshes=obj.GetComponentsInChildren<MeshFilter>(true);
        int uvCount=0,normalCount=0;
        foreach(var m in meshes) if(m.sharedMesh!=null){
            if(m.sharedMesh.uv!=null && m.sharedMesh.uv.Length==m.sharedMesh.vertexCount)uvCount++;
            if(m.sharedMesh.normals!=null && m.sharedMesh.normals.Length==m.sharedMesh.vertexCount)normalCount++;
        }
        var mats=new HashSet<Material>();
        foreach(var r in obj.GetComponentsInChildren<Renderer>(true))foreach(var m in r.sharedMaterials)if(m!=null)mats.Add(m);
        var bounds=GeometryBounds(obj);
        bool boundsPass=Vector3.Distance(bounds.min,min)<.055f && Vector3.Distance(bounds.max,max)<.055f;
        bool scales=true;
        foreach(var t in obj.GetComponentsInChildren<Transform>(true)){
            if(Vector3.Distance(t.localScale,Vector3.one)>.0001f){scales=false;break;}
        }
        var entry=new QAEntry{
            asset=id,prefab=Prefabs+id+".prefab",imported=true,
            minX=bounds.min.x,minY=bounds.min.y,minZ=bounds.min.z,
            maxX=bounds.max.x,maxY=bounds.max.y,maxZ=bounds.max.z,
            meshCount=meshes.Length,uvMeshCount=uvCount,normalMeshCount=normalCount,
            colliderCount=obj.GetComponentsInChildren<Collider>(true).Length,materialCount=mats.Count,
            scaleOne=scales,boundsPass=boundsPass,sha256=HashFBX(id),
            status=(boundsPass&&scales&&uvCount==meshes.Length&&normalCount==meshes.Length&&mats.Count<=4)?"PASS":"FAIL"
        };
        report.entries.Add(entry);
        if(entry.status!="PASS")throw new Exception("Unity author import QA failure "+id+" bounds:"+bounds+" UV:"+uvCount+"/"+meshes.Length);
    }
    static string HashFBX(string id){
        using(var file=File.OpenRead(Models+id+".fbx"))
        using(var sha=SHA256.Create())return BitConverter.ToString(sha.ComputeHash(file)).Replace("-","").ToLowerInvariant();
    }
    static void Save(GameObject go,string id){
        PrefabUtility.SaveAsPrefabAsset(go,Prefabs+id+".prefab");
        UnityEngine.Object.DestroyImmediate(go);
    }
    [MenuItem("Tools/C01 Props15/WAVE02 Build & Audit")]
    public static void Build(){
        Directory.CreateDirectory(Prefabs);Directory.CreateDirectory(Root+"/Materials");
        Directory.CreateDirectory(Root+"/QA");AssetDatabase.Refresh();
        foreach(var role in Palette.Keys)GetMaterial(role);
        var report=new QAReport{engineVersion=Application.unityVersion,runType="UnityEditor actual FBX asset import",
            qaScope="FBX mesh UV0 normal arrays, renderer bounds, scale, material slots, prefab authoring; physical clearance not tested",
            independentQA="NOT RUN"};
        try{
            GameObject p;
            p=new GameObject("P15-04_CeilingCableTray");
            Attach(p,"P15-04");
            AddBox(p,new Vector3(1.5f,-.09f,0),new Vector3(3,.18f,.38f));
            Verify(p,"P15-04",new Vector3(0,-.18f,-.19f),new Vector3(3,0,.19f),report);Save(p,"P15-04");
            p=new GameObject("P15-05_CableTrayElbow");
            Attach(p,"P15-05");
            // Collider follows L shape approximately; it must not fill elbow's empty diagonal corner.
            AddBox(p,new Vector3(.20f,-.09f,0),new Vector3(.40f,.18f,.38f));
            AddBox(p,new Vector3(.55f,-.09f,.29f),new Vector3(.38f,.18f,.52f));
            Verify(p,"P15-05",new Vector3(0,-.18f,-.19f),new Vector3(.74f,0,.55f),report);Save(p,"P15-05");
            p=new GameObject("P15-06_TechnicalWireHarness");
            Attach(p,"P15-06");
            AddBox(p,new Vector3(.75f,0,.116f),new Vector3(1.5f,.20f,.23f));
            Verify(p,"P15-06",new Vector3(0,-.10f,0),new Vector3(1.5f,.10f,.232f),report);Save(p,"P15-06");
            p=new GameObject("P15-07_CoolantDistributor");
            Attach(p,"P15-07");
            AddBox(p,new Vector3(0,.45f,.023f),new Vector3(1.2f,.9f,.046f));
            AddBox(p,new Vector3(0,.48f,.165f),new Vector3(.97f,.12f,.12f));
            Verify(p,"P15-07",new Vector3(-.6f,0,0),new Vector3(.6f,.9f,.3f),report);Save(p,"P15-07");
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            report.status="PASS";
        }catch(Exception e){
            report.status="FAIL";
            File.WriteAllText(Root+"/QA/unity_editor_import.json",JsonUtility.ToJson(report,true));
            Debug.LogError("C01-15 W02 prefab import FAILED "+e);
            throw;
        }
        File.WriteAllText(Root+"/QA/unity_editor_import.json",JsonUtility.ToJson(report,true));
        Debug.Log("C01-15 W02 Unity prefab generation succeeded; independent QA and in-ship clearance PENDING.");
    }
}
#endif
