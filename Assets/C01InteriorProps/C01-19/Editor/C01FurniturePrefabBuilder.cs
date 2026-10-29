#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;
public static class C01FurniturePrefabBuilder {
 [Serializable] class Part { public string name; public string material; public float[] center; public float[] size; }
 [Serializable] class Model { public string id; public Part[] parts; }
 [Serializable] class Wrapper { public Model[] models; }
 private const string Root="Assets/C01InteriorProps/C01-19";
 [MenuItem("Tools/C01/Build furniture prefabs")]
 public static void Build(){
  var src=AssetDatabase.LoadAssetAtPath<TextAsset>(Root+"/Source/parts_unity.json");
  if(src==null)throw new Exception("Missing C01-19 geometry data");
  var data=JsonUtility.FromJson<Wrapper>(src.text);
  if(data==null||data.models==null||data.models.Length!=4)throw new Exception("Invalid geometry catalog");
  var shader=Shader.Find("Universal Render Pipeline/Lit");
  if(shader==null)throw new Exception("Universal Render Pipeline/Lit not found");
  Directory.CreateDirectory(Root+"/Materials");Directory.CreateDirectory(Root+"/Prefabs");
  string[] families={"steel","dark","fabric","accent"};
  Color[] colors={new Color(.38f,.45f,.48f),new Color(.11f,.16f,.19f),new Color(.30f,.39f,.43f),new Color(.90f,.53f,.16f)};
  var mats=new Material[families.Length];
  for(int i=0;i<families.Length;i++){
   string path=Root+"/Materials/M_C01_"+families[i].ToUpperInvariant()+".mat";
   mats[i]=AssetDatabase.LoadAssetAtPath<Material>(path);
   if(mats[i]==null){mats[i]=new Material(shader);mats[i].color=colors[i];AssetDatabase.CreateAsset(mats[i],path);}
  }
  foreach(var model in data.models){
   var root=new GameObject(model.id+"_Furniture");
   root.transform.position=Vector3.zero;root.transform.rotation=Quaternion.identity;root.transform.localScale=Vector3.one;
   GameObject hinge=null;
   Vector3 hingeAt=new Vector3(-.305f,.9f,-.237f);
   if(model.id=="P19-02"){hinge=new GameObject("Door_Hinge_Pivot");hinge.transform.SetParent(root.transform,false);hinge.transform.localPosition=hingeAt;}
   foreach(var part in model.parts){
    string slug=System.Text.RegularExpressions.Regex.Replace(part.name,"[^a-zA-Z0-9_]","_");
    string path=Root+"/Models/"+model.id+"/"+model.id+"__"+slug+".obj";
    var imported=AssetDatabase.LoadAssetAtPath<GameObject>(path);
    if(imported==null){UnityEngine.Object.DestroyImmediate(root);throw new Exception("OBJ not imported: "+path);}
    bool swing=hinge!=null&&(part.name=="Door_Leaf"||part.name=="Door_Handle"||part.name=="Vent_Upper");
    var go=(GameObject)PrefabUtility.InstantiatePrefab(imported);
    go.name=part.name;go.transform.SetParent(swing?hinge.transform:root.transform,false);
    go.transform.localPosition=swing?-hingeAt:Vector3.zero;go.transform.localRotation=Quaternion.identity;go.transform.localScale=Vector3.one;
    int materialId=Array.IndexOf(families,part.material);
    if(materialId<0)throw new Exception("Invalid material "+part.material);
    foreach(var renderer in go.GetComponentsInChildren<MeshRenderer>())renderer.sharedMaterial=mats[materialId];
    var collider=go.AddComponent<BoxCollider>();
    collider.center=new Vector3(part.center[0],part.center[1],part.center[2]);
    collider.size=new Vector3(part.size[0],part.size[1],part.size[2]);
   }
   string target=Root+"/Prefabs/"+model.id+"_Furniture.prefab";
   if(PrefabUtility.SaveAsPrefabAsset(root,target)==null)throw new Exception("Unable to save prefab "+target);
   UnityEngine.Object.DestroyImmediate(root);
   Debug.Log("C01-19 prefab authored: "+target);
  }
  AssetDatabase.SaveAssets();AssetDatabase.Refresh();
 }
}
#endif
