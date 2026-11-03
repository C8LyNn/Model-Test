#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
namespace C01.Cargo {
public static class BuildWave02CargoPrefabs {
 const string Root = "Assets/C01InteriorProps/C01-18-Wave02";
 const string P1807ExpectedFBXSha256 = "858a24db4338804ee3a3a70c310cd4936e3c45f559b9c4ab81c6037add564554";
 static readonly string[] IDs = {"P18-04","P18-05","P18-06","P18-07"};
 [MenuItem("Tools/C01/Cargo/Build Wave 02 FBX Prefabs")]
 public static void Build() {
  // Fail closed before ANY asset/material/prefab write: this must be the actual
  // independently STATIC_PASS W20 P18-07 binary FBX, never Git LFS pointer text.
  VerifyExactP1807FbxBeforeAnyWrites();
  string matDir=Root+"/Materials",prefabDir=Root+"/Prefabs";
  if(!AssetDatabase.IsValidFolder(matDir)) AssetDatabase.CreateFolder(Root,"Materials");
  if(!AssetDatabase.IsValidFolder(prefabDir))AssetDatabase.CreateFolder(Root,"Prefabs");
  foreach(string id in IDs) {
   string path=Root+"/Models/"+id+".fbx";
   GameObject source=AssetDatabase.LoadAssetAtPath<GameObject>(path);
   if(!source) throw new InvalidOperationException("Missing imported FBX (extract CI build archive): "+path);
   var root=new GameObject(id.Replace('-','_'));
   try {
    var sourceInstance=(GameObject)PrefabUtility.InstantiatePrefab(source);
    if(!sourceInstance) throw new InvalidOperationException("FBX model failed import: "+id);
    sourceInstance.name=id+"_FBX";
    sourceInstance.transform.SetParent(root.transform,false);
    sourceInstance.transform.localPosition=Vector3.zero;
    sourceInstance.transform.localRotation=Quaternion.identity;
    sourceInstance.transform.localScale=Vector3.one;
    int meshes=0, colliders=0;
    foreach(var mf in root.GetComponentsInChildren<MeshFilter>(true)) {
     if(!mf.sharedMesh || mf.sharedMesh.vertexCount<3)throw new InvalidOperationException("Empty mesh: "+id+" "+mf.name);
     var mesh=mf.sharedMesh;
     if(mesh.uv==null || mesh.uv.Length!=mesh.vertexCount)throw new InvalidOperationException("Missing UV0: "+id+" "+mf.name);
     if(mesh.normals==null || mesh.normals.Length!=mesh.vertexCount)throw new InvalidOperationException("Missing normals: "+id+" "+mf.name);
     meshes++;
     var renderer=mf.GetComponent<MeshRenderer>();
     if(renderer) renderer.sharedMaterial=SharedMaterial(mf.name,matDir);
     if(NeedsCollider(mf.name)) {
      var bc=mf.gameObject.GetComponent<BoxCollider>()??mf.gameObject.AddComponent<BoxCollider>();
      bc.center=mesh.bounds.center;
      bc.size=mesh.bounds.size;
      bc.isTrigger=false;
      colliders++;
     }
    }
    if(meshes<5||colliders<2)throw new InvalidOperationException("Invalid meshes/colliders "+id);
    if(id=="P18-05"||id=="P18-07") {
     string needle=id=="P18-05"?"Lid_HingePivot":"Toolbox_LidHinge";
     if(!FindTransform(root.transform,needle))throw new InvalidOperationException("Lid pivot missing: "+id);
    }
    if(id=="P18-07") {
     // C01-02 confirmed 13 lock-vs-lid triangle contacts at 0° and 9 at 5°.
     // A locked lid MUST have the real static Front_Lock collider; it is
     // disabled only when the explicit unlock state precedes any hinge movement.
     if(meshes!=10 || colliders!=4)
      throw new InvalidOperationException("P18-07 expected 10 native meshes / 4 solid colliders: "+
       meshes+"/"+colliders);
     var hinge=FindTransform(root.transform,"Toolbox_LidHinge");
     var lockNode=FindTransform(root.transform,"Front_Lock");
     if(!hinge || !lockNode)
      throw new InvalidOperationException("P18-07 actual native FBX lid hinge / Front_Lock missing");
     foreach(string child in new[]{"Bin_Lid","Lid_Label","Handle_Post_L","Handle_Post_R","Handle_Grip"}) {
      var t=FindTransform(root.transform,child);
      if(!t || t.parent!=hinge)
       throw new InvalidOperationException("P18-07 moving lid/handle child not parented to hinge: "+child);
     }
     var lockCollider=lockNode.GetComponent<BoxCollider>();
     var lockRenderer=lockNode.GetComponent<MeshRenderer>();
     if(!lockCollider || lockCollider.isTrigger || !lockRenderer || !lockRenderer.enabled)
      throw new InvalidOperationException("P18-07 requires VISIBLE lock mesh with physical non-trigger Front_Lock collider");
     var gate=root.AddComponent<C01ToolBinLatchGate>();
     gate.Configure(hinge,lockCollider);
     if(gate.IsUnlocked || gate.IsLockVisiblyReleased || !lockCollider.enabled)
      throw new InvalidOperationException("P18-07 prefab MUST initialize with VISIBLE latch ENGAGED and lid LOCKED");
    }
    // A kinematic Rigidbody allows later pickup by gameplay scripts; no autonomous falling.
    var body=root.AddComponent<Rigidbody>();
    body.isKinematic=true;body.useGravity=false;body.interpolation=RigidbodyInterpolation.Interpolate;
    var prefabPath=prefabDir+"/"+id+".prefab";
    var prefab=PrefabUtility.SaveAsPrefabAsset(root,prefabPath);
    if(!prefab)throw new InvalidOperationException("Prefab not saved "+prefabPath);
    Debug.Log("C01-18_W02_REAL_FBX_PREFAB_PASS "+id+" meshes="+meshes+" colliders="+colliders);
   } finally {UnityEngine.Object.DestroyImmediate(root);}
  }
  AssetDatabase.SaveAssets();AssetDatabase.Refresh();
 }
 private static void VerifyExactP1807FbxBeforeAnyWrites() {
  var path=Root+"/Models/P18-07.fbx";
  if(!File.Exists(path))
   throw new FileNotFoundException("P18-07 real binary FBX not staged",path);
  using(var stream=File.OpenRead(path))
  using(var hasher=SHA256.Create()) {
   if(stream.Length!=41484)
    throw new InvalidOperationException("P18-07 genuine FBX size mismatch; possible LFS pointer/stale export: "+stream.Length);
   string actual=BitConverter.ToString(hasher.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
   if(!string.Equals(actual,P1807ExpectedFBXSha256,StringComparison.Ordinal))
    throw new InvalidOperationException("P18-07 immutable REAL FBX SHA256 mismatch (refuse prefab writes)");
  }
 }
 private static Transform FindTransform(Transform t,string name) {
  if(t.name==name)return t;
  foreach(Transform c in t) {var x=FindTransform(c,name);if(x)return x;}return null;
 }
 private static bool NeedsCollider(string n) {
  return n=="Floor_Foot"||n=="Pressure_Shell"||n=="Transport_Socket"||
   n=="Case_Bottom"||n=="Case_Lid"||n=="Sample_Vault"||
   n=="Reinforced_Base"||n=="Safety_Lid"||n=="Bin_Chassis"||
   n=="Bin_Lid"||n=="Base_Stiffener"||n=="Front_Lock";
 }
 private static Material SharedMaterial(string part,string folder) {
  string u=part.ToUpperInvariant();
  string key=u.Contains("WARNING")||u.Contains("LABEL")||u.Contains("ACCENT")||u.Contains("LOCK")||u.Contains("LATCH")||u.Contains("CAP")||u.Contains("EMBLEM")?"CAUTION":
    u.Contains("GASKET")||u.Contains("GRIP")||u.Contains("HANDLE")||u.Contains("RAIL")?"GASKET":
    u.Contains("FOOT")||u.Contains("BAND")||u.Contains("LID")||u.Contains("POST")||u.Contains("CHASSIS")||u.Contains("BASE")?"DARK":"STEEL";
  string path=folder+"/"+key+".mat";
  var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
  if(mat)return mat;
  Shader shader=Shader.Find("Universal Render Pipeline/Lit");
  if(!shader)throw new InvalidOperationException("Unity URP Lit shader unavailable");
  mat=new Material(shader);
  var color=key=="CAUTION"?new Color(.94f,.52f,.13f):key=="GASKET"?new Color(.11f,.15f,.19f):key=="DARK"?new Color(.07f,.11f,.16f):new Color(.31f,.39f,.46f);
  mat.SetColor("_BaseColor",color);mat.SetFloat("_Metallic",key=="GASKET"?.12f:.55f);mat.SetFloat("_Smoothness",.34f);
  AssetDatabase.CreateAsset(mat,path);return mat;
 }
}
}
#endif
