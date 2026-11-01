// C01-10 PASS18: READ-ONLY real Unity 6 Editor inspection of exact staged Blender FBX binaries.
// No source mesh edits, no ship scene changes, no producer approvals or synthetic proxy objects.
// Batch entry: -executeMethod C01.InteriorProps.Editor.Pass18NativeUnityBatchAudit.RunBatch
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace C01.InteriorProps.Editor
{
    public static class Pass18NativeUnityBatchAudit
    {
        const string Manifest = "C01InteriorProps/Pass04/source_stage_36.json";
        const string OutCsv = "C01InteriorProps_QA/PASS18/UNITY_ACTUAL_FBX_IMPORT_36.csv";
        const string Stage = "Assets/C01InteriorProps/Pass04Incoming/";
        const string Candidate = "CANDIDATE_BINARY_FBX_QA_NOT_APPROVED";
        const float DegenerateAreaSquared = 1e-14f;

        [Serializable]
        sealed class Registry { public Asset[] assets; }
        [Serializable]
        sealed class Asset
        {
            public string id, source_commit, native_export_sync, final_fbx_sha256,
                native_blend_sha256, native_blend_path, independent_qa;
        }

        static readonly Dictionary<string,int> MinimumPartCount = new Dictionary<string,int> {
            {"P15-01",25},{"P15-02",34},{"P15-03",34},
            {"P16-01",12},{"P16-02",12},{"P16-03",12},{"P16-04",27},
            {"P16-05",19},{"P16-06",23},{"P16-07",11},
            {"P17-01",25},{"P17-02",38},{"P17-03",20},
            {"P18-01",47},{"P18-02",59},{"P18-03",63},
            {"P19-01",4},{"P19-02",5},{"P19-05",7}
        };
        static readonly Dictionary<string,int> MinimumTriangles = new Dictionary<string,int> {
            {"P16-01",220},{"P16-02",220},{"P16-03",220},{"P16-04",452},
            {"P16-05",344},{"P16-06",388},{"P16-07",208},
            {"P17-01",380},{"P17-02",536},{"P17-03",424},
            {"P18-01",980},{"P18-02",1284},{"P18-03",1780},
            {"P19-01",470},{"P19-02",292},{"P19-05",252}
        };

        static string ProjectRoot { get { return Path.GetFullPath(Path.Combine(Application.dataPath,"..")); } }
        static string Abs(string relative)
        {
            if (Path.IsPathRooted(relative) || relative.Contains("..") || relative.IndexOf('\\') >= 0)
                throw new InvalidDataException("Unsafe path: "+relative);
            return Path.GetFullPath(Path.Combine(ProjectRoot,relative.Replace('/',Path.DirectorySeparatorChar)));
        }
        static string HexSha(string filename)
        {
            using (var sha=SHA256.Create())
            using (var stream=File.OpenRead(filename))
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
        }
        static bool IsHex64(string value)
        {
            return !string.IsNullOrEmpty(value) && value.Length==64 &&
                value.All(c=>(c>='0'&&c<='9')||(c>='a'&&c<='f'));
        }
        static bool HasFbxMagic(string filename)
        {
            var magic=Encoding.ASCII.GetBytes("Kaydara FBX Binary");
            var buffer=new byte[magic.Length];
            using(var stream=File.OpenRead(filename))
                if(stream.Read(buffer,0,buffer.Length)!=buffer.Length) return false;
            return buffer.SequenceEqual(magic);
        }
        static string Csv(string s)
        {
            s=s??"";
            return s.IndexOfAny(new[]{',','"','\n','\r'})>=0 ?
                "\""+s.Replace("\"","\"\"")+"\"" : s;
        }
        static string AssetPath(string id) { return Stage+id+"/"+id+".fbx"; }
        static string[] GetRequiredMovableNames(string id)
        {
            if(id=="P15-03") return new[]{"Door"};
            if(id=="P16-06") return new[]{"ROTOR"};
            if(id=="P17-03") return new[]{"LeverPivot"};
            if(id=="P18-03") return new[]{"Wheel_LB","Wheel_LF","Wheel_RB","Wheel_RF"};
            return new string[0];
        }
        static string CheckMovableHierarchy(string id,GameObject prefab)
        {
            var required=GetRequiredMovableNames(id);
            if(required.Length==0) return "NOT_APPLICABLE";
            var transforms=prefab.GetComponentsInChildren<Transform>(true);
            var missing=required.Where(token=>!transforms.Any(x=>
                x.name.IndexOf(token,StringComparison.OrdinalIgnoreCase)>=0)).ToArray();
            return missing.Length==0 ? "NAMED_HIERARCHY_PRESENT_MOTION_NOT_TESTED" :
                "MISSING_MOVABLE_NODES:"+string.Join("|",missing);
        }

        [MenuItem("C01/Interior Props/PASS18/Run signed FBX Unity read-only audit")]
        public static void RunBatch()
        {
            var json=File.ReadAllText(Abs(Manifest));
            var registry=JsonUtility.FromJson<Registry>(json);
            if(registry==null || registry.assets==null || registry.assets.Length!=36 ||
               registry.assets.Select(x=>x.id).Distinct().Count()!=36)
                throw new InvalidDataException("Requires exactly 36 unique signed manifest IDs");
            if(EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Play Mode must be stopped");
            // AssetDatabase may import FBX; this tool never creates meshes or overwrites scenes.
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var header="id,source_commit,expected_fbx_sha256,actual_fbx_sha256,unity_version,"+
                "urp_pipeline,meshes,vertices,triangles,degenerates,missing_uv0,missing_normals,"+
                "non_urp_materials,source_colliders,moving_hierarchy,unity_result,release_approval";
            var lines=new List<string>{header};
            int inspected=0,failed=0,notRun=0;
            bool urp=GraphicsSettings.currentRenderPipeline!=null &&
                GraphicsSettings.currentRenderPipeline.GetType().FullName
                  .IndexOf("Universal",StringComparison.OrdinalIgnoreCase)>=0;

            foreach(var e in registry.assets.OrderBy(x=>x.id,StringComparer.Ordinal))
            {
                var path=AssetPath(e.id);
                var filename=Abs(path);
                string status="UNITY_NOT_RUN",real="",moving="NOT_RUN";
                int meshes=0,vertices=0,triangles=0,degenerate=0,uvMissing=0,
                    normalMissing=0,nonUrpMaterials=0,colliders=0;
                try
                {
                    if(e.independent_qa=="APPROVED")
                        throw new InvalidDataException("Integrator manifest must not self-approve QA");
                    if(e.native_export_sync!=Candidate)
                    {
                        status="HOLD_NATIVE_SOURCE_OR_QA";
                    }
                    else if(!IsHex64(e.final_fbx_sha256) || !IsHex64(e.native_blend_sha256))
                    {
                        status="HOLD_MISSING_SIGNED_NATIVE_PAIR";
                    }
                    else if(!File.Exists(filename))
                    {
                        status="UNITY_NOT_RUN_FBX_NOT_STAGED";
                    }
                    else
                    {
                        // Critical: never inspect a stale or mismatched imported FBX.
                        real=HexSha(filename);
                        if(real!=e.final_fbx_sha256 || !HasFbxMagic(filename))
                            throw new InvalidDataException("Hydrated FBX hash/magic mismatch");
                        var importer=AssetImporter.GetAtPath(path) as ModelImporter;
                        if(importer==null) throw new InvalidDataException("Not a Unity ModelImporter");
                        var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path);
                        if(prefab==null) throw new InvalidDataException("Unity did not import a GameObject");
                        var filters=prefab.GetComponentsInChildren<MeshFilter>(true);
                        meshes=filters.Length;
                        moving=CheckMovableHierarchy(e.id,prefab);
                        foreach(var f in filters)
                        {
                            Mesh mesh=f.sharedMesh;
                            if(mesh==null)throw new InvalidDataException("MeshFilter without mesh");
                            if(!mesh.isReadable)
                                throw new InvalidDataException("Mesh must be readable for actual geometry QA");
                            vertices+=mesh.vertexCount;
                            var positions=mesh.vertices;
                            if(mesh.uv==null || mesh.uv.Length!=mesh.vertexCount)uvMissing++;
                            if(mesh.normals==null || mesh.normals.Length!=mesh.vertexCount)normalMissing++;
                            for(int sub=0;sub<mesh.subMeshCount;sub++)
                            {
                                var indices=mesh.GetTriangles(sub);
                                if(indices.Length%3!=0) throw new InvalidDataException("Non-triangle index list");
                                for(int t=0;t<indices.Length;t+=3)
                                {
                                    int ia=indices[t],ib=indices[t+1],ic=indices[t+2];
                                    if(ia<0||ib<0||ic<0||
                                       ia>=positions.Length||ib>=positions.Length||ic>=positions.Length)
                                        throw new InvalidDataException("Out-of-range triangle");
                                    if(Vector3.Cross(positions[ib]-positions[ia],
                                        positions[ic]-positions[ia]).sqrMagnitude<=DegenerateAreaSquared)
                                        degenerate++;
                                    triangles++;
                                }
                            }
                        }
                        var renderers=prefab.GetComponentsInChildren<Renderer>(true);
                        foreach(var rend in renderers)
                            foreach(var mat in rend.sharedMaterials)
                                if(mat==null || mat.shader==null ||
                                   (!mat.shader.name.StartsWith("Universal Render Pipeline/",
                                     StringComparison.OrdinalIgnoreCase) &&
                                    !mat.shader.name.StartsWith("Shader Graphs/",
                                     StringComparison.OrdinalIgnoreCase)))
                                    nonUrpMaterials++;
                        colliders=prefab.GetComponentsInChildren<Collider>(true).Length;
                        if(MinimumPartCount.ContainsKey(e.id) && meshes<MinimumPartCount[e.id])
                            throw new InvalidDataException("Imported MeshFilter count below source budget");
                        if(MinimumTriangles.ContainsKey(e.id) && triangles<MinimumTriangles[e.id])
                            throw new InvalidDataException("Imported triangle count below source budget");
                        if(degenerate>0 || uvMissing>0 || normalMissing>0)
                            throw new InvalidDataException("Geometry/UV/normal failure");
                        // Materials, colliders and moving parts are separate HOLD gates;
                        // a source FBX import alone is NEVER claimed to be a finished prefab.
                        status=(!urp || nonUrpMaterials>0 ||
                                moving.StartsWith("MISSING_MOVABLE",StringComparison.Ordinal))
                            ? "UNITY_IMPORTED_WITH_MATERIAL_OR_PIVOT_HOLD"
                            : "UNITY_IMPORT_DIAGNOSTIC_ONLY_COLLIDER_SWEEP_NOT_RUN";
                        inspected++;
                    }
                }
                catch(Exception ex)
                {
                    status="UNITY_IMPORT_FAIL:"+ex.GetType().Name+":"+ex.Message;
                    failed++;
                }
                if(status.StartsWith("UNITY_NOT_RUN") || status.StartsWith("HOLD_"))notRun++;
                string[] cells={e.id,e.source_commit,e.final_fbx_sha256,real,
                    Application.unityVersion,urp?"URP_ACTIVE":"URP_NOT_ACTIVE",
                    meshes.ToString(),vertices.ToString(),triangles.ToString(),
                    degenerate.ToString(),uvMissing.ToString(),normalMissing.ToString(),
                    nonUrpMaterials.ToString(),colliders.ToString(),moving,status,"NOT_APPROVED"};
                lines.Add(string.Join(",",cells.Select(Csv)));
            }
            var dest=Abs(OutCsv);
            Directory.CreateDirectory(Path.GetDirectoryName(dest));
            File.WriteAllLines(dest,lines,Encoding.UTF8);
            Debug.Log("[C01-10 PASS18] Actual Unity Editor report: "+OutCsv+
                " inspected="+inspected+" failed="+failed+" notRunOrHold="+notRun+
                " / 36. Motion/PhysX clearance, Blender reimport, scene gameplay and C01-02 FINAL QA NOT RUN.");
            if(inspected==0||failed>0)throw new InvalidOperationException(
                "PASS18 incomplete or failed. Inspect "+OutCsv+"; no release approvals granted.");
        }
    }
}
