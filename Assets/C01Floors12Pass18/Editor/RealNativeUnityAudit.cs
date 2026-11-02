// C01-12 DETAIL PASS18 — manual Unity 6000.3.14f1 URP integration gate.
// Explicitly invoked only. Creates QA-only prefabs under Assets/C01Floors12Pass18.
// Never changes ship scenes, existing prefabs, project render pipeline or build settings.
// The code itself is NOT evidence of a Unity test until its batch/editor method succeeds.
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace C01.Floors12Pass18.Editor
{
    public static class RealNativeUnityAudit
    {
        const string Output = "Assets/C01Floors12Pass18/Generated";
        const string Root = "C01StandaloneKits/FloorCeiling/DetailPass17";
        const float Tol = .005f;
        class Model
        {
            public string id, stem, fbxHash;
            public float minY, maxY;
            public Model(string id, string stem, string sha, float low, float high)
            { this.id=id; this.stem=stem; fbxHash=sha; minY=low; maxY=high; }
        }
        // Exact current PASS17 binary SHA, NOT a Git blob SHA and NOT a stale v003 FBX.
        static readonly Model[] Models = {
            new Model("F01","C01_SHI_F01_FLOOR_BASIC","46acac987ca3f8387472b2dc8b611cd871c90cd3e7d4773568c9005c84cb5c09",-.2f,0),
            new Model("F02","C01_SHI_F02_FLOOR_MARKED","229d88a2471fb27e48e62a7c81396f935b45e6ae548ce9d2540908ef63932782",-.2f,0),
            new Model("C01","C01_SHI_C01_CEILING_BASIC","632135269d3ac8893a273b364e23aac088c09494011d1d79dc2ca511394344e6",3f,3.2f)
        };
        [Serializable] class Entry {
            public string id, importedFbxSha256, prefabPath, status;
            public int triangleCount, renderers, colliders;
            public Vector3 min, max;
            public List<string> errors = new List<string>();
        }
        [Serializable] class Report {
            public string unityVersion, renderPipeline, status, independentC0102Final="PENDING";
            public string testMode="EXPLICIT_UNITY_EDITOR_EXECUTION";
            public string productionUrpPbrTextureAndNormalMapValidation="NOT_RUN";
            public string shipIntegrationClearanceAndPlayMode="NOT_RUN";
            public List<Entry> models=new List<Entry>();
            public List<string> errors=new List<string>();
        }
        static string Project => Directory.GetParent(Application.dataPath).FullName;
        static string Disk(string rel) => Path.Combine(Project, rel.Replace('/', Path.DirectorySeparatorChar));
        static string SHA256File(string path) {
            using(var sha=SHA256.Create())
            using(var stream=File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
        static void Require(bool ok, string message) {
            if(!ok) throw new InvalidOperationException(message);
        }
        static void EnsureAssetDir(string path) {
            if(!Directory.Exists(Disk(path))) Directory.CreateDirectory(Disk(path));
        }
        // W20: fail the entire three-model intake BEFORE creating even one staged FBX.
        // A stale second or third model must never leave a partially admitted first prefab.
        static void PreflightAllThreeImmutableInputs() {
            Require(Models.Length==3, "Expected exactly 3 historical QA-only model IDs");
            Require(Models.Select(m=>m.id).Distinct().Count()==3, "Duplicate model ID");
            foreach (var m in Models) {
                string src=Disk(Root+"/FBX/"+m.stem+"_v004.fbx");
                Require(File.Exists(src),m.id+" current source FBX missing; hydrate LFS first");
                var file=new FileInfo(src);
                Require(file.Length>1000,m.id+" FBX is empty or a Git LFS pointer");
                Require(SHA256File(src)==m.fbxHash,m.id+" immutable source FBX SHA256 mismatch");
                // Fail closed on all three existing stage slots before copying any model.
                string alreadyStaged=Disk(Output+"/Models/"+m.stem+"_v004.fbx");
                if(File.Exists(alreadyStaged))
                    Require(SHA256File(alreadyStaged)==m.fbxHash,
                        m.id+" incompatible/stale staged FBX; no automatic overwrite");
            }
        }
        static Bounds WorldToRootBounds(Transform root, IEnumerable<MeshFilter> filters) {
            Bounds result=default;bool first=true;
            foreach(var filter in filters){
                var m=filter.sharedMesh;
                Require(m!=null,"Missing imported mesh");
                foreach(var p in m.vertices){
                    var local=root.InverseTransformPoint(filter.transform.TransformPoint(p));
                    if(first){result=new Bounds(local,Vector3.zero);first=false;}
                    else result.Encapsulate(local);
                }
            }
            Require(!first,"No imported vertices");
            return result;
        }
        static void AuditMesh(Mesh mesh, string id) {
            Require(mesh!=null,id+" null sharedMesh");
            var triangles=mesh.triangles;
            Require(triangles.Length>0&&triangles.Length%3==0,id+" invalid triangle index array");
            Require(mesh.normals.Length==mesh.vertexCount,id+" missing normal array");
            Require(mesh.uv.Length==mesh.vertexCount,id+" missing/partial UV0 array");
            var vertices=mesh.vertices;var uv=mesh.uv;
            for(int i=0;i<triangles.Length;i+=3){
                int a=triangles[i],b=triangles[i+1],c=triangles[i+2];
                Require(a>=0&&b>=0&&c>=0&&a<vertices.Length&&b<vertices.Length&&c<vertices.Length,id+" invalid triangle index");
                Require(Vector3.Cross(vertices[b]-vertices[a],vertices[c]-vertices[a]).sqrMagnitude>1e-15f,id+" degenerate XYZ face");
                Vector2 u=uv[b]-uv[a],v=uv[c]-uv[a];
                Require(Mathf.Abs(u.x*v.y-u.y*v.x)>1e-10f,id+" degenerate UV0");
            }
        }
        static void AssertBounds(Bounds bounds, Model m){
            Require(Mathf.Abs(bounds.size.x-1f)<Tol && Mathf.Abs(bounds.size.z-1f)<Tol,m.id+" footprint not 1x1 Unity XZ");
            Require(Mathf.Abs(bounds.min.y-m.minY)<Tol && Mathf.Abs(bounds.max.y-m.maxY)<Tol,m.id+" vertical orientation/bounds wrong");
            Require(Mathf.Abs(bounds.min.x)<Tol && Mathf.Abs(bounds.max.x-1f)<Tol,m.id+" pivot X moved");
            // Source Y is -1..0 in Blender; Unity's depth-axis sign is importer-dependent.
            Require(Mathf.Abs(bounds.size.y-.2f)<Tol,m.id+" panel thickness changed");
        }
        static Entry StageOne(Model m, Scene preview){
            var entry=new Entry{id=m.id,status="RUNNING"};
            string src=Disk(Root+"/FBX/"+m.stem+"_v004.fbx");
            Require(File.Exists(src),m.id+" source FBX not found; git lfs pull needed");
            Require(SHA256File(src)==m.fbxHash,m.id+" source FBX SHA mismatch, FAIL CLOSED");
            var target=Output+"/Models/"+m.stem+"_v004.fbx";
            var destination=Disk(target);
            if(File.Exists(destination))Require(SHA256File(destination)==m.fbxHash,m.id+" stale staged model—quarantined; delete manually after audit");
            else File.Copy(src,destination);
            AssetDatabase.ImportAsset(target,ImportAssetOptions.ForceSynchronousImport);
            var importer=AssetImporter.GetAtPath(target) as ModelImporter;
            Require(importer!=null,m.id+" missing Unity FBX importer");
            importer.globalScale=1;
            importer.useFileScale=true;
            importer.importAnimation=false;
            importer.importCameras=false;
            importer.importLights=false;
            importer.isReadable=true;
            importer.importNormals=ModelImporterNormals.Import;
            importer.SaveAndReimport();
            entry.importedFbxSha256=SHA256File(destination);
            var source=AssetDatabase.LoadAssetAtPath<GameObject>(target);
            Require(source!=null,m.id+" model import returned null");
            var root=new GameObject("PASS18_QA_"+m.id);
            SceneManager.MoveGameObjectToScene(root,preview);
            try {
                var imported=(GameObject)PrefabUtility.InstantiatePrefab(source,preview);
                Require(imported!=null,m.id+" cannot instantiate imported FBX");
                imported.transform.SetParent(root.transform,false);
                imported.transform.localPosition=Vector3.zero;
                imported.transform.localRotation=Quaternion.identity;
                imported.transform.localScale=Vector3.one;
                var meshFilters=imported.GetComponentsInChildren<MeshFilter>(true);
                var renderers=imported.GetComponentsInChildren<MeshRenderer>(true);
                Require(meshFilters.Length>0&&renderers.Length>0,m.id+" no imported meshes/renderers");
                int tris=0;
                foreach(var f in meshFilters){AuditMesh(f.sharedMesh,m.id);tris+=f.sharedMesh.triangles.Length/3;}
                Require(tris==28,m.id+" expected true v004 28 triangles but Unity imported "+tris);
                var b=WorldToRootBounds(root.transform,meshFilters);
                AssertBounds(b,m);
                var collider=root.AddComponent<BoxCollider>();
                collider.center=b.center;collider.size=b.size;
                Require(collider.size.y>0 && collider.size.x>0 && collider.size.z>0,m.id+" invalid box collider");
                entry.triangleCount=tris;entry.renderers=renderers.Length;entry.colliders=1;entry.min=b.min;entry.max=b.max;
                var prefab=Output+"/Prefabs/"+m.stem+"_PASS18_QA.prefab";
                var saved=PrefabUtility.SaveAsPrefabAsset(root,prefab);
                Require(saved!=null,m.id+" prefab was not serialized");
                entry.prefabPath=prefab;entry.status="PASS_QA_ONLY";
                return entry;
            } finally {UnityEngine.Object.DestroyImmediate(root);}
        }
        [MenuItem("Tools/C01/Floors & Ceilings/PASS18 Stage QA-only FBX prefabs and validate")]
        public static void Run() {
            var report=new Report{unityVersion=Application.unityVersion,
                renderPipeline=GraphicsSettings.currentRenderPipeline?.GetType().FullName ?? "NONE",status="FAIL"};
            string output=Disk("Library/C01Floors12/PASS18_REAL_UNITY_IMPORT_QA.json");
            Scene preview=default;
            try {
                Require(Application.unityVersion.StartsWith("6000.3."),"Expected Unity 6000.3.x actual Editor");
                Require(GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset,
                    "URP renderer is not active");
                // Read-only, all-or-nothing SHA gate BEFORE directory/asset mutations.
                PreflightAllThreeImmutableInputs();
                EnsureAssetDir(Output+"/Models");EnsureAssetDir(Output+"/Prefabs");
                preview=EditorSceneManager.NewPreviewScene();
                foreach(var model in Models) report.models.Add(StageOne(model,preview));
                AssetDatabase.SaveAssets();
                report.status="PASS_QA_ONLY";
            } catch(Exception ex) {
                report.errors.Add(ex.ToString()); Debug.LogError("C01-12 PASS18 Unity QA FAIL: "+ex);
            } finally {
                if(preview.IsValid()) EditorSceneManager.ClosePreviewScene(preview);
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                File.WriteAllText(output,JsonUtility.ToJson(report,true)+"\n");
                Debug.Log("C01-12 PASS18 Unity QA status="+report.status+" / "+output+
                    " — C01-02 FINAL APPROVAL remains PENDING");
            }
            if(report.status!="PASS_QA_ONLY")throw new InvalidOperationException("C01-12 Unity import QA failed; see Library/C01Floors12 report");
        }
    }
}
#endif
