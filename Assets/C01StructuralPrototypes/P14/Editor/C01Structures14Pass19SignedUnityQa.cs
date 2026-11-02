#if UNITY_EDITOR
// C01-14 W19 — QA-ONLY signed original native Blender FBX -> Unity 6 URP prefab validation.
// Not a release approval. Does not touch ship geometry, production prefabs or 36 P15-P19 assets.
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class C01Structures14Pass19SignedUnityQa
{
    const string Root = "Assets/C01StructuralPrototypes/P14";
    const string QaRoot = Root + "/Pass19/UnityQA";
    const string Incoming = QaRoot + "/Incoming";
    const string Prefabs = QaRoot + "/Prefabs";
    const string Materials = QaRoot + "/Materials";

    sealed class SignedInput
    {
        public readonly string Id, FbxPath, BlendPath, FbxSha, BlendSha;
        public readonly int Meshes, Triangles;
        public SignedInput(string id, string fbx, string blend, string fbxSha, string blendSha, int meshes, int triangles)
        {
            Id=id; FbxPath=fbx; BlendPath=blend; FbxSha=fbxSha; BlendSha=blendSha;
            Meshes=meshes; Triangles=triangles;
        }
        public string Staged => Incoming + "/" + Id + "_EXACT_SIGNED_QA_ONLY.fbx";
        public string Prefab => Prefabs + "/" + Id + "_QA_ONLY.prefab";
    }

    static readonly SignedInput[] Inputs = {
        new SignedInput(
            "RAI-01",
            Root+"/Pass17/Native/C01_14_RAI-01_DETAIL17.fbx",
            Root+"/Pass17/Native/C01_14_RAI-01_DETAIL17.blend",
            "f0c8fd590d7752431c869be2f9807209b7632d87a77ab619049c90f60f0ff1fe",
            "715bd015029b6f4cfc4126b4b6e0e944cd03c2719f70ceb719d5912baa3e0e42",
            20,424),
        new SignedInput(
            "RMP-01",
            Root+"/Pass03/FBX/C01_14_RMP-01_v002.fbx",
            Root+"/Pass03/Sources/C01_14_RMP-01_v002.blend",
            "97f0b125313057f4ecf601dd60a02b4d3f0d55b87c1713d71a0adbedcc6d1443",
            "7cba127139253a34b0575b0c55f10112395acb790b9716e1a248a3bcc8812cfa",
            6,72)
    };

    static string ProjectRoot => Path.GetFullPath(Path.Combine(Application.dataPath,".."));

    static string Absolute(string relative)
    {
        if (string.IsNullOrWhiteSpace(relative) || Path.IsPathRooted(relative) ||
            relative.Contains("..") || relative.Contains("\\") || !relative.StartsWith(Root+"/",StringComparison.Ordinal))
            throw new InvalidDataException("Unsafe C01-14 path: "+relative);
        var path=Path.GetFullPath(Path.Combine(ProjectRoot,relative));
        if (!path.StartsWith(Path.GetFullPath(Path.Combine(ProjectRoot,Root))+Path.DirectorySeparatorChar,StringComparison.Ordinal))
            throw new InvalidDataException("Path escaped C01-14 scope: "+relative);
        return path;
    }
    static string Sha(string filename)
    {
        using (var sha=SHA256.Create())
        using (var stream=File.OpenRead(filename))
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
    }
    static void AssertSigned(string assetPath,string expected,string magic)
    {
        var disk=Absolute(assetPath);
        if(!File.Exists(disk))throw new FileNotFoundException("Genuine LFS binary missing: "+assetPath,disk);
        using(var stream=File.OpenRead(disk))
        {
            var bytes=Encoding.ASCII.GetBytes(magic);
            var head=new byte[bytes.Length];
            if(stream.Read(head,0,head.Length)!=head.Length || !head.SequenceEqual(bytes))
                throw new InvalidDataException("Not hydrated native file; Git LFS pointer or stale proxy: "+assetPath);
        }
        if(Sha(disk)!=expected)throw new InvalidDataException("Native SHA mismatch, HOLD: "+assetPath);
    }

    static Material QaMaterial(string name,Color color,Shader shader)
    {
        string path=Materials+"/"+name+"_QA_ONLY.mat";
        var m=AssetDatabase.LoadAssetAtPath<Material>(path);
        if(m!=null)
        {
            if(m.shader!=shader)throw new InvalidDataException("Unexpected prior QA material: "+path);
            return m;
        }
        m=new Material(shader){name=name+"_QA_ONLY"};
        m.SetColor("_BaseColor",color);
        m.SetFloat("_Smoothness",.25f);
        AssetDatabase.CreateAsset(m,path);
        return m;
    }

    static void PrefabFromSigned(SignedInput candidate,Material steel,Material dark,Material caution)
    {
        if(AssetDatabase.LoadAssetAtPath<GameObject>(candidate.Prefab)!=null)
            throw new InvalidOperationException("Refusing to overwrite existing QA prefab; inspect before rerun: "+candidate.Prefab);
        var importer=AssetImporter.GetAtPath(candidate.Staged) as ModelImporter;
        if(importer==null)throw new InvalidOperationException("Unity failed to allocate ModelImporter for "+candidate.Id);
        importer.isReadable=true;
        importer.importNormals=ModelImporterNormals.Import;
        importer.meshCompression=ModelImporterMeshCompression.Off;
        importer.preserveHierarchy=true;
        importer.SaveAndReimport();
        var original=AssetDatabase.LoadAssetAtPath<GameObject>(candidate.Staged);
        if(original==null)throw new InvalidDataException("Native FBX import gave no GameObject: "+candidate.Id);

        var root=new GameObject("C01_14_"+candidate.Id+"_QA_ONLY");
        try
        {
            var instance=PrefabUtility.InstantiatePrefab(original) as GameObject;
            if(instance==null)throw new InvalidDataException("Cannot instantiate exact signed FBX "+candidate.Id);
            // Preserve all imported child pivots, rotations and FBX axis conversion as-is.
            instance.transform.SetParent(root.transform,false);
            var filters=instance.GetComponentsInChildren<MeshFilter>(true);
            if(filters.Length!=candidate.Meshes)
                throw new InvalidDataException(candidate.Id+": expected "+candidate.Meshes+" actual imported mesh parts "+filters.Length);
            int triangleCount=0,collisionCount=0,visibleParts=0;
            foreach(var filter in filters)
            {
                var mesh=filter.sharedMesh;
                if(mesh==null || !mesh.isReadable)throw new InvalidDataException("Unreadable imported mesh: "+filter.name);
                if(mesh.vertexCount==0 || mesh.uv.Length!=mesh.vertexCount || mesh.normals.Length!=mesh.vertexCount)
                    throw new InvalidDataException("Missing geometry, UV0 or normal stream: "+filter.name);
                var tris=mesh.triangles;
                if(tris.Length%3!=0)throw new InvalidDataException("Invalid triangle index count");
                triangleCount+=tris.Length/3;
                foreach(var i in tris)if(i<0 || i>=mesh.vertexCount)
                    throw new InvalidDataException("Invalid index "+i+" on "+filter.name);
                var rend=filter.GetComponent<MeshRenderer>();
                bool isCollision=filter.name.StartsWith("COL_",StringComparison.OrdinalIgnoreCase);
                if(isCollision && candidate.Id=="RMP-01")
                {
                    if(rend!=null)rend.enabled=false;
                    var collider=filter.gameObject.AddComponent<MeshCollider>();
                    collider.sharedMesh=mesh;
                    collider.convex=false;
                    collisionCount++;
                }
                else
                {
                    if(rend==null)throw new InvalidDataException("Missing renderer: "+filter.name);
                    rend.sharedMaterial=filter.name.Contains("AntiSlip")?caution:
                        filter.name.Contains("MiddleRail")?dark:steel;
                    visibleParts++;
                    if(candidate.Id=="RAI-01" && (
                        filter.name=="TopRail" || filter.name=="MiddleRail" ||
                        filter.name=="Post_Start" || filter.name=="Post_End"))
                    {
                        // Only main physical members get colliders. No accidental
                        // hundreds of bolt/washer colliders or rigidbody welds.
                        var col=filter.gameObject.AddComponent<BoxCollider>();
                        col.center=mesh.bounds.center;
                        col.size=mesh.bounds.size;
                        collisionCount++;
                    }
                }
            }
            if(triangleCount!=candidate.Triangles)
                throw new InvalidDataException(candidate.Id+": source triangle mismatch "+triangleCount+" vs "+candidate.Triangles);
            if(candidate.Id=="RAI-01" && (collisionCount!=4 || visibleParts!=20))
                throw new InvalidDataException("RAI 4 structural collider/20 mesh invariant violated");
            if(candidate.Id=="RMP-01" && (collisionCount!=1 || visibleParts!=5))
                throw new InvalidDataException("RMP original dedicated collider/visible mesh invariant violated");

            if(candidate.Id=="RAI-01")
            {
                var bounds=new Bounds();
                bool has=false;
                foreach(var renderer in instance.GetComponentsInChildren<MeshRenderer>(true))
                {
                    if(!renderer.enabled)continue;
                    if(!has){bounds=renderer.bounds;has=true;}else bounds.Encapsulate(renderer.bounds);
                }
                if(!has)throw new InvalidDataException("No visible rail bounds");
                // This tests ACTUAL Unity Y-up import and source dimensions.
                var s=bounds.size;
                if(Mathf.Abs(s.x-2.0f)>.02f || Mathf.Abs(s.y-1.1f)>.02f || Mathf.Abs(s.z-.14f)>.02f)
                    throw new InvalidDataException("FBX axis/scale/bounds mismatch: "+s+"; expected (2,1.1,.14) m");
            }

            root.isStatic=true;
            PrefabUtility.SaveAsPrefabAsset(root,candidate.Prefab);
            if(AssetDatabase.LoadAssetAtPath<GameObject>(candidate.Prefab)==null)
                throw new IOException("Unity did not persist QA prefab");
            Debug.Log("[C01-14 W19] QA_ONLY Unity prefab staged from verified FBX: "+candidate.Id+
                " SHA "+candidate.FbxSha+" meshes "+filters.Length+" triangles "+triangleCount+
                " colliders "+collisionCount+" Unity "+Application.unityVersion+
                ". NOT C01-02 approved, NOT production release.");
        }
        finally {UnityEngine.Object.DestroyImmediate(root);}
    }

    [MenuItem("Tools/C01/Structures 14/QA Only/Build signed PASS19 native prefabs")]
    public static void RunSignedQaOnly()
    {
        if(!Application.unityVersion.StartsWith("6000.",StringComparison.Ordinal))
            throw new NotSupportedException("This gate requires actual Unity 6 Editor (6000.x)");
        if(EditorApplication.isPlayingOrWillChangePlaymode)
            throw new InvalidOperationException("Exit play mode first");
        var renderPipeline=GraphicsSettings.currentRenderPipeline;
        if(renderPipeline==null || renderPipeline.GetType().FullName.IndexOf("Universal",StringComparison.OrdinalIgnoreCase)<0)
            throw new InvalidOperationException("Actual Unity6 URP render pipeline not active");

        // Fail closed BEFORE any writes if one of the two producer binaries is stale.
        foreach(var x in Inputs)
        {
            AssertSigned(x.FbxPath,x.FbxSha,"Kaydara FBX Binary");
            AssertSigned(x.BlendPath,x.BlendSha,"BLENDER");
            if(File.Exists(Absolute(x.Staged)) && Sha(Absolute(x.Staged))!=x.FbxSha)
                throw new InvalidDataException("Refusing to overwrite nonmatching staged FBX "+x.Staged);
            if(File.Exists(Absolute(x.Prefab)))
                throw new InvalidOperationException("QA prefab already exists; no silent overwrite "+x.Prefab);
        }

        Directory.CreateDirectory(Absolute(Incoming));
        Directory.CreateDirectory(Absolute(Prefabs));
        Directory.CreateDirectory(Absolute(Materials));
        foreach(var x in Inputs)
        {
            if(!File.Exists(Absolute(x.Staged)))
                File.Copy(Absolute(x.FbxPath),Absolute(x.Staged),false);
            AssertSigned(x.Staged,x.FbxSha,"Kaydara FBX Binary");
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

        var shader=Shader.Find("Universal Render Pipeline/Lit");
        if(shader==null)throw new InvalidOperationException("URP Lit shader unavailable");
        var steel=QaMaterial("Steel",new Color(.47f,.52f,.59f),shader);
        var dark=QaMaterial("Dark",new Color(.12f,.16f,.20f),shader);
        var caution=QaMaterial("Caution",new Color(.86f,.61f,.12f),shader);
        foreach(var x in Inputs)PrefabFromSigned(x,steel,dark,caution);
        AssetDatabase.SaveAssets();
        Debug.Log("[C01-14 W19] Both signed OPTIONAL structure QA prefabs built. " +
            "Real Unity Editor execution is REQUIRED to claim success; external C01-02 and release still PENDING.");
    }
}
#endif
