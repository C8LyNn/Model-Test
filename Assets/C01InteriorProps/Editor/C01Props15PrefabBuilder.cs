#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public static class C01Props15PrefabBuilder {
    const string Root = "Assets/C01InteriorProps/P15";
    const string Models = Root + "/Models/FBX/";
    const string Prefabs = Root + "/Prefabs/";
    const string QA = Root + "/QA/";
    static readonly Dictionary<string,Color> Palette = new Dictionary<string,Color> {
        {"STEEL",new Color(.44f,.52f,.58f,1)}, {"DARK",new Color(.10f,.14f,.18f,1)},
        {"WARN",new Color(.90f,.55f,.14f,1)}
    };
    static readonly Dictionary<string,Material> Mats = new Dictionary<string,Material>();
    static Material MaterialFor(string key) {
        if(Mats.ContainsKey(key)) return Mats[key];
        string path=Root+"/Materials/C01_P15_"+key+".mat";
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(m==null) {
            var shader=Shader.Find("Universal Render Pipeline/Lit");
            if(shader==null) throw new Exception("URP/Lit shader missing");
            m=new Material(shader);m.name="C01_P15_"+key;
            m.SetColor("_BaseColor",Palette[key]);m.SetFloat("_Smoothness",.35f);
            AssetDatabase.CreateAsset(m,path);
        }
        Mats[key]=m;return m;
    }
    static void Attach(GameObject parent,string name,string file) {
        var source=AssetDatabase.LoadAssetAtPath<GameObject>(Models+file);
        if(source==null) throw new FileNotFoundException("FBX missing",Models+file);
        var obj=(GameObject)PrefabUtility.InstantiatePrefab(source);
        obj.name=name;obj.transform.SetParent(parent.transform,false);
        obj.transform.localPosition=Vector3.zero;obj.transform.localRotation=Quaternion.identity;
        obj.transform.localScale=Vector3.one;
        foreach(var renderer in obj.GetComponentsInChildren<Renderer>(true)) {
            var original=renderer.sharedMaterials;
            var replacement=new Material[original.Length];
            for(int i=0;i<original.Length;i++) {
                string n=original[i]!=null?original[i].name.ToUpperInvariant():"STEEL";
                replacement[i]=MaterialFor(n.Contains("WARN")?"WARN":n.Contains("DARK")?"DARK":"STEEL");
            }
            renderer.sharedMaterials=replacement;
        }
    }
    static void Box(GameObject parent,Vector3 center,Vector3 dimensions) {
        var c=parent.AddComponent<BoxCollider>();c.center=center;c.size=dimensions;
    }
    static void Save(GameObject go,string name) {
        PrefabUtility.SaveAsPrefabAsset(go,Prefabs+name+".prefab");
        UnityEngine.Object.DestroyImmediate(go);
    }
    [MenuItem("Tools/C01 Props15/Build FBX prefab set")]
    public static void Build() {
        Directory.CreateDirectory(Prefabs);
        Directory.CreateDirectory(QA);
        Directory.CreateDirectory(Root+"/Materials");
        AssetDatabase.Refresh();
        foreach(var key in Palette.Keys) MaterialFor(key);
        try {
            var p=new GameObject("P15-01_Pipe");
            Attach(p,"FBX_P15-01","P15-01.fbx");
            Box(p,new Vector3(.5f,0,.07f),new Vector3(1,.14f,.14f));
            Save(p,"P15-01_Pipe");

            var g=new GameObject("P15-02_Grille");
            Attach(g,"FBX_P15-02","P15-02.fbx");
            Box(g,new Vector3(0,0,.04f),new Vector3(.6f,.4f,.08f));
            Save(g,"P15-02_Grille");

            var c=new GameObject("P15-03_Cabinet");
            Attach(c,"FBX_P15-03_Body","P15-03_Body.fbx");
            Box(c,new Vector3(0,.9f,-.1625f),new Vector3(.8f,1.8f,.025f));
            Box(c,new Vector3(-.3875f,.9f,-.0175f),new Vector3(.025f,1.8f,.29f));
            Box(c,new Vector3(.3875f,.9f,-.0175f),new Vector3(.025f,1.8f,.29f));
            Box(c,new Vector3(0,.0225f,-.0175f),new Vector3(.75f,.045f,.29f));
            Box(c,new Vector3(0,1.7775f,-.0175f),new Vector3(.75f,.045f,.29f));
            var hinge=new GameObject("Door_Hinge_Y");
            hinge.transform.SetParent(c.transform,false);
            hinge.transform.localPosition=new Vector3(-.352f,0,.138f);
            Attach(hinge,"FBX_P15-03_Door","P15-03_Door.fbx");
            Box(hinge,new Vector3(.35f,.9f,0),new Vector3(.70f,1.59f,.04f));
            Save(c,"P15-03_Cabinet");
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            foreach(string name in new[]{"P15-01_Pipe","P15-02_Grille","P15-03_Cabinet"}) {
                var asset=AssetDatabase.LoadAssetAtPath<GameObject>(Prefabs+name+".prefab");
                if(asset==null || asset.transform.localScale!=Vector3.one)
                    throw new Exception("Prefab missing / root scale not 1: "+name);
            }
            File.WriteAllText(QA+"unity_editor_execution.txt",
                "Unity "+Application.unityVersion+" | Prefabs P15-01 P15-02 P15-03 generated, independent QA pending\n");
            Debug.Log("C01-15 prefab generation completed; verify material import and clearances in scene.");
        } catch(Exception e) {Debug.LogError("C01-15 FBX/prefab build FAILED: "+e);throw;}
    }
}
#endif
