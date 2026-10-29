#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
// Execute menu C01 / Controls / Build Prefabs once generated FBX files are imported.
public static class C01ControlsPrefabBuilder
{
    const string Root="Assets/C01InteriorProps";
    static readonly string[] IDs={"P17-01","P17-02","P17-03"};
    [MenuItem("C01/Controls/Build Prefabs")]
    public static void Build()
    {
        Directory.CreateDirectory(Root+"/Prefabs");
        Directory.CreateDirectory(Root+"/Materials");
        AssetDatabase.Refresh();
        var steel=MakeMaterial("STEEL",new Color(.34f,.4f,.45f),false);
        var dark=MakeMaterial("DARK",new Color(.075f,.1f,.135f),false);
        var caution=MakeMaterial("CAUTION",new Color(.93f,.46f,.085f),false);
        var emissive=MakeMaterial("EMISSION",new Color(.07f,.59f,.78f),true);
        foreach(string id in IDs)
        {
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Models/"+id+".fbx");
            if(model==null) { Debug.LogError("Missing real FBX: "+id); continue; }
            GameObject root=new GameObject(id+"_Controls");
            var inst=(GameObject)PrefabUtility.InstantiatePrefab(model);
            inst.transform.SetParent(root.transform,false);
            inst.transform.localPosition=Vector3.zero;
            inst.transform.localRotation=Quaternion.identity;
            inst.transform.localScale=Vector3.one;
            foreach(var mr in inst.GetComponentsInChildren<Renderer>(true))
            {
                var source=mr.sharedMaterials;
                var target=new Material[source.Length];
                for(int i=0;i<target.Length;i++)
                {
                    string n=source[i]!=null?source[i].name.ToUpperInvariant():"";
                    target[i]=n.Contains("EMISSION")?emissive:
                       n.Contains("CAUTION")?caution:n.Contains("DARK")?dark:steel;
                }
                mr.sharedMaterials=target;
            }
            var collider=root.AddComponent<BoxCollider>();
            if(id=="P17-01"){collider.center=new Vector3(0,.53f,0);collider.size=new Vector3(1.6f,1.06f,.65f);}
            if(id=="P17-02"){collider.center=new Vector3(0,.14f,.035f);collider.size=new Vector3(.18f,.28f,.07f);}
            if(id=="P17-03")
            {
                collider.center=new Vector3(0,.17f,0);
                collider.size=new Vector3(.4f,.34f,.3f);
                var lever=Find(inst.transform,"LeverPivot");
                if(lever==null)Debug.LogError("P17-03 missing real LeverPivot");
                else
                {
                    var sphere=lever.gameObject.AddComponent<SphereCollider>();
                    sphere.center=new Vector3(0,.14f,0);
                    sphere.radius=.045f;
                    // Rotate lever.localRotation about local X, degrees 0-45 during gameplay.
                }
            }
            var path=Root+"/Prefabs/"+id+".prefab";
            PrefabUtility.SaveAsPrefabAsset(root,path);
            UnityEngine.Object.DestroyImmediate(root);
            Debug.Log("C01-17 native Unity prefab generated: "+path);
        }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Validate();
    }
    static Transform Find(Transform root,string name)
    {
        if(root.name.Contains(name))return root;
        foreach(Transform c in root){var found=Find(c,name);if(found!=null)return found;}
        return null;
    }
    static Material MakeMaterial(string id,Color color,bool glow)
    {
        var path=Root+"/Materials/C01_"+id+".mat";
        var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(mat!=null)return mat;
        var shader=Shader.Find("Universal Render Pipeline/Lit");
        if(shader==null)throw new Exception("URP Lit shader missing");
        mat=new Material(shader);mat.name="C01_"+id;
        mat.SetColor("_BaseColor",color);
        if(glow){mat.EnableKeyword("_EMISSION");mat.SetColor("_EmissionColor",color*2);}
        AssetDatabase.CreateAsset(mat,path);
        return mat;
    }
    [MenuItem("C01/Controls/Validate Prefabs")]
    public static void Validate()
    {
        int errors=0;
        foreach(string id in IDs)
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+id+".prefab");
            if(prefab==null){Debug.LogError("Missing prefab "+id);errors++;continue;}
            if(prefab.transform.localScale!=Vector3.one){Debug.LogError("Scale "+id);errors++;}
            if(prefab.GetComponent<BoxCollider>()==null){Debug.LogError("No collider "+id);errors++;}
            if(prefab.GetComponentsInChildren<MeshFilter>(true).Length==0){Debug.LogError("No mesh "+id);errors++;}
            if(id=="P17-03"&&Find(prefab.transform,"LeverPivot")==null){Debug.LogError("No lever pivot");errors++;}
        }
        if(errors!=0)throw new Exception("C01-17 prefab validation errors: "+errors);
        Debug.Log("PASS three native prefabs: presence, mesh, root scale, colliders, lever; clearance NOT RUN");
    }
}
#endif
