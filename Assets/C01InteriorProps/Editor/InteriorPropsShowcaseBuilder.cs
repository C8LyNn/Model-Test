// C01-10 / Interior Props showcase builder, Unity 6 URP.
// Fail-closed: no placeholder meshes and no writes to the ship source scene.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace C01.InteriorProps.Editor
{
    public static class InteriorPropsShowcaseBuilder
    {
        const string Root = "Assets/C01InteriorProps";
        const string Generated = Root + "/Generated";
        const string Prefabs = Generated + "/Prefabs";
        const string Scenes = Generated + "/Scenes";
        const string Master = "C01_InteriorProps_Showcase_MASTER";
        const string MasterPath = Prefabs + "/" + Master + ".prefab";
        const float MaxDeviation = 0.20f; // metres; stricter thresholds belong to C01-01/C01-02
        const float MinMeshExtent = 0.001f;

        sealed class Spec
        {
            public readonly string Id, Family, Mount;
            public readonly Vector3 Expected, Position;
            public Spec(string id, string family, string mount, float width, float depth, float height,
                        float x, float y, float z)
            {
                Id = id; Family = family; Mount = mount;
                Expected = new Vector3(width, height, depth);
                Position = new Vector3(x, y, z);
            }
        }

        // X is width, Y height, Z depth. All positions are in metres.
        // The clear strip x=[-1.5,+1.5] is a 3m reference lane, NOT a ship corridor.
        static readonly Spec[] Specs =
        {
            new Spec("P15-01","Installations","wall",1.00f,.14f,.14f,-9f,2.0f,0f),
            new Spec("P15-02","Installations","wall",.60f,.08f,.40f,-5f,1.8f,0f),
            new Spec("P15-03","Installations","floor",.80f,.35f,1.80f,5f,0f,0f),
            new Spec("P16-01","Lighting","ceiling",1.20f,.15f,.12f,-9f,3.0f,5f),
            new Spec("P16-02","Lighting","wall",.35f,.14f,.22f,-5f,2.0f,5f),
            new Spec("P16-03","Lighting","wall",.20f,.20f,.30f,5f,2.0f,5f),
            new Spec("P17-01","Controls","floor",1.60f,.65f,1.10f,-9f,0f,10f),
            new Spec("P17-02","Controls","wall",.18f,.07f,.28f,-5f,1.5f,10f),
            new Spec("P17-03","Controls","floor",.40f,.30f,.55f,5f,0f,10f),
            new Spec("P18-01","Cargo","floor",.90f,.90f,.90f,-9f,0f,15f),
            new Spec("P18-02","Cargo","floor",2.10f,.80f,2.10f,-5f,0f,15f),
            new Spec("P18-03","Cargo","floor",1.00f,.70f,1.20f,5f,0f,15f),
            new Spec("P19-01","Furniture","floor",.95f,2.10f,.65f,-9f,0f,20f),
            new Spec("P19-02","Furniture","floor",.65f,.55f,1.80f,-5f,0f,20f),
            new Spec("P19-03","Furniture","floor",1.40f,.65f,.75f,5f,0f,20f),
            new Spec("P19-04","Furniture","floor",.60f,.60f,.95f,9f,0f,20f)
        };

        sealed class Found
        {
            public string Fbx, Blend;
            public string[] Previews;
            public GameObject Model;
            public Bounds Bounds;
            public int Triangles;
            public string Error;
        }

        static string[] SourceFiles()
        {
            return Directory.GetFiles(Application.dataPath, "*", SearchOption.AllDirectories)
                .Where(p => !p.Replace('\\','/').Contains("/C01InteriorProps/Generated/"))
                .Where(p => new[] { ".fbx", ".blend", ".png", ".jpg", ".jpeg" }
                    .Contains(Path.GetExtension(p).ToLowerInvariant())).ToArray();
        }

        static bool BelongsTo(string path, string id)
        {
            string n = Path.GetFileNameWithoutExtension(path);
            return n.Equals(id, StringComparison.OrdinalIgnoreCase) ||
                   (n.StartsWith(id, StringComparison.OrdinalIgnoreCase) &&
                    n.Length > id.Length && (n[id.Length] == '_' || n[id.Length] == '-'));
        }

        static string ToAssetPath(string absolute)
        {
            if (string.IsNullOrEmpty(absolute)) return null;
            string a = absolute.Replace('\\','/');
            string root = Application.dataPath.Replace('\\','/');
            return "Assets" + a.Substring(root.Length);
        }

        static Bounds CalculateBounds(GameObject instance, out int triangles)
        {
            var filters = instance.GetComponentsInChildren<MeshFilter>(true);
            triangles = 0;
            bool any = false;
            Bounds aggregate = new Bounds();
            foreach (var f in filters)
            {
                if (f.sharedMesh == null) continue;
                Mesh m = f.sharedMesh;
                triangles += (int)(m.GetIndexCount(0) / 3);
                Bounds mb = m.bounds;
                var tr = f.transform;
                foreach (int dx in new[] { -1, 1 })
                foreach (int dy in new[] { -1, 1 })
                foreach (int dz in new[] { -1, 1 })
                {
                    var pt = tr.TransformPoint(mb.center + Vector3.Scale(mb.extents,
                            new Vector3(dx, dy, dz)));
                    if (!any) { aggregate = new Bounds(pt, Vector3.zero); any = true; }
                    else aggregate.Encapsulate(pt);
                }
            }
            if (!any) throw new InvalidOperationException("No real MeshFilter with mesh");
            return aggregate;
        }

        static Dictionary<string,Found> Preflight(bool writeCsv)
        {
            string[] files = SourceFiles();
            var results = new Dictionary<string,Found>();
            foreach (var s in Specs)
            {
                var item = new Found { Previews = Array.Empty<string>() };
                results.Add(s.Id, item);
                var owned = files.Where(p => BelongsTo(p, s.Id)).ToArray();
                var fbx = owned.Where(p => Path.GetExtension(p).Equals(".fbx",StringComparison.OrdinalIgnoreCase)).ToArray();
                var blend = owned.Where(p => Path.GetExtension(p).Equals(".blend",StringComparison.OrdinalIgnoreCase)).ToArray();
                item.Previews = owned.Where(p => new[]{".png",".jpg",".jpeg"}
                    .Contains(Path.GetExtension(p).ToLowerInvariant())).Select(ToAssetPath).ToArray();
                item.Fbx = fbx.Length == 1 ? ToAssetPath(fbx[0]) : null;
                item.Blend = blend.Length == 1 ? ToAssetPath(blend[0]) : null;
                var errors = new List<string>();
                if (fbx.Length != 1) errors.Add("FBX count="+fbx.Length);
                if (blend.Length != 1) errors.Add("BLEND count="+blend.Length);
                if (item.Previews.Length < 3) errors.Add("previews="+item.Previews.Length+" (need 3 angles)");
                if (item.Fbx != null)
                {
                    item.Model = AssetDatabase.LoadAssetAtPath<GameObject>(item.Fbx);
                    if (item.Model == null) errors.Add("Unity FBX importer has no model GameObject");
                    else
                    {
                        var instance = (GameObject)PrefabUtility.InstantiatePrefab(item.Model);
                        try
                        {
                            item.Bounds = CalculateBounds(instance, out item.Triangles);
                            var d = item.Bounds.size;
                            if (d.x < MinMeshExtent || d.y < MinMeshExtent || d.z < MinMeshExtent)
                                errors.Add("degenerate imported bounds");
                            if (Mathf.Abs(d.x-s.Expected.x)>MaxDeviation ||
                                Mathf.Abs(d.y-s.Expected.y)>MaxDeviation ||
                                Mathf.Abs(d.z-s.Expected.z)>MaxDeviation)
                                errors.Add("dimensions differ >0.20m, measured="+d.ToString("F3"));
                            if (s.Mount == "floor" && Mathf.Abs(item.Bounds.min.y) > .05f)
                                errors.Add("floor origin does not rest at Y=0; minY="+item.Bounds.min.y.ToString("F3"));
                            if (instance.transform.localScale != Vector3.one)
                                errors.Add("model root scale not (1,1,1)");
                        }
                        catch (Exception ex) { errors.Add(ex.Message); }
                        finally { UnityEngine.Object.DestroyImmediate(instance); }
                    }
                }
                item.Error = string.Join("; ", errors);
            }
            if (writeCsv)
            {
                string root = Path.GetFullPath(Path.Combine(Application.dataPath, "../C01InteriorProps_QA"));
                Directory.CreateDirectory(root);
                var lines = new List<string>{ "id,status,fbx,blend,preview_count,triangles,bounds_xyz,problems" };
                foreach (var s in Specs)
                {
                    var r = results[s.Id];
                    string safe = r.Error.Replace("\"","\"\"");
                    lines.Add(string.Join(",",s.Id,string.IsNullOrEmpty(r.Error)?"LOCAL_IMPORT_CHECK_PASS":"BLOCKED",
                        r.Fbx??"MISSING",r.Blend??"MISSING",r.Previews.Length,r.Triangles,
                        "\""+r.Bounds.size.ToString("F3")+"\"","\""+safe+"\""));
                }
                File.WriteAllLines(Path.Combine(root,"PREFLIGHT.csv"),lines);
            }
            return results;
        }

        [MenuItem("C01/Interior Props/Preflight (16 real assets)")]
        public static void Audit()
        {
            var v = Preflight(true);
            int ready = v.Count(k => string.IsNullOrEmpty(k.Value.Error));
            Debug.Log("[C01-10] "+ready+"/16 assets with FBX, BLEND, 3 previews, imported meshes and provisional bounds. C01InteriorProps_QA/PREFLIGHT.csv");
        }

        static void EnsureFolder(string relative)
        {
            Directory.CreateDirectory(Path.GetFullPath(Path.Combine(Application.dataPath, "..", relative)));
        }

        static GameObject MakeIndividual(Spec spec, Found source)
        {
            var root = new GameObject(spec.Id);
            try
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(source.Model);
                instance.name = "SOURCE_" + spec.Id;
                instance.transform.SetParent(root.transform,false);
                // Do not recenter, scale, rotate or edit supplier mesh geometry.
                int count;
                Bounds b = CalculateBounds(root, out count);
                var c = root.AddComponent<BoxCollider>();
                c.center = b.center; c.size = b.size;  // provisional conservative collider
                var prefab = PrefabUtility.SaveAsPrefabAsset(root, Prefabs+"/"+spec.Id+".prefab");
                if (prefab == null) throw new Exception("Prefab save returned null for "+spec.Id);
                return prefab;
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        static void Add(GameObject root, Spec s, GameObject prefab, Vector3 position)
        {
            var group = root.transform.Find(s.Family);
            if (group == null)
            {
                var g = new GameObject(s.Family);
                g.transform.SetParent(root.transform,false);
                group = g.transform;
            }
            var copy = (GameObject)PrefabUtility.InstantiatePrefab(prefab,group);
            copy.name = s.Id;
            copy.transform.localPosition = position;
            copy.transform.localRotation = Quaternion.identity;
            copy.transform.localScale = Vector3.one;
        }

        static void Lighting()
        {
            var go = new GameObject("Showcase_EditorLight");
            var l = go.AddComponent<Light>();
            l.type = LightType.Directional;
            l.intensity = 1.0f;
            go.transform.rotation = Quaternion.Euler(48f,-25f,0f);
            var camera = new GameObject("Showcase_Camera");
            var c = camera.AddComponent<Camera>();
            c.transform.position = new Vector3(24f,29f,-19f);
            c.transform.LookAt(new Vector3(0f,0f,10f));
            c.farClipPlane = 200f;
            c.fieldOfView = 52f;
        }

        static void SaveNewScene(string file, GameObject prefab)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            PrefabUtility.InstantiatePrefab(prefab);
            Lighting();
            if (!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Scenes+"/"+file+".unity"))
                throw new IOException("SaveScene returned false: "+file);
        }

        static void SaveRoom(string filename, Dictionary<string,GameObject> prefabs, string[] ids, Vector3[] points)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var root = new GameObject(filename);
            for (int i=0; i<ids.Length; i++)
            {
                var s = Specs.First(x => x.Id == ids[i]);
                Add(root,s,prefabs[s.Id],points[i]);
            }
            Lighting();
            if (!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(),Scenes+"/"+filename+".unity"))
                throw new IOException("Unable to save "+filename);
        }

        [MenuItem("C01/Interior Props/Build Showcase + Cabin + Technical")]
        public static void Build()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
                throw new InvalidOperationException("Stop Play Mode first");
            var blocked = Preflight(true).Where(x => !string.IsNullOrEmpty(x.Value.Error))
                .Select(x => x.Key + ": " + x.Value.Error).ToArray();
            if (blocked.Length != 0)
                throw new InvalidOperationException("C01-10 integration BLOCKED; missing/invalid real assets:\n"+
                                                    string.Join("\n",blocked));
            if (Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty))
                throw new InvalidOperationException("Save existing edited scenes before generating new scenes");
            EnsureFolder(Prefabs); EnsureFolder(Scenes);
            AssetDatabase.Refresh();
            var inputs = Preflight(true);
            var prefabs = new Dictionary<string,GameObject>();
            foreach (var s in Specs) prefabs.Add(s.Id, MakeIndividual(s,inputs[s.Id]));
            var root = new GameObject(Master);
            GameObject masterAsset;
            try
            {
                foreach (var s in Specs) Add(root,s,prefabs[s.Id],s.Position);
                if (root.GetComponentsInChildren<MeshFilter>(true).Length == 0)
                    throw new InvalidOperationException("No meshes in master");
                masterAsset = PrefabUtility.SaveAsPrefabAsset(root,MasterPath);
                if (masterAsset == null) throw new IOException("Unable to save master prefab");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
            SaveNewScene("C01_InteriorProps_Showcase",masterAsset);
            SaveRoom("C01_InteriorProps_Cabin",prefabs,
                new[]{"P19-01","P19-02","P19-03","P19-04"},
                new[]{new Vector3(0,0,0),new Vector3(3.0f,0,0),new Vector3(2.2f,0,3.0f),new Vector3(1.2f,0,2.0f)});
            SaveRoom("C01_InteriorProps_TechnicalRoom",prefabs,
                new[]{"P15-01","P15-02","P15-03","P16-01","P17-03"},
                new[]{new Vector3(0,2,0),new Vector3(3,2,0),new Vector3(0,0,3),new Vector3(2,3,3),new Vector3(3,0,3)});
            AssetDatabase.SaveAssets();
            Debug.Log("[C01-10] Created 16 real-source individual prefabs, master prefab, and 3 standalone scenes. Manual clearance and independent C01-02 QA still NOT RUN.");
        }
    }
}
