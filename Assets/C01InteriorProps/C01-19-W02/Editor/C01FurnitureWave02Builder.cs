#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
public static class C01FurnitureWave02Builder {
 [Serializable] class Part { public string name;public string material;public float[] center;public float[] size;public bool moving;public bool collider; }
 [Serializable] class Model { public string id;public string mount;public float[] dims_xyz;public float[] hinge;public Part[] parts; }
 [Serializable] class Wrapper { public Model[] models; }
 const string R="Assets/C01InteriorProps/C01-19-W02";
 [MenuItem("Tools/C01/Build furniture Wave 02")]
 public static void Build(){
   var catalog=AssetDatabase.LoadAssetAtPath<TextAsset>(R+"/Source/wave02_unity.json");
   if(catalog==null)throw new Exception("Missing C01-19-W02 catalog");
   var data=JsonUtility.FromJson<Wrapper>(catalog.text);
   if(data==null||data.models==null||data.models.Length!=4)throw new Exception("Expected four furniture models");
   var sh=Shader.Find("Universal Render Pipeline/Lit");
   if(sh==null)throw new Exception("Unity 6 URP/Lit shader required");
   Directory.CreateDirectory(R+"/Materials");Directory.CreateDirectory(R+"/Prefabs");
   string[] keys={"steel","dark","fabric","accent"};
   Color[] color={new Color(.39f,.47f,.52f),new Color(.105f,.15f,.19f),new Color(.30f,.38f,.43f),new Color(.88f,.47f,.13f)};
   Material[] mats=new Material[keys.Length];
   for(int i=0;i<keys.Length;i++){
     string file=R+"/Materials/M_C01_"+keys[i].ToUpperInvariant()+".mat";
     mats[i]=AssetDatabase.LoadAssetAtPath<Material>(file);
     if(mats[i]==null){mats[i]=new Material(sh);mats[i].color=color[i];AssetDatabase.CreateAsset(mats[i],file);}
   }
   foreach(var model in data.models){
     var root=new GameObject(model.id+"_Furniture");
     root.transform.localPosition=Vector3.zero;root.transform.localRotation=Quaternion.identity;root.transform.localScale=Vector3.one;
     GameObject hinge=null;Vector3 hingeAt=Vector3.zero;
     if(model.hinge!=null && model.hinge.Length==3){
       hingeAt=new Vector3(model.hinge[0],model.hinge[1],model.hinge[2]);
       hinge=new GameObject("Moving_Hinge_Pivot");hinge.transform.SetParent(root.transform,false);hinge.transform.localPosition=hingeAt;
     }
     foreach(var p in model.parts){
       string slug=System.Text.RegularExpressions.Regex.Replace(p.name,"[^A-Za-z0-9_]","_");
       string path=R+"/Models/"+model.id+"/"+model.id+"__"+slug+".obj";
       var original=AssetDatabase.LoadAssetAtPath<GameObject>(path);
       if(original==null){UnityEngine.Object.DestroyImmediate(root);throw new Exception("Model import unavailable: "+path);}
       var go=(GameObject)PrefabUtility.InstantiatePrefab(original);
       go.name=p.name;go.transform.SetParent(p.moving?hinge.transform:root.transform,false);
       go.transform.localPosition=p.moving?-hingeAt:Vector3.zero;
       go.transform.localRotation=Quaternion.identity;go.transform.localScale=Vector3.one;
       int j=Array.IndexOf(keys,p.material);if(j<0)throw new Exception("Invalid material "+p.material);
       foreach(var r in go.GetComponentsInChildren<MeshRenderer>())r.sharedMaterial=mats[j];
       if(p.collider){
         var col=go.AddComponent<BoxCollider>();
         col.center=new Vector3(p.center[0],p.center[1],p.center[2]);
         col.size=new Vector3(p.size[0],p.size[1],p.size[2]);
       }
     }
     string file=R+"/Prefabs/"+model.id+"_Furniture.prefab";
     if(PrefabUtility.SaveAsPrefabAsset(root,file)==null)throw new Exception("Prefab failure: "+file);
     UnityEngine.Object.DestroyImmediate(root);
     Debug.Log("Created C01-19 W02 furniture prefab "+file);
   }
   AssetDatabase.SaveAssets();AssetDatabase.Refresh();
 }
}
#endif
