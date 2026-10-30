// C01-10 PASS04 — truthful source-FBX Unity 6 import and quarantine inspection.
// Not a production approval. Independent C01-02 QA remains authoritative.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace C01.InteriorProps.Editor
{
    public static class Pass04SourceImportAudit
    {
        const string AssetRoot = "Assets/C01InteriorProps";
        const string QuarantineRoot = AssetRoot + "/Pass04Quarantine";
        const string PrefabRoot = QuarantineRoot + "/Prefabs";
        const string SceneRoot = QuarantineRoot + "/Scenes";
        const string SceneName = "C01_PASS04_FBX_Source_Inspection";
        const string EvidenceDirectory = "C01InteriorProps_QA/PASS04";
        const float TriangleCrossSquaredTolerance = 1e-14f;

        // Explicit 36-ID scope; no Wave03 and no structural models.
        static readonly string[] Ids = {
            "P15-01","P15-02","P15-03","P15-04","P15-05","P15-06","P15-07",
            "P16-01","P16-02","P16-03","P16-04","P16-05","P16-06","P16-07",
            "P17-01","P17-02","P17-03","P17-04","P17-05","P17-06","P17-07",
            "P18-01","P18-02","P18-03","P18-04","P18-05","P18-06","P18-07",
            "P19-01","P19-02","P19-03","P19-04","P19-05","P19-06","P19-07","P19-08"
        };

        static readonly Regex IdPrefix = new Regex(
            @"^(P(?:15|16|17|18|19)-0[1-8])($|[_-])",
            RegexOptions.Compiled | RegexOptions.CultureInvariant | RegexOptions.IgnoreCase);

        [Serializable]
        sealed class SourceStageManifest
        {
            public SourceStageAsset[] assets;
        }

        [Serializable]
        sealed class SourceStageAsset
        {
            public string id;
            public string source_commit;
            public string native_export_sync;
        }

        sealed class Source
        {
            public string Id;
            public string Path;
            public string Sha256;
            public int Bytes;
            public int MeshCount;
            public long VertexEntries;
            public long TriangleCount;
            public long DegenerateTriangles;
            public int UvMissing;
            public int NormalsMissing;
            public int MaterialsMissing;
            public int NonUrpMaterials;
            public int SourceColliders;
            public int MovingPartCandidates;
            public string RootTransforms;
            public string Status;
            public string Diagnostics;
            public GameObject Imported;
        }

        static string ProjectRoot { get { return Path.GetFullPath(Path.Combine(Application.dataPath,"..")); } }
        static string Absolute(string assetPath)
        {
            if (!assetPath.StartsWith("Assets/",StringComparison.Ordinal) ||
                assetPath.Contains("..") || Path.IsPathRooted(assetPath))
                throw new InvalidDataException("Invalid Unity asset path: "+assetPath);
            return Path.Combine(ProjectRoot,assetPath.Replace('/',Path.DirectorySeparatorChar));
        }
        static string ToAssetPath(string absolute)
        {
            var full=Path.GetFullPath(absolute).Replace('\\','/');
            var data=Application.dataPath.Replace('\\','/');
            if(!full.StartsWith(data+"/",StringComparison.Ordinal))
                throw new InvalidDataException("Outside Assets: "+full);
            return "Assets/"+full.Substring(data.Length+1);
        }
        static string Sha(string file)
        {
            using(var reader=File.OpenRead(file))
            using(var sha=SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(reader)).Replace("-","").ToLowerInvariant();
        }
        static bool HasBinaryFbxMagic(string file)
        {
            var magic=Encoding.ASCII.GetBytes("Kaydara FBX Binary");
            byte[] buf=new byte[magic.Length];
            using(var f=File.OpenRead(file))
                if(f.Read(buf,0,buf.Length)!=buf.Length)return false;
            return buf.SequenceEqual(magic);
        }
        static Dictionary<string,List<string>> Discover()
        {
            // Never scan the whole Assets folder: it can contain historical BEFORE
            // exports, producer source and duplicates of the exact same asset ID.
            // Only the explicitly staged, hydrated binary FBX is eligible.
            var result=Ids.ToDictionary(s=>s,s=>new List<string>(),StringComparer.OrdinalIgnoreCase);
            foreach(string id in Ids)
            {
                string expected=AssetRoot+"/Pass04Incoming/"+id+"/"+id+".fbx";
                if(File.Exists(Absolute(expected)))result[id].Add(expected);
            }
            return result;
        }
        static string ValidateStagingReceipt(string id,string sha)
        {
            // This is source provenance, NOT independent C01-02 approval.
            string report=Path.Combine(ProjectRoot,"C01InteriorProps_QA","PASS04","staged_sources.csv");
            if(!File.Exists(report))return "MISSING_STAGING_SHA_RECEIPT";
            string[] rows=File.ReadAllLines(report);
            if(rows.Length==0 || rows[0].Trim()!="id,state,source_commit,fbx_sha256,size_bytes,detail")
                return "STAGING_RECEIPT_SCHEMA_INVALID";
            string[] matched=rows.Skip(1).Where(line=>line.StartsWith(id+",",StringComparison.Ordinal)).ToArray();
            if(matched.Length!=1)return "STAGING_RECEIPT_ID_MISSING_OR_DUPLICATE";
            string[] fields=matched[0].Split(new[]{','},6);
            if(fields.Length<6 || fields[1]!="STAGED_SOURCE_NOT_QA_APPROVED")
                return "STAGING_RECEIPT_STATUS_NOT_STAGED";
            if(!String.Equals(fields[3],sha,StringComparison.OrdinalIgnoreCase))
                return "STAGING_RECEIPT_SHA_MISMATCH";
            // Receipt must match the *current pinned producer revision*, not merely
            // an old file+receipt pair left in Pass04Incoming by a previous wave.
            string manifestFile=Path.Combine(ProjectRoot,"C01InteriorProps","Pass04","source_stage_36.json");
            if(!File.Exists(manifestFile))return "MISSING_CURRENT_SOURCE_MANIFEST";
            SourceStageManifest manifest;
            try {
                manifest=JsonUtility.FromJson<SourceStageManifest>(File.ReadAllText(manifestFile));
            } catch(Exception) { return "INVALID_CURRENT_SOURCE_MANIFEST"; }
            if(manifest==null || manifest.assets==null || manifest.assets.Length!=Ids.Length)
                return "INCOMPLETE_CURRENT_SOURCE_MANIFEST";
            var expected=manifest.assets.Where(x=>x!=null &&
                String.Equals(x.id,id,StringComparison.Ordinal)).ToArray();
            if(expected.Length!=1 || String.IsNullOrEmpty(expected[0].source_commit) ||
               !Regex.IsMatch(expected[0].source_commit,@"\A[0-9a-f]{40}\z"))
                return "AMBIGUOUS_OR_INVALID_CURRENT_SOURCE_COMMIT";
            // Protect against a copied old FBX and a matching old receipt when
            // the *current* producer authoring source still needs a DETAIL
            // PASS12 native Blender save/export roundtrip. Exact Git commit or
            // byte SHA by itself cannot certify authoring/export parity.
            if(!String.Equals(expected[0].native_export_sync,
                "CANDIDATE_BINARY_FBX_QA_NOT_APPROVED",StringComparison.Ordinal))
                return "SOURCE_NATIVE_EXPORT_BLOCKED_BY_MANIFEST";
            if(!String.Equals(expected[0].source_commit,fields[2],StringComparison.Ordinal))
                return "STAGING_RECEIPT_PRODUCER_COMMIT_STALE";
            if(!String.Equals(fields[5].Replace('\\','/'),
                AssetRoot+"/Pass04Incoming/"+id+"/"+id+".fbx",StringComparison.Ordinal))
                return "STAGING_RECEIPT_PATH_MISMATCH";
            return "";
        }
        // Certain models intentionally export multiple FBX subparts. Only the exact
        // Pxx-yy.fbx is assumed to be the canonical source; never conflate parts.
        static string ChooseSource(string id,List<string> candidates,out string error)
        {
            error="";
            if(candidates.Count==0){error="MISSING_BINARY_FBX_IN_UNITY_ASSETS";return null;}
            var exact=candidates.Where(x=>Path.GetFileNameWithoutExtension(x)
                .Equals(id,StringComparison.OrdinalIgnoreCase)).ToArray();
            if(exact.Length!=1)
            {
                error=exact.Length==0 ? "AMBIGUOUS_SUBPART_EXPORTS_NO_EXACT_ROOT_FBX" :
                                       "DUPLICATE_CANONICAL_FBX";
                return null;
            }
            return exact[0];
        }
        static bool Finite(Vector3 p)
        {
            return !(float.IsNaN(p.x)||float.IsNaN(p.y)||float.IsNaN(p.z)||
                     float.IsInfinity(p.x)||float.IsInfinity(p.y)||float.IsInfinity(p.z));
        }
        static Source Inspect(string id,string path)
        {
            var r=new Source{Id=id,Path=path,Status="SOURCE_PRECHECK_NOT_RUN",Diagnostics=""};
            var defects=new List<string>();
            if(string.IsNullOrEmpty(path)){r.Status="BLOCKED";r.Diagnostics="NO_CANONICAL_FBX";return r;}
            var absolute=Absolute(path);
            r.Bytes=(int)Math.Min(int.MaxValue,new FileInfo(absolute).Length);
            r.Sha256=Sha(absolute);
            string receiptError=ValidateStagingReceipt(id,r.Sha256);
            if(receiptError!="")defects.Add(receiptError);
            if(!HasBinaryFbxMagic(absolute)){
                r.Status="FAIL";r.Diagnostics="NOT_REAL_BINARY_FBX_OR_LFS_POINTER";return r;
            }
            if(r.Bytes<200){r.Status="FAIL";r.Diagnostics="FBX_TOO_SMALL";return r;}
            var importer=AssetImporter.GetAtPath(path) as ModelImporter;
            if(importer==null){r.Status="BLOCKED";r.Diagnostics="MODEL_IMPORTER_NOT_AVAILABLE";return r;}
            r.Imported=AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if(r.Imported==null){r.Status="BLOCKED";r.Diagnostics="MODEL_ASSET_NOT_IMPORTED";return r;}
            // Inspect the imported FBX asset directly. InstantiatePrefab in the
            // user's active scene would mark it dirty, even if later destroyed.
            // No hierarchy/mesh data is modified during this read-only preflight.
            var inst=r.Imported;
            try {
                r.RootTransforms="pos="+inst.transform.localPosition.ToString("F5")+
                    " rot="+inst.transform.localRotation.eulerAngles.ToString("F5")+
                    " scale="+inst.transform.localScale.ToString("F5");
                if((inst.transform.localScale-Vector3.one).sqrMagnitude>1e-8f)
                    defects.Add("ROOT_SCALE_NOT_ONE");
                var filters=inst.GetComponentsInChildren<MeshFilter>(true);
                if(filters.Length==0)defects.Add("NO_MESHFILTERS");
                r.SourceColliders=inst.GetComponentsInChildren<Collider>(true).Length;
                foreach(var filter in filters)
                {
                    var mesh=filter.sharedMesh;
                    if(mesh==null){defects.Add("NULL_SHARED_MESH");continue;}
                    r.MeshCount++;
                    r.VertexEntries+=mesh.vertexCount;
                    for(var sub=0;sub<mesh.subMeshCount;sub++)
                    {
                        long indexCount=(long)mesh.GetIndexCount(sub);
                        if(indexCount%3!=0 || mesh.GetTopology(sub)!=MeshTopology.Triangles)
                        {defects.Add("NON_TRIANGLE_SUBMESH");continue;}
                        r.TriangleCount+=indexCount/3;
                    }
                    if(!mesh.isReadable)
                    {
                        defects.Add("NOT_RUN_VERTEX_AUDIT_MESH_UNREADABLE:"+filter.name);
                        continue; // NEVER toggle source importer flags silently
                    }
                    var positions=mesh.vertices;
                    var normals=mesh.normals;
                    var uv=mesh.uv;
                    if(normals==null||normals.Length!=positions.Length)r.NormalsMissing++;
                    if(uv==null||uv.Length!=positions.Length)r.UvMissing++;
                    if(positions.Any(v=>!Finite(v)))defects.Add("NONFINITE_VERTEX");
                    for(var sub=0;sub<mesh.subMeshCount;sub++)
                    {
                        if(mesh.GetTopology(sub)!=MeshTopology.Triangles)continue;
                        var indices=mesh.GetIndices(sub);
                        for(int t=0;t+2<indices.Length;t+=3)
                        {
                            int a=indices[t],b=indices[t+1],c=indices[t+2];
                            if(a>=positions.Length||b>=positions.Length||c>=positions.Length||
                               a<0||b<0||c<0){defects.Add("INDEX_OUT_OF_RANGE");continue;}
                            if(Vector3.Cross(positions[b]-positions[a],positions[c]-positions[a])
                               .sqrMagnitude<=TriangleCrossSquaredTolerance)
                                r.DegenerateTriangles++;
                        }
                    }
                    var name=filter.name.ToLowerInvariant();
                    if(name.Contains("hinge")||name.Contains("pivot")||name.Contains("rotor")||
                       name.Contains("wheel")||name.Contains("lever"))
                        r.MovingPartCandidates++;
                }
                foreach(var renderer in inst.GetComponentsInChildren<MeshRenderer>(true))
                    foreach(var material in renderer.sharedMaterials)
                    {
                        if(material==null){r.MaterialsMissing++;continue;}
                        var sh=material.shader;
                        if(sh==null){r.MaterialsMissing++;continue;}
                        var shader=sh.name;
                        if(!shader.StartsWith("Universal Render Pipeline/",StringComparison.Ordinal) &&
                           !shader.StartsWith("Shader Graphs/",StringComparison.Ordinal))
                            r.NonUrpMaterials++;
                    }
                if(r.UvMissing>0)defects.Add("UV0_MISSING");
                if(r.NormalsMissing>0)defects.Add("NORMALS_MISSING");
                if(r.DegenerateTriangles>0)defects.Add("DEGENERATE_TRIANGLES");
                if(r.MaterialsMissing>0)defects.Add("MATERIAL_SLOT_EMPTY");
                if(r.NonUrpMaterials>0)defects.Add("MATERIAL_NOT_URP_REVIEW");
            }
            catch(Exception ex){defects.Add("UNITY_MESH_EXCEPTION:"+ex.GetType().Name+":"+ex.Message);}
            r.Diagnostics=String.Join(";",defects.Distinct().ToArray());
            r.Status=defects.Count==0?"SOURCE_PRECHECK_PASS":"SOURCE_PRECHECK_FAIL_OR_INCOMPLETE";
            return r;
        }
        static List<Source> Collect()
        {
            var discover=Discover();
            var rows=new List<Source>();
            foreach(var id in Ids)
            {
                string err;
                var chosen=ChooseSource(id,discover[id],out err);
                var row=Inspect(id,chosen);
                if(err!=""){row.Status="BLOCKED";row.Diagnostics=err;}
                rows.Add(row);
            }
            return rows;
        }
        static string Escape(string v){return "\""+(v??"").Replace("\"","\"\"").Replace("\n"," ")+"\"";}
        static void WriteCsv(List<Source> rows)
        {
            var dir=Path.Combine(ProjectRoot,EvidenceDirectory.Replace('/',Path.DirectorySeparatorChar));
            Directory.CreateDirectory(dir);
            var lines=new List<string>{
                "asset_id,status,fbx_path,source_sha256,bytes,mesh_parts,vertex_entries,triangles,degenerate_triangles,missing_uv_meshes,missing_normal_meshes,material_missing,non_urp_materials,source_colliders,moving_part_name_candidates,root_transform,diagnostics,blender_roundtrip,unity_playmode,independent_c01_02_qa"
            };
            foreach(var s in rows)
                lines.Add(String.Join(",",new[]{
                    s.Id,s.Status,Escape(s.Path),s.Sha256??"",s.Bytes.ToString(CultureInfo.InvariantCulture),
                    s.MeshCount.ToString(),s.VertexEntries.ToString(),s.TriangleCount.ToString(),
                    s.DegenerateTriangles.ToString(),s.UvMissing.ToString(),s.NormalsMissing.ToString(),
                    s.MaterialsMissing.ToString(),s.NonUrpMaterials.ToString(),s.SourceColliders.ToString(),
                    s.MovingPartCandidates.ToString(),Escape(s.RootTransforms),Escape(s.Diagnostics),
                    "NOT_RUN_BY_C01_10","NOT_RUN","PENDING"
                }));
            File.WriteAllLines(Path.Combine(dir,"36_FBX_UNITY_IMPORT_AUDIT.csv"),lines);
        }
        // Explicit opt-in: modifies importer settings ONLY on copied QA staging FBX.
        // The producer branch and authored FBX bytes remain untouched.
        [MenuItem("C01/Mesh Repair PASS04/00 — Enable Readable on Staged Copies")]
        public static void PrepareReadableStagedCopies()
        {
            string root=AssetRoot+"/Pass04Incoming/";
            string absolute=Absolute(root+".");
            if(!Directory.Exists(absolute))
                throw new DirectoryNotFoundException("No staged QA FBX copies: "+root);
            int adjusted=0;
            foreach(var fbx in Directory.GetFiles(absolute,"*.fbx",SearchOption.AllDirectories))
            {
                var assetPath=ToAssetPath(fbx);
                var importer=AssetImporter.GetAtPath(assetPath) as ModelImporter;
                if(importer==null)continue;
                if(!importer.isReadable)
                {
                    importer.isReadable=true;
                    importer.SaveAndReimport(); // staging .meta only
                    adjusted++;
                }
            }
            Debug.Log("[C01-10] Set Read/Write for "+adjusted+
                " STAGED source copies only. Production owner FBX source unchanged.");
        }
        [MenuItem("C01/Mesh Repair PASS04/01 — Audit 36 Source FBX")]
        public static void Audit()
        {
            var rows=Collect();
            WriteCsv(rows);
            Debug.Log("[C01-10] PASS04: source-import precheck "+
               rows.Count(x=>x.Status=="SOURCE_PRECHECK_PASS")+"/"+Ids.Length+
               "; details C01InteriorProps_QA/PASS04/36_FBX_UNITY_IMPORT_AUDIT.csv. "+
               "Blender/PlayMode/independent QA NOT RUN.");
        }
        static void EnsureDirectory(string path)
        {
            Directory.CreateDirectory(Absolute(path+"/.").TrimEnd('.',Path.DirectorySeparatorChar));
        }
        static void AddPreviewColliders(GameObject root)
        {
            foreach(var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if(filter.sharedMesh==null)continue;
                if(filter.GetComponent<Collider>()!=null)continue;
                var c=filter.gameObject.AddComponent<MeshCollider>();
                c.sharedMesh=filter.sharedMesh;
                c.convex=false; // purely static diagnostic: not approved gameplay collider
            }
        }
        [MenuItem("C01/Mesh Repair PASS04/02 — Build Quarantine Prefabs and Scene")]
        public static void BuildQuarantine()
        {
            if(EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Stop Play Mode before importer QA.");
            if(Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty))
                throw new InvalidOperationException("Save dirty scenes before diagnostic generation.");
            var rows=Collect();WriteCsv(rows);
            var usable=rows.Where(x=>x.Status=="SOURCE_PRECHECK_PASS").ToArray();
            if(usable.Length==0)
                throw new InvalidOperationException("No fully inspected binary FBX sources. "+
                    "Use supplier LFS/CI hydrated files and ensure mesh read/write is available. "+
                    "No placeholders generated.");
            EnsureDirectory(PrefabRoot);EnsureDirectory(SceneRoot);
            AssetDatabase.Refresh();
            var prefabs=new Dictionary<string,GameObject>();
            foreach(var s in usable)
            {
                var root=new GameObject(s.Id+"_QA_ONLY");
                try {
                    var imported=(GameObject)PrefabUtility.InstantiatePrefab(s.Imported);
                    imported.name="ORIGINAL_SOURCE_"+s.Id;
                    imported.transform.SetParent(root.transform,false);
                    AddPreviewColliders(root);
                    var output=PrefabRoot+"/"+s.Id+"_QA_ONLY.prefab";
                    var saved=PrefabUtility.SaveAsPrefabAsset(root,output);
                    if(saved==null)throw new IOException("Unity could not save diagnostic prefab "+output);
                    prefabs[s.Id]=saved;
                } finally {UnityEngine.Object.DestroyImmediate(root);}
            }
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var master=new GameObject("C01_PASS04_SOURCE_FBX_QUARANTINE_NOT_APPROVED");
            for(int i=0;i<usable.Length;i++)
            {
                var s=usable[i];
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[s.Id],master.transform);
                instance.name=s.Id+"__SOURCE_QA_ONLY";
                instance.transform.localPosition=new Vector3((i%6)*4f,0,(i/6)*4f);
                instance.transform.localRotation=Quaternion.identity;
                instance.transform.localScale=Vector3.one;
            }
            var sunlight=new GameObject("QA_Light").AddComponent<Light>();
            sunlight.type=LightType.Directional;
            sunlight.transform.rotation=Quaternion.Euler(40,-30,0);
            var camera=new GameObject("QA_Camera").AddComponent<Camera>();
            camera.transform.position=new Vector3(15,23,-22);
            camera.transform.LookAt(new Vector3(10,0,10));
            var scene=SceneRoot+"/"+SceneName+".unity";
            if(!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),scene))
                throw new IOException("Could not save quarantine scene");
            AssetDatabase.SaveAssets();
            Debug.Log("[C01-10] Built REAL FBX-linked quarantine prefab instances: "+usable.Length+
                      ". Preview MeshCollider is NON-CONVEX STATIC AND NOT PRODUCTION. "+
                      "Ship clearance, manual play and C01-02 approval NOT RUN.");
        }
        // Unity batchmode: -executeMethod C01.InteriorProps.Editor.Pass04SourceImportAudit.RunBatch
        public static void RunBatch()
        {
            Audit();
            BuildQuarantine(); // fails loudly if no actual validated sources
        }
    }
}
