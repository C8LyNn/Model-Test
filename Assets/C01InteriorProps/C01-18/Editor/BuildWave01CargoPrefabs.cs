#if UNITY_EDITOR
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
namespace C01.Cargo {
public static class BuildWave01CargoPrefabs {
 const string Root="Assets/C01InteriorProps/C01-18";
 const string SignedP1803FbxSha256 = "f169ab74086ee3853c14b46ac6f6199cd255cfca15d8b7cbef32c3758cde7926";
 // PASS17 exact current authoring OBJ usemtl slots, not unreliable name guesses.
 static readonly System.Collections.Generic.Dictionary<string,string> SourceMaterials =
  new System.Collections.Generic.Dictionary<string,string>(StringComparer.Ordinal) {
   {"P18-01/Crate_Shell","STEEL"},
   {"P18-01/Lower_Rim","DARK"},
   {"P18-01/Upper_Lid","DARK"},
   {"P18-01/Corner_LB","DARK"},
   {"P18-01/Corner_LF","DARK"},
   {"P18-01/Corner_RB","DARK"},
   {"P18-01/Corner_RF","DARK"},
   {"P18-01/Front_Trim_-0.444_0.28","CAUTION"},
   {"P18-01/Front_Trim_-0.444_0.63","CAUTION"},
   {"P18-01/Front_Trim_0.444_0.28","CAUTION"},
   {"P18-01/Front_Trim_0.444_0.63","CAUTION"},
   {"P18-01/Side_Trim_-0.444_0.28","CAUTION"},
   {"P18-01/Side_Trim_-0.444_0.63","CAUTION"},
   {"P18-01/Side_Trim_0.444_0.28","CAUTION"},
   {"P18-01/Side_Trim_0.444_0.63","CAUTION"},
   {"P18-01/TrimBacker_B_0.28","DARK"},
   {"P18-01/TrimBacker_B_0.63","DARK"},
   {"P18-01/TrimBacker_F_0.28","DARK"},
   {"P18-01/TrimBacker_F_0.63","DARK"},
   {"P18-01/TrimBacker_L_0.28","DARK"},
   {"P18-01/TrimBacker_L_0.63","DARK"},
   {"P18-01/TrimBacker_R_0.28","DARK"},
   {"P18-01/TrimBacker_R_0.63","DARK"},
   {"P18-01/RearHinge_L_Leaf","STEEL"},
   {"P18-01/RearHinge_L_Pin","DARK"},
   {"P18-01/FrontLatch_L_Backing","DARK"},
   {"P18-01/FrontLatch_L_Lever","CAUTION"},
   {"P18-01/FrontLatch_L_Fastener","STEEL"},
   {"P18-01/RearHinge_R_Leaf","STEEL"},
   {"P18-01/RearHinge_R_Pin","DARK"},
   {"P18-01/FrontLatch_R_Backing","DARK"},
   {"P18-01/FrontLatch_R_Lever","CAUTION"},
   {"P18-01/FrontLatch_R_Fastener","STEEL"},
   {"P18-01/LidCornerBolt_LB","STEEL"},
   {"P18-01/LidCornerBolt_LF","STEEL"},
   {"P18-01/LidCornerBolt_RB","STEEL"},
   {"P18-01/LidCornerBolt_RF","STEEL"},
   {"P18-01/RearHinge_L_Retainer_L","STEEL"},
   {"P18-01/RearHinge_L_Retainer_R","STEEL"},
   {"P18-01/RearHinge_R_Retainer_L","STEEL"},
   {"P18-01/RearHinge_R_Retainer_R","STEEL"},
   {"P18-01/FrontLatch_L_UpperKeeper","STEEL"},
   {"P18-01/FrontLatch_R_UpperKeeper","STEEL"},
   {"P18-01/FrontLatch_L_KeeperScrew_A","STEEL"},
   {"P18-01/FrontLatch_L_KeeperScrew_B","STEEL"},
   {"P18-01/FrontLatch_R_KeeperScrew_A","STEEL"},
   {"P18-01/FrontLatch_R_KeeperScrew_B","STEEL"},
   {"P18-02/Rack_Post_-1.015_-0.365","DARK"},
   {"P18-02/Rack_Post_-1.015_0.365","DARK"},
   {"P18-02/Rack_Post_1.015_-0.365","DARK"},
   {"P18-02/Rack_Post_1.015_0.365","DARK"},
   {"P18-02/Shelf_0_Deck","STEEL"},
   {"P18-02/Shelf_0_Lip_-0.375","CAUTION"},
   {"P18-02/Shelf_0_Lip_0.375","CAUTION"},
   {"P18-02/Shelf_1_Deck","STEEL"},
   {"P18-02/Shelf_1_Lip_-0.375","CAUTION"},
   {"P18-02/Shelf_1_Lip_0.375","CAUTION"},
   {"P18-02/Shelf_2_Deck","STEEL"},
   {"P18-02/Shelf_2_Lip_-0.375","CAUTION"},
   {"P18-02/Shelf_2_Lip_0.375","CAUTION"},
   {"P18-02/Back_Support_0.6","STEEL"},
   {"P18-02/Back_Support_1.48","STEEL"},
   {"P18-02/Top_Label_-0.5","CAUTION"},
   {"P18-02/Top_Label_0.5","CAUTION"},
   {"P18-02/Shelf0_Bracket_LB","DARK"},
   {"P18-02/Shelf0_Bracket_LF","DARK"},
   {"P18-02/Shelf0_Bracket_RB","DARK"},
   {"P18-02/Shelf0_Bracket_RF","DARK"},
   {"P18-02/Shelf0_LipBolt_LB","STEEL"},
   {"P18-02/Shelf0_LipBolt_LF","STEEL"},
   {"P18-02/Shelf0_LipBolt_RB","STEEL"},
   {"P18-02/Shelf0_LipBolt_RF","STEEL"},
   {"P18-02/Shelf1_Bracket_LB","DARK"},
   {"P18-02/Shelf1_Bracket_LF","DARK"},
   {"P18-02/Shelf1_Bracket_RB","DARK"},
   {"P18-02/Shelf1_Bracket_RF","DARK"},
   {"P18-02/Shelf1_LipBolt_LB","STEEL"},
   {"P18-02/Shelf1_LipBolt_LF","STEEL"},
   {"P18-02/Shelf1_LipBolt_RB","STEEL"},
   {"P18-02/Shelf1_LipBolt_RF","STEEL"},
   {"P18-02/Shelf2_Bracket_LB","DARK"},
   {"P18-02/Shelf2_Bracket_LF","DARK"},
   {"P18-02/Shelf2_Bracket_RB","DARK"},
   {"P18-02/Shelf2_Bracket_RF","DARK"},
   {"P18-02/Shelf2_LipBolt_LB","STEEL"},
   {"P18-02/Shelf2_LipBolt_LF","STEEL"},
   {"P18-02/Shelf2_LipBolt_RB","STEEL"},
   {"P18-02/Shelf2_LipBolt_RF","STEEL"},
   {"P18-02/Top_Label_L_MountingBackplate","DARK"},
   {"P18-02/Top_Label_L_Bolt_L","STEEL"},
   {"P18-02/Top_Label_L_Bolt_R","STEEL"},
   {"P18-02/Top_Label_R_MountingBackplate","DARK"},
   {"P18-02/Top_Label_R_Bolt_L","STEEL"},
   {"P18-02/Top_Label_R_Bolt_R","STEEL"},
   {"P18-02/BackSupport_0.60_Gusset_L","STEEL"},
   {"P18-02/BackSupport_0.60_Gusset_R","STEEL"},
   {"P18-02/BackSupport_1.48_Gusset_L","STEEL"},
   {"P18-02/BackSupport_1.48_Gusset_R","STEEL"},
   {"P18-02/BackSupport_0.60_GussetFastener_L","STEEL"},
   {"P18-02/BackSupport_0.60_GussetFastener_R","STEEL"},
   {"P18-02/BackSupport_1.48_GussetFastener_L","STEEL"},
   {"P18-02/BackSupport_1.48_GussetFastener_R","STEEL"},
   {"P18-02/Rack_FootPlate_LB","STEEL"},
   {"P18-02/Rack_FootPlate_LF","STEEL"},
   {"P18-02/Rack_FootPlate_RB","STEEL"},
   {"P18-02/Rack_FootPlate_RF","STEEL"},
   {"P18-03/Cart_Shelf_0","STEEL"},
   {"P18-03/Cart_Shelf_Lip_0_-0.48","CAUTION"},
   {"P18-03/Cart_Shelf_Lip_0_0.48","CAUTION"},
   {"P18-03/Cart_Shelf_1","STEEL"},
   {"P18-03/Cart_Shelf_Lip_1_-0.48","CAUTION"},
   {"P18-03/Cart_Shelf_Lip_1_0.48","CAUTION"},
   {"P18-03/Cart_Upright_-0.44_-0.29","DARK"},
   {"P18-03/Cart_Upright_-0.44_0.29","DARK"},
   {"P18-03/Cart_Upright_0.44_-0.29","DARK"},
   {"P18-03/Cart_Upright_0.44_0.29","DARK"},
   {"P18-03/Wheel_LB","RUBBER"},
   {"P18-03/Wheel_LF","RUBBER"},
   {"P18-03/Wheel_RB","RUBBER"},
   {"P18-03/Wheel_RF","RUBBER"},
   {"P18-03/Cart_Handle_Post_-0.44","DARK"},
   {"P18-03/Cart_Handle_Post_0.44","DARK"},
   {"P18-03/Cart_Handle_Grip","RUBBER"},
   {"P18-03/Wheel_LB_ForkInner","DARK"},
   {"P18-03/Wheel_LB_ForkOuter","DARK"},
   {"P18-03/Wheel_LB_ForkCrown","STEEL"},
   {"P18-03/Wheel_LB_Anchor","DARK"},
   {"P18-03/Wheel_LB_Gusset","STEEL"},
   {"P18-03/Wheel_LB_Axle","STEEL"},
   {"P18-03/Wheel_LB_Hub_In","STEEL"},
   {"P18-03/Wheel_LB_Hub_Out","STEEL"},
   {"P18-03/Wheel_LB_AxleFastener","DARK"},
   {"P18-03/Wheel_LF_ForkInner","DARK"},
   {"P18-03/Wheel_LF_ForkOuter","DARK"},
   {"P18-03/Wheel_LF_ForkCrown","STEEL"},
   {"P18-03/Wheel_LF_Anchor","DARK"},
   {"P18-03/Wheel_LF_Gusset","STEEL"},
   {"P18-03/Wheel_LF_Axle","STEEL"},
   {"P18-03/Wheel_LF_Hub_In","STEEL"},
   {"P18-03/Wheel_LF_Hub_Out","STEEL"},
   {"P18-03/Wheel_LF_AxleFastener","DARK"},
   {"P18-03/Wheel_RB_ForkInner","DARK"},
   {"P18-03/Wheel_RB_ForkOuter","DARK"},
   {"P18-03/Wheel_RB_ForkCrown","STEEL"},
   {"P18-03/Wheel_RB_Anchor","DARK"},
   {"P18-03/Wheel_RB_Gusset","STEEL"},
   {"P18-03/Wheel_RB_Axle","STEEL"},
   {"P18-03/Wheel_RB_Hub_In","STEEL"},
   {"P18-03/Wheel_RB_Hub_Out","STEEL"},
   {"P18-03/Wheel_RB_AxleFastener","DARK"},
   {"P18-03/Wheel_RF_ForkInner","DARK"},
   {"P18-03/Wheel_RF_ForkOuter","DARK"},
   {"P18-03/Wheel_RF_ForkCrown","STEEL"},
   {"P18-03/Wheel_RF_Anchor","DARK"},
   {"P18-03/Wheel_RF_Gusset","STEEL"},
   {"P18-03/Wheel_RF_Axle","STEEL"},
   {"P18-03/Wheel_RF_Hub_In","STEEL"},
   {"P18-03/Wheel_RF_Hub_Out","STEEL"},
   {"P18-03/Wheel_RF_AxleFastener","DARK"},
   {"P18-03/Wheel_LB_CrownBolt","DARK"},
   {"P18-03/Wheel_LF_CrownBolt","DARK"},
   {"P18-03/Wheel_RB_CrownBolt","DARK"},
   {"P18-03/Wheel_RF_CrownBolt","DARK"},
   {"P18-03/Wheel_LB_AnchorRetainer","STEEL"},
   {"P18-03/Wheel_LF_AnchorRetainer","STEEL"},
   {"P18-03/Wheel_RB_AnchorRetainer","STEEL"},
   {"P18-03/Wheel_RF_AnchorRetainer","STEEL"},
   {"P18-03/Cart_HandleClamp_L","STEEL"},
   {"P18-03/Cart_HandleClamp_R","STEEL"},
  };
 [MenuItem("Tools/C01/Cargo/Build Wave 01 FBX Prefabs")]
 public static void Build() {
  // Fail closed before importing or writing a model/prefab.
  VerifyGenuineP1803BeforeWrites();
  foreach(string id in new[]{"P18-01","P18-02","P18-03"}) {
   string modelPath=Root+"/Models/"+id+".fbx";
   var imported=AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
   if(!imported) throw new InvalidOperationException("No imported FBX: "+modelPath);
   var root=new GameObject(id.Replace('-','_'));
   try {
    var obj=(GameObject)PrefabUtility.InstantiatePrefab(imported);
    obj.name=id+"_FBX"; obj.transform.SetParent(root.transform,false);
    obj.transform.localPosition=Vector3.zero; obj.transform.localRotation=Quaternion.identity; obj.transform.localScale=Vector3.one;
    int count=0,collision=0,totalTriangles=0;
    foreach(var mf in root.GetComponentsInChildren<MeshFilter>(true)) {
     if(!mf.sharedMesh || mf.sharedMesh.vertexCount==0) throw new InvalidOperationException("Empty FBX mesh: "+id+" "+mf.name);
     count++;
     totalTriangles+=mf.sharedMesh.triangles.Length/3;
     var renderer=mf.GetComponent<MeshRenderer>();
     if(!renderer)throw new InvalidOperationException("Missing MeshRenderer "+id+"/"+mf.name);
     string matName;
     if(!SourceMaterials.TryGetValue(id+"/"+mf.name,out matName))
      throw new InvalidOperationException("Unregistered OBJ material part "+id+"/"+mf.name);
     var mat=AssetDatabase.LoadAssetAtPath<Material>(Root+"/Materials/"+matName+".mat");
     if(!mat)throw new InvalidOperationException("Missing URP material "+matName+" for "+id+"/"+mf.name);
     renderer.sharedMaterial=mat;
     bool collider=id=="P18-01"?mf.name.StartsWith("Crate_Shell"):id=="P18-02"?(mf.name.StartsWith("Rack_Post")||(mf.name.StartsWith("Shelf_")&&mf.name.Contains("_Deck"))):((mf.name=="Cart_Shelf_0"||mf.name=="Cart_Shelf_1")||mf.name.StartsWith("Cart_Upright_"));
     if(collider) {
      var bc=mf.GetComponent<BoxCollider>()??mf.gameObject.AddComponent<BoxCollider>();
      bc.center=mf.sharedMesh.bounds.center;bc.size=mf.sharedMesh.bounds.size;collision++;
     }
    }
    int expectedParts=id=="P18-01"?47:(id=="P18-02"?59:63);
    int expectedTriangles=id=="P18-01"?980:(id=="P18-02"?1284:1780);
    int expectedColliders=id=="P18-01"?1:(id=="P18-02"?7:6);
    if(count!=expectedParts||totalTriangles!=expectedTriangles||collision!=expectedColliders)
     throw new InvalidOperationException(id+" FBX fidelity gate failed: "+count+"/"+totalTriangles+"/"+collision+" expected "+expectedParts+"/"+expectedTriangles+"/"+expectedColliders);
    if(id=="P18-03") {
     int wheels=0;
     var natives = new Transform[4];
     string[] names = {"Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF"};
     foreach(var t in root.GetComponentsInChildren<Transform>(true)) {
      if(t.name=="Wheel_LB"||t.name=="Wheel_LF"||t.name=="Wheel_RB"||t.name=="Wheel_RF") {
       if(!t.GetComponent<MeshFilter>())throw new InvalidOperationException("Wheel has no mesh: "+t.name);
       for (int i=0;i<names.Length;i++)
        if(t.name==names[i]) {
         if(natives[i]!=null)throw new InvalidOperationException("Duplicate wheel pivot "+names[i]);
         natives[i]=t;
        }
       wheels++;
      }
     }
     if(wheels!=4)throw new InvalidOperationException("Expected four movable wheel mesh pivots, got "+wheels);
     // All signed FBX metal bearings have real rendered intersections with
     // fixed forks; they are INTENTIONALLY NON-PHYSICS meshes. Physics on
     // the cart is delegated to six shelf/upright BoxColliders only.
     foreach (var m in root.GetComponentsInChildren<MeshFilter>(true)) {
      string n=m.name;
      if(n.StartsWith("Wheel_",StringComparison.Ordinal) && m.GetComponent<Collider>()!=null)
       throw new InvalidOperationException("Invalid solid wheel/fork/hub/axle Collider: "+n);
     }
     if(collision!=6)throw new InvalidOperationException("P18-03 requires six static shelf/upright colliders");
     var visualRoll = root.AddComponent<C01CartWheelVisualBearing>();
     visualRoll.Configure(natives);
     if(!visualRoll.IsConfigured)throw new InvalidOperationException("P18-03 visual bearing guard unconfigured");
    }
    var path=Root+"/Prefabs/"+id+".prefab";
    if(!PrefabUtility.SaveAsPrefabAsset(root,path))throw new InvalidOperationException("Prefab save failed "+path);
    Debug.Log("[C01-18] FBX PREFAB BUILT "+id+" meshParts="+count+" triangles="+totalTriangles+" colliderParts="+collision);
   } finally {UnityEngine.Object.DestroyImmediate(root);}
  }
  AssetDatabase.SaveAssets();AssetDatabase.Refresh();
 }
 private static void VerifyGenuineP1803BeforeWrites() {
  const int signedLength=194060;
  string p=Root+"/Models/P18-03.fbx";
  if(!File.Exists(p))throw new FileNotFoundException("Missing signed P18-03 FBX (Git LFS hydration required)",p);
  using(var fs=File.OpenRead(p))
  using(var sha=SHA256.Create()) {
   if(fs.Length!=signedLength)
    throw new InvalidOperationException("P18-03 binary FBX length differs from immutable signature");
   string digest=BitConverter.ToString(sha.ComputeHash(fs)).Replace("-","").ToLowerInvariant();
   if(!string.Equals(digest,SignedP1803FbxSha256,StringComparison.Ordinal))
    throw new InvalidOperationException("P18-03 true hydrated binary FBX SHA differs: refusing Unity prefab build");
  }
 }
}
}
#endif
