// C01-02 independent inspection. Does not alter the ship scene or producer prefabs.
// Unity 6 Editor menu: Tools > C01 > Interior Props > Audit Prefabs.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace C01.InteriorProps.QA.Editor
{
    public static class C01InteriorPropsQa
    {
        private const string Root = "Assets/C01InteriorProps";
        private static readonly string[] Ids = {
            "P15-01", "P15-02", "P15-03", "P16-01", "P16-02", "P16-03",
            "P17-01", "P17-02", "P17-03", "P18-01", "P18-02", "P18-03",
            "P19-01", "P19-02", "P19-03", "P19-04"
        };
        [Serializable] private class AssetResult
        {
            public string id, status, prefabPath, meshStatus, normalsStatus, uvStatus;
            public string scaleStatus, materialsStatus, collidersStatus, pivotStatus;
            public string importStatus, playmodeStatus, clearanceStatus;
            public Vector3 boundsMin, boundsMax, boundsSize;
            public int meshCount, triangleCount, materialCount, colliderCount;
            public string[] issues;
        }
        [Serializable] private class AuditReport
        {
            public string generator = "C01-02 Independent Unity 6 Editor QA";
            public string utc = DateTime.UtcNow.ToString("o");
            public string unityVersion = Application.unityVersion;
            public AssetResult[] assets;
            public string warning = "Only inspected actual prefabs; PlayMode, corridor clearance, screenshots and Blender FBX round-trip NOT RUN.";
        }
        [MenuItem("Tools/C01/Interior Props/Audit Prefabs")]
        public static void Run()
        {
            var results = new List<AssetResult>();
            var paths = AssetDatabase.IsValidFolder(Root)
                ? AssetDatabase.FindAssets("t:Prefab", new[] { Root })
                    .Select(AssetDatabase.GUIDToAssetPath).ToArray()
                : new string[0];
            foreach (var id in Ids)
            {
                var exact = paths.Where(p => string.Equals(Path.GetFileNameWithoutExtension(p), id, StringComparison.OrdinalIgnoreCase)).ToArray();
                // Material variants (e.g. P16-03_Amber) are not duplicate primary prefabs.
                var matches = exact.Length > 0 ? exact : paths.Where(p => TokenMatch(Path.GetFileNameWithoutExtension(p), id)).ToArray();
                var r = new AssetResult {
                    id=id, status="BLOCKED", prefabPath="", meshStatus="NOT RUN",
                    normalsStatus="NOT RUN", uvStatus="NOT RUN", scaleStatus="NOT RUN",
                    materialsStatus="NOT RUN", collidersStatus="NOT RUN", pivotStatus="NOT RUN",
                    importStatus="NOT RUN", playmodeStatus="NOT RUN", clearanceStatus="NOT RUN",
                    issues=new[] {"MISSING: uniquely named real prefab"}
                };
                if (matches.Length != 1)
                {
                    if (matches.Length>1) {r.status="FAIL";r.issues=new[] {"DUPLICATE: multiple matching prefabs"};}
                    results.Add(r);continue;
                }
                r.prefabPath=matches[0];
                GameObject obj=null;
                try
                {
                    obj=PrefabUtility.LoadPrefabContents(matches[0]);
                    var issues=new List<string>();
                    var filters=obj.GetComponentsInChildren<MeshFilter>(true);
                    var renderers=obj.GetComponentsInChildren<MeshRenderer>(true);
                    var colliders=obj.GetComponentsInChildren<Collider>(true);
                    r.meshCount=filters.Length;r.colliderCount=colliders.Length;
                    r.scaleStatus=CheckScale(obj.transform) &&
                        obj.GetComponentsInChildren<Transform>(true).All(CheckScale) ? "PASS" : "FAIL";
                    if(r.scaleStatus=="FAIL")issues.Add("Root/child localScale != (1,1,1)");
                    r.collidersStatus=colliders.Length>0?"PASS":"FAIL";
                    if(r.collidersStatus=="FAIL")issues.Add("No colliders");
                    bool normalsOk=true,uvOk=true,hasMesh=false;
                    bool bounded=false;
                    Vector3 min=Vector3.positiveInfinity, max=Vector3.negativeInfinity;
                    var worldToRoot=obj.transform.worldToLocalMatrix;
                    foreach(var f in filters)
                    {
                        var mesh=f.sharedMesh;
                        if(mesh==null){issues.Add("MeshFilter with null mesh");normalsOk=false;uvOk=false;continue;}
                        hasMesh=true;r.triangleCount+=mesh.triangles.Length/3;
                        if(mesh.normals==null || mesh.normals.Length!=mesh.vertexCount)normalsOk=false;
                        if(mesh.uv==null || mesh.uv.Length!=mesh.vertexCount)uvOk=false;
                        var b=mesh.bounds;var xfm=worldToRoot*f.transform.localToWorldMatrix;
                        for(int i=0;i<8;i++)
                        {
                            var corner=new Vector3((i&1)!=0?b.max.x:b.min.x,
                                (i&2)!=0?b.max.y:b.min.y,(i&4)!=0?b.max.z:b.min.z);
                            var p=xfm.MultiplyPoint3x4(corner);
                            min=Vector3.Min(min,p);max=Vector3.Max(max,p);bounded=true;
                        }
                    }
                    r.meshStatus=hasMesh && bounded && r.triangleCount>0?"PASS":"FAIL";
                    r.normalsStatus=hasMesh?(normalsOk?"PASS":"FAIL"):"NOT RUN";
                    r.uvStatus=hasMesh?(uvOk?"PASS":"FAIL"):"NOT RUN";
                    if(r.meshStatus=="FAIL")issues.Add("No readable, valid mesh found");
                    if(r.normalsStatus=="FAIL")issues.Add("Normals missing or wrong count");
                    if(r.uvStatus=="FAIL")issues.Add("UV0 missing or wrong count");
                    if(bounded){r.boundsMin=min;r.boundsMax=max;r.boundsSize=max-min;}
                    var mats=renderers.SelectMany(x=>x.sharedMaterials).Where(x=>x!=null).Distinct().ToArray();
                    r.materialCount=mats.Length;
                    var badMaterial=renderers.Any(x=>x.sharedMaterials.Any(m=>m==null)) ||
                        mats.Any(x=>x.shader==null || !x.shader.name.Contains("Universal Render Pipeline"));
                    r.materialsStatus=mats.Length>=1 && mats.Length<=4 && !badMaterial?"PASS":"FAIL";
                    if(r.materialsStatus=="FAIL")issues.Add("Missing/invalid URP materials or >4 materials");
                    // Only the signed mounting contract and actual scene can certify the pivot.
                    r.pivotStatus="NOT RUN";
                    r.importStatus=r.meshStatus=="PASS"?"PASS":"FAIL";
                    r.status=issues.Count>0?"FAIL":"BLOCKED";
                    r.issues=issues.Count>0?issues.ToArray():new[]{"Pivot mounting, corridor clearance and PlayMode not inspected here"};
                }
                catch(Exception e)
                {
                    r.status="FAIL";r.issues=new[]{"Prefab load/geometry error: "+e.Message};
                }
                finally {if(obj!=null)PrefabUtility.UnloadPrefabContents(obj);}
                results.Add(r);
            }
            var report=new AuditReport {assets=results.ToArray()};
            var outDir=Path.Combine(Directory.GetParent(Application.dataPath).FullName,"C01InteriorProps_QA");
            Directory.CreateDirectory(outDir);
            var path=Path.Combine(outDir,"unity_editor_audit.json");
            File.WriteAllText(path,JsonUtility.ToJson(report,true));
            AssetDatabase.Refresh();
            Debug.Log("C01-02 QA: "+results.Count+" expected prefabs; report: "+path+
                "; full PASS withheld pending Blender, clearance and PlayMode evidence.");
        }
        private static bool CheckScale(Transform t)
        {
            return Vector3.Distance(t.localScale,Vector3.one)<0.0001f;
        }
        private static bool TokenMatch(string name,string id)
        {
            var index=name.IndexOf(id,StringComparison.OrdinalIgnoreCase);
            if(index<0)return false;
            int after=index+id.Length;
            return (index==0 || !char.IsLetterOrDigit(name[index-1])) &&
                   (after==name.Length || !char.IsLetterOrDigit(name[after]));
        }
    }
}
