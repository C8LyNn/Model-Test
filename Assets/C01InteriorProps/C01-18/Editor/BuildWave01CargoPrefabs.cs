#if UNITY_EDITOR
using System;
using UnityEditor;
using UnityEngine;
namespace C01.Cargo {
public static class BuildWave01CargoPrefabs {
 const string Root="Assets/C01InteriorProps/C01-18";
 [MenuItem("Tools/C01/Cargo/Build Wave 01 FBX Prefabs")]
 public static void Build() {
  foreach(string id in new[]{"P18-01","P18-02","P18-03"}) {
   string modelPath=Root+"/Models/"+id+".fbx";
   var imported=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
   if(!imported) throw new InvalidOperationException("No imported FBX: "+modelPath);
   var root=new GameObject(id.Replace('-','_'));
   try {
    var obj=(GameObject)PrefabUtility.InstantiatePrefab(imported);
    obj.name=id+"_FBX"; obj.transform.SetParent(root.transform,false);
    obj.transform.localPosition=Vector3.zero; obj.transform.localRotation=Quaternion.identity; obj.transform.localScale=Vector3.one;
    int count=0,collision=0;
    foreach(var mf in root.GetComponentsInChildren<MeshFilter>(true)) {
     if(!mf.sharedMesh || mf.sharedMesh.vertexCount==0) throw new InvalidOperationException("Empty FBX mesh: "+id+" "+mf.name);
     count++;
     var renderer=mf.GetComponent<MeshRenderer>();
     if(renderer) {
      string name=mf.name.ToUpperInvariant();
      string matName=name.Contains("WHEEL")||name.Contains("GRIP")?"RUBBER":(name.Contains("LABEL")||name.Contains("TRIM")||name.Contains("LIP")?"CAUTION":(name.Contains("POST")||name.Contains("UPRIGHT")||name.Contains("RIM")||name.Contains("LID")?"DARK":"STEEL"));
      var mat=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/"+matName+".mat");
      if(mat) renderer.sharedMaterial=mat;
     }
     bool collider=id=="P18-01"?mf.name.StartsWith("Crate_Shell"):id=="P18-02"?(mf.name.StartsWith("Rack_Post")||(mf.name.StartsWith("Shelf_")&&mf.name.Contains("_Deck"))):(mf.name.StartsWith("Cart_Shelf_")||mf.name.StartsWith("Cart_Upright_"));
     if(collider) {
      var bc=mf.GetComponent<BoxCollider>()??mf.gameObject.AddComponent<BoxCollider>();
      bc.center=mf.sharedMesh.bounds.center;bc.size=mf.sharedMesh.bounds.size;collision++;
     }
    }
    if(count<3||collision==0) throw new InvalidOperationException(id+" imported model must have mesh and colliders");
    if(id=="P18-03") {
     int wheels=0;foreach(var t in root.GetComponentsInChildren<Transform>(true)) if(t.name.StartsWith("Wheel_"))wheels++;
     if(wheels!=4) throw new InvalidOperationException("4 wheel meshes required");
    }
    var path=Root+"/Prefabs/"+id+".prefab";
    if(!PrefabUtility.SaveAsPrefabAsset(root,path))throw new InvalidOperationException("Prefab save failed "+path);
    Debug.Log("[C01-18] FBX PREFAB BUILT "+id+" meshParts="+count+" colliderParts="+collision);
   } finally {UnityEngine.Object.DestroyImmediate(root);}
  }
  AssetDatabase.SaveAssets();AssetDatabase.Refresh();
 }
}
}
#endif
