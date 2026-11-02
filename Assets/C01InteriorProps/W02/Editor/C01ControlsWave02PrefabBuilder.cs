#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
// Wave02 isolated: models from reviewed FBX only, never modify ship architecture or scenes.
public static class C01ControlsWave02PrefabBuilder
{
    const string Root="Assets/C01InteriorProps/W02";
    static readonly string[] IDs={"P17-04","P17-05","P17-06","P17-07"};
    [MenuItem("C01/Controls/Wave02/Build FBX Prefabs")]
    public static void Build()
    {
        Directory.CreateDirectory(Root+"/Prefabs");
        Directory.CreateDirectory(Root+"/Materials");
        AssetDatabase.Refresh();
        Material steel=Get("METAL",new Color(.43f,.48f,.53f),false);
        Material dark=Get("DARK",new Color(.075f,.11f,.15f),false);
        Material yellow=Get("CAUTION",new Color(.95f,.46f,.08f),false);
        Material cyan=Get("GLOW",new Color(.09f,.56f,.75f),true);
        foreach(string id in IDs)
        {
            string modelPath=Root+"/Models/"+id+".fbx";
            var asset=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            if(asset==null) throw new Exception("Missing actual imported FBX "+modelPath);
            var go=new GameObject(id+"_C01_W02");
            var model=(GameObject)PrefabUtility.InstantiatePrefab(asset);
            model.transform.SetParent(go.transform,false);
            model.transform.localPosition=Vector3.zero;
            model.transform.localRotation=Quaternion.identity;
            model.transform.localScale=Vector3.one;
            foreach(var renderer in go.GetComponentsInChildren<Renderer>(true))
            {
                var mats=renderer.sharedMaterials;
                var assigned=new Material[mats.Length];
                for(int i=0;i<mats.Length;i++)
                {
                    string m=mats[i]!=null?mats[i].name.ToUpperInvariant():"";
                    assigned[i]=m.Contains("GLOW")?cyan:m.Contains("CAUTION")?yellow:m.Contains("DARK")?dark:steel;
                }
                renderer.sharedMaterials=assigned;
            }
            var box=go.AddComponent<BoxCollider>();
            if(id=="P17-04"){box.center=new Vector3(0,.675f,0);box.size=new Vector3(2.4f,1.35f,1f);}
            if(id=="P17-05"){box.center=new Vector3(0,.75f,-.00425f);box.size=new Vector3(.85f,1.5f,.6085f);}
            if(id=="P17-06"){box.center=new Vector3(0,.36f,.11f);box.size=new Vector3(.52f,.72f,.22f);}
            if(id=="P17-07"){box.center=new Vector3(0,.41f,.12f);box.size=new Vector3(.7f,.82f,.24f);}
            if(id=="P17-06")
            {
                Transform cover=Find(model.transform,"CoverPivot");
                Transform sw=Find(model.transform,"SwitchPivot");
                if(cover==null||sw==null)throw new Exception("Missing separate CoverPivot/SwitchPivot in "+id);
                var guardCollider=cover.gameObject.AddComponent<BoxCollider>();
                guardCollider.center=new Vector3(0,-.22f,.014f);
                guardCollider.size=new Vector3(.48f,.42f,.035f);
                // Use local X rotation cover 0..95 deg; switch -25..25 deg; no gameplay scripts.
            }
            if(id=="P17-07")
            {
                Transform cartridge=Find(model.transform,"CartridgePivot");
                if(cartridge==null)throw new Exception("Missing removable CartridgePivot in "+id);
                var insertCollider=cartridge.gameObject.AddComponent<BoxCollider>();
                insertCollider.center=new Vector3(0,0,.054f);
                insertCollider.size=new Vector3(.13f,.29f,.085f);
                // Child can translate +Z 0..0.25 m; never move root wall-mounted assembly.
            }
            PrefabUtility.SaveAsPrefabAsset(go,Root+"/Prefabs/"+id+".prefab");
            UnityEngine.Object.DestroyImmediate(go);
            Debug.Log("W02 native Unity prefab generated for "+id);
        }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Validate();
    }
    static Transform Find(Transform root,string name)
    {
        if(root.name.Contains(name))return root;
        foreach(Transform c in root){var value=Find(c,name);if(value!=null)return value;}
        return null;
    }
    static Material Get(string name,Color color,bool emission)
    {
        string path=Root+"/Materials/"+name+".mat";
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(m!=null)return m;
        Shader shader=Shader.Find("Universal Render Pipeline/Lit");
        if(shader==null)throw new Exception("URP Lit missing");
        m=new Material(shader);m.name=name;m.SetColor("_BaseColor",color);
        if(emission){m.EnableKeyword("_EMISSION");m.SetColor("_EmissionColor",color*2);}
        AssetDatabase.CreateAsset(m,path);
        return m;
    }
    [MenuItem("C01/Controls/Wave02/Validate FBX Prefabs")]
    public static void Validate()
    {
        int err=0;
        foreach(string id in IDs)
        {
            var p=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+id+".prefab");
            if(p==null){Debug.LogError("No real prefab "+id);err++;continue;}
            if(p.transform.localScale!=Vector3.one){err++;Debug.LogError("Root scale "+id);}
            if(p.GetComponentsInChildren<MeshFilter>(true).Length==0){err++;Debug.LogError("No mesh "+id);}
            if(p.GetComponent<BoxCollider>()==null){err++;Debug.LogError("No collider "+id);}
            if(id=="P17-06"&&(Find(p.transform,"CoverPivot")==null||Find(p.transform,"SwitchPivot")==null)){err++;Debug.LogError("Missing movable pivots "+id);}
            if(id=="P17-07"&&Find(p.transform,"CartridgePivot")==null){err++;Debug.LogError("Missing cartridge "+id);}
        }
        if(err!=0)throw new Exception("W02 prefab validation FAIL: "+err);
        Debug.Log("W02 prefab presence & hierarchy PASS. Corridor, real movement and playtest NOT RUN.");
    }
}
#endif
