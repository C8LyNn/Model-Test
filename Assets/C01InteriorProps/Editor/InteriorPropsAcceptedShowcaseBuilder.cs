// C01-10 — Accepted-only Interior Props integration (Unity 6 URP).
// C01-02 owns QA status. This tool does not mutate source meshes or ship geometry.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace C01.InteriorProps.Editor
{
    public static class InteriorPropsAcceptedShowcaseBuilder
    {
        const string Root = "Assets/C01InteriorProps";
        const string Ledger = Root + "/QA/approved_assets.csv";
        const string OutputRoot = Root + "/AcceptedShowcase";
        const string PrefabDir = OutputRoot + "/Prefabs";
        const string SceneDir = OutputRoot + "/Scenes";
        const string Evidence = "C01InteriorProps_QA/integration";
        const string MasterName = "C01_InteriorProps_Showcase_MASTER";
        const float DimensionTolerance = .002f; // C01-01, ±2 mm
        const float PivotTolerance = .001f;     // C01-01, ±1 mm
        const float ScaleTolerance = .0001f;    // C01-01
        const float MinCorridorWidth = 3.0f;    // test reference strip only, NOT ship clearance

        struct Slot
        {
            public string Id, Family, Mount;
            public float W,D,H;
            public Slot(string id,string family,string mount,float w,float d,float h)
            { Id=id;Family=family;Mount=mount;W=w;D=d;H=h; }
        }
        // Exact canonical Wave 01 dimensions from C01-01 standard v0.2.1.
        static readonly Slot[] Wave01 = {
            new Slot("P15-01","Installations","rail",1f,.14f,.14f),
            new Slot("P15-02","Installations","wall",.6f,.08f,.4f),
            new Slot("P15-03","Installations","floor",.8f,.35f,1.8f),
            new Slot("P16-01","Lighting","ceiling",1.2f,.15f,.12f),
            new Slot("P16-02","Lighting","wall",.35f,.14f,.22f),
            new Slot("P16-03","Lighting","wall",.2f,.2f,.3f),
            new Slot("P17-01","Controls","floor",1.6f,.65f,1.1f),
            new Slot("P17-02","Controls","wall",.18f,.07f,.28f),
            new Slot("P17-03","Controls","floor",.4f,.3f,.55f),
            new Slot("P18-01","Cargo","floor",.9f,.9f,.9f),
            new Slot("P18-02","Cargo","floor",2.1f,.8f,2.1f),
            new Slot("P18-03","Cargo","floor",1f,.7f,1.2f),
            new Slot("P19-01","Furniture","floor",.95f,2.1f,.65f),
            new Slot("P19-02","Furniture","floor",.65f,.55f,1.8f),
            new Slot("P19-03","Furniture","floor",1.4f,.65f,.75f),
            new Slot("P19-04","Furniture","floor",.6f,.6f,.95f),
        };
        // Wave 02 ownership only; dimensions MUST be supplied by signed QA ledger.
        static readonly string[] Wave02 = {
            "P15-04","P15-05","P15-06","P15-07",
            "P16-04","P16-05","P16-06","P16-07",
            "P17-04","P17-05","P17-06","P17-07",
            "P18-04","P18-05","P18-06","P18-07",
            "P19-05","P19-06","P19-07","P19-08"
        };
        static readonly HashSet<string> AllIds = new HashSet<string>(
            Wave01.Select(s=>s.Id).Concat(Wave02),StringComparer.Ordinal);
        const string Header = "asset_id,approval,owner,family,mount,width_m,depth_m,height_m,prefab_path,fbx_path,fbx_sha256,qa_reference";

        sealed class Record
        {
            public Slot Slot;
            public string Approval,Owner,PrefabPath,FbxPath,Hash,QaRef;
            public GameObject Prefab;
            public Bounds Measured;
            public string Error;
        }

        static string Absolute(string projectPath)
        {
            if (string.IsNullOrEmpty(projectPath) ||
                !projectPath.Replace('\\','/').StartsWith("Assets/",StringComparison.Ordinal))
                throw new InvalidDataException("Must be project-relative Assets path: "+projectPath);
            if (projectPath.Contains("..") || Path.IsPathRooted(projectPath))
                throw new InvalidDataException("Unsafe path: "+projectPath);
            return Path.GetFullPath(Path.Combine(Path.GetDirectoryName(Application.dataPath),
                projectPath.Replace('/',Path.DirectorySeparatorChar)));
        }
        static string Sha256(string path)
        {
            using (var sha=SHA256.Create())
            using (var fs=File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(fs)).Replace("-","").ToLowerInvariant();
        }
        static float F(string v)
        {
            return float.Parse(v,CultureInfo.InvariantCulture);
        }
        static bool Near(float a,float b,float eps) { return Mathf.Abs(a-b)<=eps; }
        static bool UnitScale(Vector3 s) {
            return Near(s.x,1,ScaleTolerance)&&Near(s.y,1,ScaleTolerance)&&Near(s.z,1,ScaleTolerance);
        }
        static bool IdentityRotation(Quaternion q) {
            return Quaternion.Angle(q,Quaternion.identity)<.01f;
        }
        static List<Record> LoadLedger()
        {
            if (!File.Exists(Absolute(Ledger)))
                throw new FileNotFoundException("QA-approved ledger missing; no integration allowed",Ledger);
            string[] lines=File.ReadAllLines(Absolute(Ledger));
            if(lines.Length==0||lines[0].Trim()!=Header)
                throw new InvalidDataException("QA ledger schema mismatch: "+Ledger);
            var records=new List<Record>(); var used=new HashSet<string>();
            for(int i=1;i<lines.Length;i++)
            {
                if(string.IsNullOrWhiteSpace(lines[i]))continue;
                var row=lines[i].Split(',');
                if(row.Length!=12)throw new InvalidDataException("QA ledger line "+(i+1)+" must have 12 fields");
                string id=row[0].Trim();
                if(!AllIds.Contains(id))throw new InvalidDataException("Unknown prop ID: "+id);
                if(!used.Add(id))throw new InvalidDataException("Duplicate QA approval: "+id);
                // Explicit approval only; other rows cannot be added to generated scenes.
                if(row[1].Trim()!="APPROVED")continue;
                var slot=new Slot(id,row[3].Trim(),row[4].Trim(),F(row[5]),F(row[6]),F(row[7]));
                if(slot.W<=0||slot.D<=0||slot.H<=0)throw new InvalidDataException("Invalid dimensions "+id);
                if(!new[]{"floor","wall","ceiling","rail"}.Contains(slot.Mount))
                    throw new InvalidDataException("Invalid mount "+id);
                if(!new[]{"Installations","Lighting","Controls","Cargo","Furniture"}.Contains(slot.Family))
                    throw new InvalidDataException("Invalid family "+id);
                string owner="C01-"+id.Substring(1,2);
                if(row[2].Trim()!=owner)throw new InvalidDataException("Wrong owner "+id);
                if(Wave01.Any(x=>x.Id==id)) {
                    var expected=Wave01.First(x=>x.Id==id);
                    if(slot.Mount!=expected.Mount||slot.Family!=expected.Family||
                       !Near(slot.W,expected.W,DimensionTolerance)||
                       !Near(slot.D,expected.D,DimensionTolerance)||
                       !Near(slot.H,expected.H,DimensionTolerance))
                        throw new InvalidDataException("Wave01 slot deviates from C01-01: "+id);
                }
                var r=new Record {
                    Slot=slot,Approval=row[1].Trim(),Owner=owner,
                    PrefabPath=row[8].Trim(),FbxPath=row[9].Trim(),
                    Hash=row[10].Trim().ToLowerInvariant(),QaRef=row[11].Trim()
                };
                if(r.QaRef.Length<12 || !r.QaRef.StartsWith("https://github.com/C8LyNn/Model-Test/",StringComparison.Ordinal))
                    throw new InvalidDataException("QA evidence URL missing for "+id);
                if(r.Hash.Length!=64||r.Hash.Any(c=>!"0123456789abcdef".Contains(c)))
                    throw new InvalidDataException("Invalid SHA-256 field for "+id);
                records.Add(r);
            }
            return records;
        }
        static Bounds ImportedBounds(GameObject root)
        {
            var filters=root.GetComponentsInChildren<MeshFilter>(true);
            bool found=false;Bounds b=new Bounds();
            foreach(var filter in filters)
            {
                if(filter.sharedMesh==null)continue;
                Mesh mesh=filter.sharedMesh;
                if(mesh.vertexCount==0)continue;
                foreach(var v in mesh.vertices)
                {
                    var p=root.transform.InverseTransformPoint(filter.transform.TransformPoint(v));
                    if(!found){b=new Bounds(p,Vector3.zero);found=true;}else b.Encapsulate(p);
                }
            }
            if(!found)throw new InvalidDataException("Prefab lacks real MeshFilter geometry");
            return b;
        }
        static string Validate(Record r)
        {
            var errs=new List<string>();string fullFbx=null;
            try {fullFbx=Absolute(r.FbxPath);} catch(Exception e){errs.Add(e.Message);}
            if(fullFbx!=null) {
                if(!File.Exists(fullFbx))errs.Add("FBX missing");
                else {
                    if(new FileInfo(fullFbx).Length<200)errs.Add("FBX file suspiciously small / LFS pointer");
                    else if(Sha256(fullFbx)!=r.Hash)errs.Add("FBX SHA-256 differs from QA-approved SHA");
                }
            }
            if(!r.PrefabPath.StartsWith("Assets/C01InteriorProps/",StringComparison.Ordinal))
                errs.Add("Prefab outside props folder");
            else {
                r.Prefab=AssetDatabase.LoadAssetAtPath<GameObject>(r.PrefabPath);
                if(r.Prefab==null)errs.Add("Unity prefab missing or failed import");
                else {
                    GameObject go=null;
                    try {
                        go=(GameObject)PrefabUtility.InstantiatePrefab(r.Prefab);
                        if(!UnitScale(go.transform.localScale))errs.Add("root scale !=1");
                        if(!IdentityRotation(go.transform.localRotation))errs.Add("root rotation not identity");
                        if(go.GetComponentsInChildren<Collider>(true).Length==0)errs.Add("no colliders");
                        r.Measured=ImportedBounds(go);
                        var b=r.Measured;var s=r.Slot;
                        if(!Near(b.size.x,s.W,DimensionTolerance)||!Near(b.size.z,s.D,DimensionTolerance)||
                           !Near(b.size.y,s.H,DimensionTolerance))
                           errs.Add("bounds mismatch (2mm tolerance)");
                        if(s.Mount=="floor") {
                            if(!Near(b.min.y,0,PivotTolerance)||
                               !Near(b.center.x,0,PivotTolerance)||
                               !Near(b.center.z,0,PivotTolerance))errs.Add("floor origin/pivot mismatch");
                        } else if(s.Mount=="wall") {
                            if(!Near(b.center.x,0,PivotTolerance)||
                               !Near(b.center.y,0,PivotTolerance)||
                               !Near(b.max.z,0,PivotTolerance))errs.Add("wall mounting pivot mismatch");
                        } else if(s.Mount=="ceiling") {
                            if(!Near(b.max.y,0,PivotTolerance)||
                               !Near(b.center.x,0,PivotTolerance)||
                               !Near(b.center.z,0,PivotTolerance))errs.Add("ceiling mounting pivot mismatch");
                        } else if(s.Mount=="rail") {
                            if(!Near(b.min.x,0,PivotTolerance)||
                               !Near(b.center.y,0,PivotTolerance)||
                               !Near(b.center.z,0,PivotTolerance))errs.Add("rail start pivot mismatch");
                        }
                        if(go.GetComponentsInChildren<MeshRenderer>(true).Length==0)
                            errs.Add("no MeshRenderer");
                    } catch(Exception e) {errs.Add(e.Message);}
                    finally {if(go!=null)UnityEngine.Object.DestroyImmediate(go);}
                }
            }
            return string.Join("; ",errs.ToArray());
        }
        static void WriteReport(List<Record> records)
        {
            string abs=Path.GetFullPath(Path.Combine(Path.GetDirectoryName(Application.dataPath),Evidence));
            Directory.CreateDirectory(abs);
            var lines=new List<string> {"asset_id,status,prefab,fbx,qa_ref,issues"};
            foreach(var r in records)
            {
                string e=(r.Error??"").Replace("\"","\"\"");
                lines.Add(r.Slot.Id+","+(e.Length==0?"SOURCE_PRECHECK_PASS":"BLOCKED")+","+
                    r.PrefabPath+","+r.FbxPath+","+r.QaRef+",\""+e+"\"");
            }
            File.WriteAllLines(Path.Combine(abs,"ACCEPTED_PREFLIGHT.csv"),lines);
        }
        [MenuItem("C01/Interior Props/Wave 02/Preflight Approved SHA")]
        public static void Preflight()
        {
            var list=LoadLedger();
            foreach(var r in list)r.Error=Validate(r);
            WriteReport(list);
            Debug.Log("[C01-10] "+list.Count(x=>x.Error=="")+"/"+list.Count+
                " records pass local source checks; no independent ship clearance claimed.");
        }
        static void Folder(string p) {
            Directory.CreateDirectory(Absolute(p+"/.").TrimEnd(Path.DirectorySeparatorChar,'.'));
        }
        static Transform Group(GameObject root,string label)
        {
            var t=root.transform.Find(label);
            if(t!=null)return t;
            var child=new GameObject(label);
            child.transform.SetParent(root.transform,false);
            return child.transform;
        }
        static Vector3 ShowcasePosition(Record r,int index)
        {
            // Diagnostic gallery, outside x [-1.5,1.5] 3m reference lane.
            float x=(index%2==0?-7f:7f);
            float z=(index/2)*4.0f;
            float y=r.Slot.Mount=="ceiling"?5f:
                    (r.Slot.Mount=="wall"||r.Slot.Mount=="rail"?2.3f:0f);
            return new Vector3(x,y,z);
        }
        static GameObject AddInstance(GameObject root,Record r,Vector3 at)
        {
            var parent=Group(root,r.Slot.Family);
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(r.Prefab,parent);
            instance.name=r.Slot.Id;
            instance.transform.localPosition=at;
            instance.transform.localRotation=Quaternion.identity;
            instance.transform.localScale=Vector3.one;
            return instance;
        }
        static void StandaloneScene(string name,IEnumerable<Record> records)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var root=new GameObject(name);
            int i=0;
            foreach(var r in records)AddInstance(root,r,ShowcasePosition(r,i++));
            var light=new GameObject("InspectionLight").AddComponent<Light>();
            light.type=LightType.Directional;light.intensity=1;
            light.transform.rotation=Quaternion.Euler(50,-20,0);
            var scenePath=SceneDir+"/"+name+".unity";
            if(!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),scenePath))
                throw new IOException("Unity failed to save "+scenePath);
        }
        [MenuItem("C01/Interior Props/Wave 02/Build Approved Showcase")]
        public static void Build()
        {
            if(EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Stop Play Mode");
            if(Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty))
                throw new InvalidOperationException("Save existing scenes first");
            var records=LoadLedger();
            if(records.Count==0)throw new InvalidOperationException(
                "C01-02 has approved 0 assets: no placeholder scenes will be built.");
            foreach(var r in records)r.Error=Validate(r);
            WriteReport(records);
            var errors=records.Where(r=>r.Error!="").Select(r=>r.Slot.Id+": "+r.Error).ToArray();
            if(errors.Length>0)throw new InvalidOperationException(
                "QA-approved asset SHA/import/pivot gate failed:\n"+string.Join("\n",errors));
            Folder(PrefabDir);Folder(SceneDir);
            AssetDatabase.Refresh();
            var root=new GameObject(MasterName);
            GameObject master;
            try {
                for(int i=0;i<records.Count;i++)AddInstance(root,records[i],ShowcasePosition(records[i],i));
                master=PrefabUtility.SaveAsPrefabAsset(root,PrefabDir+"/"+MasterName+".prefab");
                if(master==null)throw new IOException("Master prefab save failed");
            } finally {UnityEngine.Object.DestroyImmediate(root);}
            StandaloneScene("C01_InteriorProps_Showcase",records);
            StandaloneScene("C01_InteriorProps_Cabin",records.Where(r=>r.Slot.Family=="Furniture"));
            StandaloneScene("C01_InteriorProps_Bridge",records.Where(r=>r.Slot.Family=="Controls"));
            StandaloneScene("C01_InteriorProps_Engineering",records.Where(r=>
                r.Slot.Family=="Installations"||r.Slot.Family=="Lighting"));
            StandaloneScene("C01_InteriorProps_Cargo",records.Where(r=>r.Slot.Family=="Cargo"));
            AssetDatabase.SaveAssets();
            Debug.Log("[C01-10] Generated "+records.Count+" approved prefab instances in separate master and five scenes. "+
                "Real ship 3m corridor, gate swing, stairs and elevators: NOT RUN until QA evidence.");
        }
    }
}
