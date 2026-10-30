#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class C01Structures14PrefabBuilder {
    const string Root="Assets/C01StructuralPrototypes/P14";
    [MenuItem("Tools/C01/Structures 14/Build reference prefabs")]
    public static void Build() {
        Directory.CreateDirectory(Root+"/Prefabs");
        Directory.CreateDirectory(Root+"/Materials");
        AssetDatabase.Refresh();
        var shader=Shader.Find("Universal Render Pipeline/Lit");
        if (shader==null) throw new InvalidOperationException("Unity 6 URP Lit shader not found");
        var steel=GetMaterial("Steel",new Color(.46f,.53f,.58f),shader);
        var dark=GetMaterial("Dark",new Color(.11f,.15f,.19f),shader);
        var caution=GetMaterial("Caution",new Color(.92f,.59f,.09f),shader);
        foreach (string id in new[]{"RMP-01","RAI-01"}) {
            string path=Root+"/FBX/C01_14_"+id+"_v001.fbx";
            var source=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (source==null) throw new FileNotFoundException("Missing imported real FBX",path);
            var root=new GameObject("P_C01_14_"+id.Replace("-",""));
            try {
                root.transform.localScale=Vector3.one;
                var imported=(GameObject)PrefabUtility.InstantiatePrefab(source);
                imported.transform.SetParent(root.transform,false);
                imported.transform.localPosition=Vector3.zero;
                imported.transform.localRotation=Quaternion.identity;
                imported.transform.localScale=Vector3.one;
                bool hasCollider=false;
                foreach(var filter in imported.GetComponentsInChildren<MeshFilter>(true)) {
                    var obj=filter.gameObject;
                    var renderer=obj.GetComponent<MeshRenderer>();
                    if(obj.name.StartsWith("COL_",StringComparison.OrdinalIgnoreCase)) {
                        if(renderer)renderer.enabled=false;
                        if(id=="RMP-01") {
                            var col=obj.AddComponent<MeshCollider>();
                            col.sharedMesh=filter.sharedMesh;
                            col.convex=false;
                            hasCollider=true;
                        }
                    } else {
                        if(renderer)renderer.sharedMaterial=obj.name.Contains("AntiSlip")?caution:
                            obj.name.Contains("MiddleRail")?dark:steel;
                        if(id=="RAI-01") {
                            var col=obj.AddComponent<BoxCollider>();
                            col.center=filter.sharedMesh.bounds.center;
                            col.size=filter.sharedMesh.bounds.size;
                            hasCollider=true;
                        }
                    }
                }
                if(!hasCollider)throw new InvalidOperationException("No valid collision mesh for "+id);
                root.isStatic=true;
                PrefabUtility.SaveAsPrefabAsset(root,Root+"/Prefabs/"+root.name+".prefab");
            } finally {UnityEngine.Object.DestroyImmediate(root);}
        }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("C01-14 reference prefabs authored. In-engine mesh and clearance QA is still required.");
    }
    static Material GetMaterial(string name,Color color,Shader shader) {
        string path=Root+"/Materials/M_C01_14_"+name+".mat";
        var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(mat!=null)return mat;
        mat=new Material(shader) {name="M_C01_14_"+name};
        mat.SetColor("_BaseColor",color);
        mat.SetFloat("_Smoothness",.22f);
        AssetDatabase.CreateAsset(mat,path);
        return mat;
    }
}
#endif
