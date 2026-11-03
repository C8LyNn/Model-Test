// C01-10 W29: exactly signed original FBX; QA-only non-door scene.
// Generates nothing until real licensed Unity 6000.3.14f1 runs.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
namespace C01.InteriorProps.Pass29 {
 [Serializable] public class NineSource {public string id,sha;public int bytes;}
 [Serializable] public class NineManifest {public string schema;public NineSource[] inputs;}
 public static class W29Room {
  const string In="Assets/C01InteriorProps/Pass29Incoming";
  const string Out="Assets/C01InteriorProps/Pass29/Generated";
  const string Prefabs=Out+"/Resources/W29QA";
  const string Mats=Out+"/Materials";
  public const string Scene=Out+"/Scenes/W29_NONDOOR_ROOM_4x4_CORRIDOR_2x4.unity";
  static readonly string[] Ids={"W01","F01","C01","P16-01","P17-02","P18-01","P19-03","P15-03","P18-03"};
  static Dictionary<string,GameObject> prefabs=new Dictionary<string,GameObject>();
  static string Full(string rel) {return Path.Combine(Directory.GetParent(Application.dataPath).FullName,rel.Replace('/',Path.DirectorySeparatorChar));}
  static string Hash(string path) {
   using(var s=File.OpenRead(path))using(var h=SHA256.Create())
    return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();
  }
  static Bounds Bounds(GameObject go) {
   var r=go.GetComponentsInChildren<MeshRenderer>(true);
   if(r.Length==0)throw new InvalidDataException("No real FBX renderers: "+go.name);
   Bounds b=r[0].bounds;for(int i=1;i<r.Length;i++)b.Encapsulate(r[i].bounds);return b;
  }
  static NineManifest Check() {
   if(Application.unityVersion!="6000.3.14f1")throw new InvalidOperationException("Wrong Unity version");
   if(!File.ReadAllText(Full("Packages/manifest.json")).Contains("\"com.unity.render-pipelines.universal\": \"17.3.0\""))
    throw new InvalidOperationException("URP 17.3.0 required");
   if(GraphicsSettings.currentRenderPipeline==null||
    GraphicsSettings.currentRenderPipeline.GetType().Name.IndexOf("Universal",StringComparison.OrdinalIgnoreCase)<0)
    throw new InvalidOperationException("Actual URP pipeline not active");
   var m=JsonUtility.FromJson<NineManifest>(File.ReadAllText(Full("C01InteriorProps/Pass29/W29_SIGNED_NONDOOR_NINE.json")));
   if(m==null||m.schema!="C01-W29-SIGNED-FBX-9-V1"||m.inputs==null||m.inputs.Length!=9||
    !Ids.OrderBy(s=>s).SequenceEqual(m.inputs.Select(s=>s.id).OrderBy(s=>s)))
    throw new InvalidDataException("Signed nine allowlist wrong");
   foreach(var x in m.inputs) {
    if(x.id.StartsWith("D")||x.id=="W04")throw new InvalidDataException("Protected geometry");
    string path=Full(In+"/"+x.id+"/"+x.id+".fbx");
    if(!File.Exists(path)||new FileInfo(path).Length!=x.bytes)
     throw new FileNotFoundException("Original FBX not physically staged "+x.id);
    var header=new byte[18];using(var s=File.OpenRead(path))if(s.Read(header,0,18)!=18)
      throw new InvalidDataException("Invalid binary header");
    if(System.Text.Encoding.ASCII.GetString(header)!="Kaydara FBX Binary"||Hash(path)!=x.sha)
     throw new InvalidDataException("Wrong full original SHA "+x.id);
    if(File.Exists(Full(Prefabs+"/"+x.id+".prefab")))
     throw new IOException("No overwrite of old QA output "+x.id);
   }
   if(File.Exists(Full(Scene)))throw new IOException("QA scene already exists");
   if(Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty))
    throw new InvalidOperationException("Save existing scene; no ship modifications allowed");
   return m;
  }
  static GameObject Copy(string id,string name,float yaw=0) {
   var go=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[id]);
   go.name=name;go.transform.rotation=Quaternion.Euler(0,yaw,0);return go;
  }
  static void Place(GameObject go,float x,float y,float z,bool yTop=false,bool xzCenter=false,bool yCenter=false) {
   var b=Bounds(go);
   go.transform.position+=new Vector3(x-(xzCenter?b.center.x:b.min.x),
    y-(yTop?b.max.y:yCenter?b.center.y:b.min.y),
    z-(xzCenter?b.center.z:b.min.z));
  }
  static void Tile(int x,int z,bool ceiling) {
   var go=Copy(ceiling?"C01":"F01",(ceiling?"CEILING_":"FLOOR_")+x+"_"+z);
   Place(go,x,ceiling?3f:0f,z,!ceiling);
  }
  static void Wall(string name,float x,float z,float yaw) {
   var go=Copy("W01","WALL_"+name,yaw);Place(go,x,0,z);
  }
  static void Prop(string id,float x,float z,float y,bool yTop=false,bool yCenter=false) {
   var go=Copy(id,"PROP_"+id);Place(go,x,y,z,yTop,true,yCenter);
  }
  [MenuItem("C01/Pass29/Build nine genuine FBX room 4x4 corridor 2x4 QA")]
  public static void Build() {
   var m=Check(); // All nine physical SHA checked before any Unity asset writes.
   AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
   var lit=Shader.Find("Universal Render Pipeline/Lit");
   if(lit==null)throw new InvalidOperationException("URP/Lit shader missing");
   foreach(var x in m.inputs) {
    string path=In+"/"+x.id+"/"+x.id+".fbx";
    if(Hash(Full(path))!=x.sha)throw new InvalidDataException("SHA changed mid-import "+x.id);
    var imp=AssetImporter.GetAtPath(path) as ModelImporter;
    if(imp==null)throw new InvalidDataException("Missing real FBX importer");
    if(!imp.isReadable||imp.importNormals!=ModelImporterNormals.Import||
     !imp.preserveHierarchy||imp.meshCompression!=ModelImporterMeshCompression.Off) {
     imp.isReadable=true;imp.importNormals=ModelImporterNormals.Import;
     imp.preserveHierarchy=true;imp.meshCompression=ModelImporterMeshCompression.Off;
     imp.SaveAndReimport();
    }
    var model=AssetDatabase.LoadAssetAtPath<GameObject>(path);
    if(model==null)throw new InvalidDataException("Imported source null "+x.id);
    var mesh=model.GetComponentsInChildren<MeshFilter>(true);
    if(mesh.Length==0)throw new InvalidDataException("Missing FBX mesh "+x.id);
    foreach(var f in mesh) {
     if(f.sharedMesh==null||!f.sharedMesh.isReadable||
      f.sharedMesh.uv.Length!=f.sharedMesh.vertexCount||
      f.sharedMesh.normals.Length!=f.sharedMesh.vertexCount||
      AssetDatabase.GetAssetPath(f.sharedMesh).Replace('\\','/')!=path)
      throw new InvalidDataException("Imported mesh UV/normal/provenance bad: "+x.id);
    }
    var test=(GameObject)PrefabUtility.InstantiatePrefab(model);
    try {
     Vector3 expect=x.id=="W01"?new Vector3(1,3,.2f):
      (x.id=="F01"||x.id=="C01")?new Vector3(1,.2f,1):Vector3.zero;
     if(expect!=Vector3.zero&&Vector3.Distance(Bounds(test).size,expect)>.012f)
      throw new InvalidDataException("Actual Unity 1m source dimensions differ "+x.id);
    }finally{UnityEngine.Object.DestroyImmediate(test);}
   }
   Directory.CreateDirectory(Full(Prefabs));
   Directory.CreateDirectory(Full(Mats));
   Directory.CreateDirectory(Full(Out+"/Scenes"));
   EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
   foreach(var x in m.inputs) {
    var model=AssetDatabase.LoadAssetAtPath<GameObject>(In+"/"+x.id+"/"+x.id+".fbx");
    var go=(GameObject)PrefabUtility.InstantiatePrefab(model);
    try {
     int k=0;
     foreach(var r in go.GetComponentsInChildren<MeshRenderer>(true)) {
      var old=r.sharedMaterials;
      if(old.Length==0||old.Any(mat=>mat==null))throw new InvalidDataException("Missing authored material slot "+x.id);
      var next=new Material[old.Length];
      for(int i=0;i<old.Length;i++) {
       var mat=new Material(lit);mat.name="QA_DERIVED_"+x.id+"_"+k;
       var color=old[i].HasProperty("_BaseColor")?old[i].GetColor("_BaseColor"):
        old[i].HasProperty("_Color")?old[i].GetColor("_Color"):Color.gray;
       mat.SetColor("_BaseColor",color);
       AssetDatabase.CreateAsset(mat,Mats+"/"+x.id+"_"+k+".mat");next[i]=mat;k++;
      }r.sharedMaterials=next;
     }
     if(x.id=="W01"||x.id=="F01"||x.id=="C01") {
      foreach(var f in go.GetComponentsInChildren<MeshFilter>(true)) {
       var c=f.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;c.convex=false;
      } // QA-only static source-derived colliders, not production acceptance.
     }else if(x.id=="P18-01"||x.id=="P19-03") {
      var b=Bounds(go);var c=go.AddComponent<BoxCollider>();
      c.center=go.transform.InverseTransformPoint(b.center);c.size=b.size;
     } // QA-only bounding collision; moving components NOT physically approved.
     var saved=PrefabUtility.SaveAsPrefabAsset(go,Prefabs+"/"+x.id+".prefab");
     if(saved==null)throw new IOException("Unity prefab not saved "+x.id);
     prefabs[x.id]=AssetDatabase.LoadAssetAtPath<GameObject>(Prefabs+"/"+x.id+".prefab");
    } finally {UnityEngine.Object.DestroyImmediate(go);}
   }
   // Room x0..4,z0..4; connected corridor x4..8,z1..3. Open 2m connection at x4.
   for(int x=0;x<4;x++)for(int z=0;z<4;z++){Tile(x,z,false);Tile(x,z,true);}
   for(int x=4;x<8;x++)for(int z=1;z<3;z++){Tile(x,z,false);Tile(x,z,true);}
   for(int x=0;x<4;x++){Wall("S_"+x,x,-.2f,0);Wall("N_"+x,x,4,180);}
   for(int z=0;z<4;z++)Wall("W_"+z,-.2f,z,90);
   Wall("E_0",4,0,-90);Wall("E_3",4,3,-90);
   for(int x=4;x<8;x++){Wall("CS_"+x,x,.8f,0);Wall("CN_"+x,x,3,180);}
   for(int z=1;z<3;z++)Wall("CE_"+z,8,z,-90);
   Prop("P16-01",2,2,3,true);Prop("P17-02",1.5f,.12f,1.4f,false,true);
   Prop("P18-01",3,3,0);Prop("P19-03",2,1.9f,0);
   Prop("P15-03",3.15f,1f,0);Prop("P18-03",1.1f,3f,0);
   var l=new GameObject("QA_LIGHT").AddComponent<Light>();
   l.type=LightType.Directional;l.intensity=1.2f;l.transform.rotation=Quaternion.Euler(55,-25,0);
   var cam=new GameObject("QA_CAMERA").AddComponent<Camera>();
   cam.tag="MainCamera";cam.transform.position=new Vector3(10,6,-6);
   cam.transform.LookAt(new Vector3(3.7f,1.5f,2f));
   if(!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Scene))
    throw new IOException("Real Unity scene save failed");
   AssetDatabase.SaveAssets();
   var output=Full("C01InteriorProps_QA/PASS29/EDITOR_SCENE_RECEIPT.txt");
   Directory.CreateDirectory(Path.GetDirectoryName(output));
   File.WriteAllText(output,"UNITY="+Application.unityVersion+
    "\nORIGINAL_FBX=9\nWALL_W01=24\nFLOOR_F01=24\nCEILING_C01=24"+
    "\nNO_CLAUDE_DOORS\nQA_DERIVED_MATERIALS_NOT_AUTHORING_APPROVED"+
    "\nMOVING_PHYSX_NOT_APPROVED\nW01_CURRENT_SHA_VERSION_HOLD\n");
  }
 }
 public sealed class W29EditTests {
  [Test]public void OriginalFBXPrefabsAndSceneExist() {
   foreach(var id in new[]{"W01","F01","C01","P16-01","P17-02","P18-01","P19-03","P15-03","P18-03"}) {
    var asset=AssetDatabase.LoadAssetAtPath<GameObject>(
      "Assets/C01InteriorProps/Pass29/Generated/Resources/W29QA/"+id+".prefab");
    Assert.NotNull(asset,"Unity-generated prefab missing "+id);
    Assert.Greater(asset.GetComponentsInChildren<MeshFilter>(true).Length,0);
   }
   Assert.NotNull(AssetDatabase.LoadAssetAtPath<SceneAsset>(W29Room.Scene));
   var s=EditorSceneManager.OpenScene(W29Room.Scene,OpenSceneMode.Single);
   var roots=s.GetRootGameObjects();
   Assert.AreEqual(24,roots.Count(x=>x.name.StartsWith("WALL_")));
   Assert.AreEqual(24,roots.Count(x=>x.name.StartsWith("FLOOR_")));
   Assert.AreEqual(24,roots.Count(x=>x.name.StartsWith("CEILING_")));
  }
 }
}
