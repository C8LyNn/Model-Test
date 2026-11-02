// C01-10 WAVE19 — Unity 6000.3.14f1 URP, QA-only actual native FBX vertical slice.
// Requires PHYSICAL Git-LFS-hydrated, SHA-checked Pass04Incoming FBX, not source stand-ins.
// A test invocation is proof only if the Unity Editor really executes successfully.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using NUnit.Framework;

namespace C01.InteriorProps.Pass19
{
    public static class VerticalSlice
    {
        const string Root = "Assets/C01InteriorProps/Pass19";
        const string Incoming = "Assets/C01InteriorProps/Pass04Incoming";
        const string OutPrefabs = Root + "/Resources/Pass19QA";
        const string OutMaterials = Root + "/Generated/Materials";
        const string OutScenes = Root + "/Generated/Scenes";
        const string ScenePath = OutScenes + "/C01_PASS19_NATIVE_3FBX_QA_ONLY.unity";
        const string CsvPath = "C01InteriorProps_QA/PASS19/UNITY_ACTUAL_3_NATIVE_PREFABS.csv";

        public sealed class Target
        {
            public string Id, Sha;
            public int MinParts, MinTris;
            public Target(string id, string sha, int parts, int tris)
            { Id=id; Sha=sha; MinParts=parts; MinTris=tris; }
        }
        public static readonly Target[] Targets = {
            new Target("P16-01","c0a782a17a0047e0d578a41e42ac714c0fa0f86c7c4960f4bc10e21a24a278fd",12,220),
            new Target("P17-02","db49121a520f16ca636626795550b83e8a4df94ded56a7ccb76308520bb7c3f6",38,536),
            new Target("P18-01","f541d502ba9eaaf5c7a0a7279c44f71f36dd482e3aed3ba0734058dcf1045f6c",47,980)
        };

        static string FullPath(string projectRelative)
        {
            if(Path.IsPathRooted(projectRelative) || projectRelative.Contains(".."))
                throw new InvalidDataException("Unsafe project path");
            return Path.Combine(Path.GetDirectoryName(Application.dataPath),
                projectRelative.Replace('/',Path.DirectorySeparatorChar));
        }
        static string Sha256(string path)
        {
            using(var h=SHA256.Create())
            using(var stream=File.OpenRead(path))
                return BitConverter.ToString(h.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
        }
        static bool IsNativeFbx(string file)
        {
            byte[] magic=System.Text.Encoding.ASCII.GetBytes("Kaydara FBX Binary");
            byte[] bytes=new byte[magic.Length];
            using(var s=File.OpenRead(file))
                return s.Read(bytes,0,bytes.Length)==bytes.Length && bytes.SequenceEqual(magic);
        }
        static void DirectoryAt(string assetFolder)
        {
            Directory.CreateDirectory(FullPath(assetFolder));
        }
        static string EscapeCsv(string value)
        {
            value=value??"";
            return value.IndexOfAny(new[]{',','"','\n','\r'})>=0
                ? "\""+value.Replace("\"","\"\"")+"\"" : value;
        }
        static Shader UrpLit()
        {
            var shader=Shader.Find("Universal Render Pipeline/Lit");
            if(shader==null)throw new InvalidOperationException("URP Lit shader not found: real URP project required");
            return shader;
        }
        static Color ColorFromSource(string sourceName)
        {
            string s=(sourceName??"").ToUpperInvariant();
            if(s.Contains("CAUTION") || s.Contains("YELLOW"))return new Color(.92f,.57f,.11f);
            if(s.Contains("RUBBER"))return new Color(.09f,.11f,.13f);
            if(s.Contains("DARK"))return new Color(.12f,.16f,.20f);
            if(s.Contains("EMISSION") || s.Contains("GLOW"))return new Color(.28f,.82f,1f);
            if(s.Contains("GLASS"))return new Color(.20f,.36f,.43f);
            return new Color(.48f,.54f,.59f);
        }
        static Material MaterialFor(Material src, string id, Shader shader,
                                    Dictionary<string,Material> cache)
        {
            string original=src!=null?src.name:"UNASSIGNED";
            string key=id+"__"+original.Replace('/','_').Replace('\\','_');
            if(cache.ContainsKey(key))return cache[key];
            string path=OutMaterials+"/"+key+".mat";
            var existing=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(existing==null)
            {
                existing=new Material(shader);
                existing.name="QA_ONLY__"+original;
                existing.SetColor("_BaseColor",ColorFromSource(original));
                string upper=original.ToUpperInvariant();
                if(upper.Contains("EMISSION") || upper.Contains("GLOW"))
                {
                    existing.EnableKeyword("_EMISSION");
                    existing.SetColor("_EmissionColor",ColorFromSource(original)*1.75f);
                }
                AssetDatabase.CreateAsset(existing,path);
            }
            else if(existing.shader!=shader)
                throw new InvalidDataException("Existing QA material is not URP Lit: "+path);
            cache[key]=existing;
            return existing;
        }
        static Bounds LocalBounds(GameObject root)
        {
            var meshes=root.GetComponentsInChildren<MeshFilter>(true);
            bool first=true;
            Bounds total=new Bounds();
            foreach(var f in meshes)
            {
                if(f.sharedMesh==null)throw new InvalidDataException("Missing MeshFilter mesh");
                var bounds=f.sharedMesh.bounds;
                foreach(int sx in new[]{-1,1})
                foreach(int sy in new[]{-1,1})
                foreach(int sz in new[]{-1,1})
                {
                    var corner=bounds.center+Vector3.Scale(bounds.extents,new Vector3(sx,sy,sz));
                    var point=root.transform.InverseTransformPoint(f.transform.TransformPoint(corner));
                    if(first){total=new Bounds(point,Vector3.zero);first=false;}
                    else total.Encapsulate(point);
                }
            }
            if(first)throw new InvalidDataException("No real imported mesh geometry");
            return total;
        }

        [MenuItem("C01/Interior Props/PASS19/Build three REAL signed FBX QA-only prefabs")]
        public static void BuildThree()
        {
            if(EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Stop PlayMode");
            if(UnityEngine.SceneManagement.SceneManager.sceneCount>0 &&
               Enumerable.Range(0,UnityEngine.SceneManagement.SceneManager.sceneCount)
               .Any(i=>UnityEngine.SceneManagement.SceneManager.GetSceneAt(i).isDirty))
                throw new InvalidOperationException("Do not overwrite unsaved scenes");
            var pipe=GraphicsSettings.currentRenderPipeline;
            if(pipe==null || pipe.GetType().FullName.IndexOf("Universal",StringComparison.OrdinalIgnoreCase)<0)
                throw new InvalidOperationException("Current render pipeline is not URP");
            var lit=UrpLit();
            DirectoryAt(OutPrefabs);
            DirectoryAt(OutMaterials);
            DirectoryAt(OutScenes);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var cache=new Dictionary<string,Material>(StringComparer.Ordinal);
            var prefabs=new Dictionary<string,GameObject>();
            var lines=new List<string>{
                "asset_id,input_fbx_sha256,unity_version,real_mesh_filters,real_vertices,real_triangles,urp_material_slots,collider_count,prefab_path,scene_path,qa_gate"
            };
            foreach(var target in Targets)
            {
                string source=Incoming+"/"+target.Id+"/"+target.Id+".fbx";
                string physical=FullPath(source);
                if(!File.Exists(physical))
                    throw new FileNotFoundException("Signed real FBX not staged",physical);
                if(!IsNativeFbx(physical)||Sha256(physical)!=target.Sha)
                    throw new InvalidDataException(target.Id+" mismatched full-byte SHA256 / FBX magic");
                var importer=AssetImporter.GetAtPath(source) as ModelImporter;
                if(importer==null)throw new InvalidDataException("Not a Unity ModelImporter: "+source);
                if(!importer.isReadable || importer.importNormals!=ModelImporterNormals.Import ||
                   !importer.preserveHierarchy || importer.meshCompression!=ModelImporterMeshCompression.Off)
                {
                    importer.isReadable=true;
                    importer.importNormals=ModelImporterNormals.Import;
                    importer.preserveHierarchy=true;
                    importer.meshCompression=ModelImporterMeshCompression.Off;
                    importer.SaveAndReimport();
                }
                var model=AssetDatabase.LoadAssetAtPath<GameObject>(source);
                if(model==null)throw new InvalidDataException("Imported FBX missing Unity GameObject: "+source);
                var qa=new GameObject(target.Id+"_REAL_NATIVE_FBX_QA_ONLY");
                try
                {
                    var instance=(GameObject)PrefabUtility.InstantiatePrefab(model);
                    instance.name="SIGNED_ORIGINAL_"+target.Id;
                    instance.transform.SetParent(qa.transform,false);
                    var filters=qa.GetComponentsInChildren<MeshFilter>(true);
                    int tris=0,vertices=0;
                    foreach(var f in filters)
                    {
                        if(f.sharedMesh==null || !f.sharedMesh.isReadable)
                            throw new InvalidDataException(target.Id+" unreadable real source mesh");
                        var mesh=f.sharedMesh;
                        vertices+=mesh.vertexCount;
                        if(mesh.uv==null || mesh.uv.Length!=mesh.vertexCount ||
                           mesh.normals==null || mesh.normals.Length!=mesh.vertexCount)
                            throw new InvalidDataException(target.Id+" missing Unity imported UV0/normals");
                        for(int sub=0;sub<mesh.subMeshCount;sub++)
                        {
                            var ix=mesh.GetTriangles(sub);
                            tris+=ix.Length/3;
                            var p=mesh.vertices;
                            for(int i=0;i<ix.Length;i+=3)
                            {
                                if(Vector3.Cross(p[ix[i+1]]-p[ix[i]],p[ix[i+2]]-p[ix[i]]).sqrMagnitude<=1e-14f)
                                    throw new InvalidDataException(target.Id+" degenerate imported triangle");
                            }
                        }
                    }
                    if(filters.Length<target.MinParts || tris<target.MinTris)
                        throw new InvalidDataException(target.Id+" lost native geometry at Unity import: "+
                            filters.Length+"/"+tris);
                    int materialSlots=0;
                    foreach(var renderer in qa.GetComponentsInChildren<MeshRenderer>(true))
                    {
                        var originals=renderer.sharedMaterials;
                        var replacements=new Material[originals.Length];
                        for(int i=0;i<originals.Length;i++)
                            replacements[i]=MaterialFor(originals[i],target.Id,lit,cache);
                        renderer.sharedMaterials=replacements;
                        materialSlots+=replacements.Length;
                    }
                    Bounds bounds=LocalBounds(qa);
                    if(bounds.size.sqrMagnitude<=0)throw new InvalidDataException("Zero-size real model");
                    // Non-primitive QA-only bounding collider, not final physical authoring.
                    var collider=qa.AddComponent<BoxCollider>();
                    collider.center=bounds.center;
                    collider.size=bounds.size;
                    if(target.Id=="P16-01")
                    {
                        var fixture=new GameObject("QA_ONLY_LightComponent");
                        fixture.transform.SetParent(qa.transform,false);
                        var light=fixture.AddComponent<Light>();
                        light.type=LightType.Point;
                        light.range=3f;
                        light.intensity=1.8f;
                        light.color=new Color(.55f,.79f,1f);
                    }
                    string prefabPath=OutPrefabs+"/"+target.Id+".prefab";
                    var prefab=PrefabUtility.SaveAsPrefabAsset(qa,prefabPath);
                    if(prefab==null)throw new IOException("Unity prefab save failed: "+prefabPath);
                    prefabs[target.Id]=prefab;
                    string[] row={target.Id,target.Sha,Application.unityVersion,
                        filters.Length.ToString(),vertices.ToString(),tris.ToString(),
                        materialSlots.ToString(),"1",prefabPath,ScenePath,"QUARANTINE_ONLY_C01_02_PENDING"};
                    lines.Add(string.Join(",",row.Select(EscapeCsv)));
                }
                finally {UnityEngine.Object.DestroyImmediate(qa);}
            }
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var sceneRoot=new GameObject("C01_PASS19_REAL_3FBX_QUARANTINE_NO_SHIP_CHANGES");
            for(int i=0;i<Targets.Length;i++)
            {
                var target=Targets[i];
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[target.Id],sceneRoot.transform);
                instance.transform.localPosition=new Vector3((i-1)*2.8f,0,0);
                instance.transform.localRotation=Quaternion.identity;
                instance.transform.localScale=Vector3.one;
            }
            var fill=new GameObject("QA_Inspection_Directional_Light").AddComponent<Light>();
            fill.type=LightType.Directional;
            fill.intensity=1.0f;
            fill.transform.rotation=Quaternion.Euler(45,-25,0);
            var camera=new GameObject("QA_Inspection_Camera").AddComponent<Camera>();
            camera.tag="MainCamera";
            camera.transform.position=new Vector3(4.2f,3.2f,-6.8f);
            camera.transform.LookAt(new Vector3(0,0.55f,0));
            camera.clearFlags=CameraClearFlags.SolidColor;
            camera.backgroundColor=new Color(.07f,.085f,.105f);
            camera.fieldOfView=50;
            if(!EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),ScenePath))
                throw new IOException("Unable to persist isolated test scene");
            AssetDatabase.SaveAssets();
            string output=FullPath(CsvPath);
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            File.WriteAllLines(output,lines);
            Debug.Log("[C01-10 W19] REAL UNITY 6 URP THREE-NATIVE VERTICAL SLICE BUILT; "+
                "signed FBX 3/3 and native QA-only prefabs 3/3, one isolated scene. "+
                "PER-MODEL C01-02 FINAL QA PENDING, NO RELEASE, NO SHIP SCENE EDIT. CSV="+CsvPath);
        }
    }

    // Executes in the actual Unity Test Framework EditMode runner, never by Python.
    public sealed class ThreeNativeEditModeTests
    {
        [Test]
        public void BuildsThreeSignedNativeSourcePrefabsAndIsolatedScene()
        {
            VerticalSlice.BuildThree();
            foreach(var t in VerticalSlice.Targets)
            {
                var path="Assets/C01InteriorProps/Pass19/Resources/Pass19QA/"+t.Id+".prefab";
                var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                Assert.NotNull(prefab,"Missing REAL Unity prefab: "+t.Id);
                Assert.GreaterOrEqual(prefab.GetComponentsInChildren<MeshFilter>(true).Length,t.MinParts);
                Assert.AreEqual(1,prefab.GetComponentsInChildren<BoxCollider>(true).Length,
                    "Diagnostic single bounding collider only");
            }
            Assert.NotNull(AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(
                "Assets/C01InteriorProps/Pass19/Generated/Scenes/C01_PASS19_NATIVE_3FBX_QA_ONLY.unity"));
        }
    }
}
