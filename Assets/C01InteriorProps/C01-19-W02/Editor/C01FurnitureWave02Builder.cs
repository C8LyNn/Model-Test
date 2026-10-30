#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

/// <summary>PASS03 prefabs import the repaired FBX. Actual Unity execution is still NOT RUN.</summary>
public static class C01FurnitureWave02Builder
{
    [Serializable] private class Model { public string id; public float[] dims_xyz; public float[] dimensions_xyz; }
    [Serializable] private class Collection { public Model[] models; }
    private const string Root = "Assets/C01InteriorProps/C01-19-W02";
    [MenuItem("Tools/C01/Build furniture Wave 02")]
    public static void Build()
    {
        var source = AssetDatabase.LoadAssetAtPath<TextAsset>(Root + "/Source/wave02_unity.json");
        if (source == null) throw new Exception("C01-19 source manifest unavailable");
        var collection = JsonUtility.FromJson<Collection>(source.text);
        if (collection == null || collection.models == null || collection.models.Length != 4)
            throw new Exception("C01-19 expected exactly four models per wave");
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null) throw new Exception("Unity 6 URP Lit shader not found");
        Directory.CreateDirectory(Root + "/Materials");
        Directory.CreateDirectory(Root + "/Prefabs");
        string[] keys = { "STEEL", "DARK", "FABRIC", "ACCENT" };
        Color[] colors = { new Color(.39f,.47f,.52f), new Color(.105f,.15f,.19f),
                           new Color(.30f,.38f,.43f), new Color(.88f,.47f,.13f) };
        var materials = new Material[keys.Length];
        for (int i=0;i<keys.Length;i++)
        {
            string p = Root + "/Materials/M_C01_" + keys[i] + ".mat";
            materials[i] = AssetDatabase.LoadAssetAtPath<Material>(p);
            if (materials[i] == null)
            {
                materials[i] = new Material(shader);
                materials[i].SetColor("_BaseColor", colors[i]);
                AssetDatabase.CreateAsset(materials[i],p);
            }
        }
        foreach(var record in collection.models)
        {
            string fbxpath=Root+"/Models/"+record.id+"/"+record.id+".fbx";
            var imported=AssetDatabase.LoadAssetAtPath<GameObject>(fbxpath);
            if(imported == null) throw new Exception("C01-19 repaired FBX missing/unimportable: "+fbxpath);
            var root = new GameObject(record.id + "_Furniture_PASS03");
            root.transform.position = Vector3.zero;
            root.transform.rotation = Quaternion.identity;
            root.transform.localScale = Vector3.one;
            try
            {
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(imported);
                instance.transform.SetParent(root.transform, false); // preserve FBX authoring transforms, hinge hierarchy
                var meshFilters = instance.GetComponentsInChildren<MeshFilter>(true);
                if(meshFilters.Length==0) throw new Exception("FBX has no imported MeshFilters: "+fbxpath);
                int triangleCount=0;
                foreach(var mf in meshFilters)
                {
                    var mesh=mf.sharedMesh;
                    if(mesh==null) throw new Exception("Null MeshFilter mesh in "+fbxpath);
                    for(int k=0;k<mesh.subMeshCount;k++) triangleCount += (int)mesh.GetIndexCount(k)/3;
                    var renderer=mf.GetComponent<MeshRenderer>();
                    if(renderer==null) throw new Exception("No MeshRenderer "+mf.name);
                    var slots=renderer.sharedMaterials;
                    for(int s=0;s<slots.Length;s++)
                    {
                        string name=slots[s] == null ? "" : slots[s].name.ToUpperInvariant();
                        int index=Array.FindIndex(keys,k=>name.Contains(k));
                        if(index<0) throw new Exception("Unmapped imported material "+name+" for "+mf.name);
                        slots[s]=materials[index];
                    }
                    renderer.sharedMaterials=slots;
                    var bc=mf.gameObject.GetComponent<BoxCollider>();
                    if(bc==null) bc=mf.gameObject.AddComponent<BoxCollider>();
                    bc.center=mesh.bounds.center;
                    bc.size=mesh.bounds.size;
                }
                Bounds bounds=default;
                bool found=false;
                foreach(var renderer in root.GetComponentsInChildren<MeshRenderer>(true))
                {
                    if(!found){bounds=renderer.bounds;found=true;}
                    else bounds.Encapsulate(renderer.bounds);
                }
                float[] expected=record.dims_xyz!=null && record.dims_xyz.Length==3 ?
                                 record.dims_xyz : record.dimensions_xyz;
                if(!found||expected==null||expected.Length!=3)
                    throw new Exception("Mesh bounds/manifest missing for "+record.id);
                Vector3 actual=bounds.size;
                if(Mathf.Abs(actual.x-expected[0])>0.002f ||
                   Mathf.Abs(actual.y-expected[1])>0.002f ||
                   Mathf.Abs(actual.z-expected[2])>0.002f)
                    throw new Exception("FBX imported bounds mismatch "+record.id+
                        " actual XYZ "+actual+" expected "+expected[0]+","+expected[1]+","+expected[2]);
                string output=Root+"/Prefabs/"+record.id+"_Furniture.prefab";
                if(PrefabUtility.SaveAsPrefabAsset(root,output)==null)
                    throw new Exception("Failed to persist prefab "+output);
                Debug.Log("C01-19 PASS03 imported native FBX "+record.id+" meshes="+meshFilters.Length+
                          " triangles="+triangleCount+" bounds="+actual);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
}
#endif
