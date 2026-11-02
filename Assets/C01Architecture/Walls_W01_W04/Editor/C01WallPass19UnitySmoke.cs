#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Independent QA-only Unity Editor gate for the four exact PASS17 Blender FBXs.
/// Execute in a DISPOSABLE Unity 6000.3 URP project with the PASS18 handoff
/// FBX files staged under QA_Candidates/PASS17_SourceRecovery/FBX.
/// Does not modify the active ship scene or the 36 P15-P19 production assets.
/// </summary>
public static class C01WallPass19UnitySmoke
{
    private const string Root = "Assets/C01Architecture/Walls_W01_W04";
    private const string FbxDir = Root + "/QA_Candidates/PASS17_SourceRecovery/FBX";
    private const string PrefabDir = Root + "/QA_Candidates/PASS18_Unity/Prefabs";
    private const string ReportDir = Root + "/QA_Candidates/PASS19_Unity/Reports";
    private static readonly string[] Ids = { "W01", "W02", "W03", "W04" };
    private static readonly string[] Filenames =
    {
        "W01_FULL_WALL_1M.fbx", "W02_PANEL_WALL_1M.fbx",
        "W03_CORNER_90_1M.fbx", "W04_DOOR_OPENING_2M.fbx"
    };
    private static readonly int[] ExpectedTriangles = { 12, 572, 20, 28 };
    private static readonly int[] ExpectedBoxColliders = { 1, 1, 2, 3 };

    [Serializable]
    private sealed class AssetEvidence
    {
        public string id;
        public string fbxSha256;
        public int triangles;
        public int meshFilters;
        public int boxColliders;
        public int materials;
        public string shaders;
        public int verticesOutsideColliders;
    }

    [Serializable]
    private sealed class Evidence
    {
        public string status;
        public string unityVersion;
        public string graphicsPipeline;
        public string purpose;
        public List<AssetEvidence> assets = new List<AssetEvidence>();
        public string error;
    }

    [MenuItem("Tools/C01/C01-11/QA Only/PASS19 Unity Smoke 4 Walls")]
    public static void RunPass19()
    {
        // This entry point may be invoked with -batchmode -quit -executeMethod.
        // Existing destination prefabs are not overwritten: use a fresh QA workspace.
        string reportPath = ReportDir + "/C01-11_PASS19_UNITY_EDITOR_RESULT.json";
        if (File.Exists(reportPath))
            throw new IOException("Refusing to overwrite prior Unity evidence: " + reportPath);

        var evidence = new Evidence
        {
            status = "FAIL",
            unityVersion = Application.unityVersion,
            graphicsPipeline = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline == null
                ? "NO_ACTIVE_SCRIPTABLE_RENDER_PIPELINE"
                : UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline.GetType().FullName,
            purpose = "QA-only exact PASS17 native walls; not ship or 36-prop approval"
        };

        try
        {
            // This method verifies exact immutable FBX SHA before creating anything,
            // and refuses pre-existing prefab outputs in QA_Candidates.
            C01WallPrefabBuilder.BuildPass17NativeQaOnly();
            AssetDatabase.Refresh();

            Scene preview = EditorSceneManager.NewPreviewScene();
            try
            {
                for (int i = 0; i < Ids.Length; i++)
                {
                    string id = Ids[i];
                    string sourcePath = FbxDir + "/" + Filenames[i];
                    string prefabPath = PrefabDir + "/C01-11_" + id + "_QA_ONLY.prefab";
                    var source = AssetDatabase.LoadAssetAtPath<GameObject>(sourcePath);
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
                    if (source == null || prefab == null)
                        throw new FileNotFoundException(id + ": source or generated prefab missing");

                    var instance = PrefabUtility.InstantiatePrefab(prefab, preview) as GameObject;
                    if (instance == null)
                        throw new InvalidOperationException(id + ": prefab could not instantiate");
                    try
                    {
                        // No source root pivot, scale, or rotation modification.
                        if ((source.transform.localPosition - instance.transform.localPosition).sqrMagnitude > 1e-10f ||
                            (source.transform.localScale - instance.transform.localScale).sqrMagnitude > 1e-10f ||
                            Quaternion.Angle(source.transform.localRotation, instance.transform.localRotation) > .001f)
                            throw new InvalidOperationException(id + ": imported root transform/pivot changed");

                        var boxes = instance.GetComponentsInChildren<BoxCollider>(true);
                        if (boxes.Length != ExpectedBoxColliders[i])
                            throw new InvalidOperationException(id + ": unexpected box collider count " + boxes.Length);

                        int tris = 0, filters = 0, materialCount = 0, outside = 0;
                        var shaders = new List<string>();
                        foreach (var filter in instance.GetComponentsInChildren<MeshFilter>(true))
                        {
                            var mesh = filter.sharedMesh;
                            if (mesh == null)
                                throw new InvalidOperationException(id + ": missing mesh");
                            filters++;
                            tris += mesh.triangles.Length / 3;
                            if (mesh.uv.Length != mesh.vertexCount || mesh.normals.Length != mesh.vertexCount)
                                throw new InvalidOperationException(id + ": UV0/normal corruption");
                            foreach (var vertex in mesh.vertices)
                            {
                                var world = filter.transform.TransformPoint(vertex);
                                bool inside = false;
                                foreach (var box in boxes)
                                {
                                    Bounds bounds = box.bounds;
                                    bounds.Expand(.002f); // 1mm numerical tolerance per side.
                                    if (bounds.Contains(world)) { inside = true; break; }
                                }
                                if (!inside) outside++;
                            }
                        }
                        foreach (var renderer in instance.GetComponentsInChildren<MeshRenderer>(true))
                        {
                            var filter = renderer.GetComponent<MeshFilter>();
                            var materials = renderer.sharedMaterials;
                            if (filter == null || filter.sharedMesh == null ||
                                materials.Length < filter.sharedMesh.subMeshCount)
                                throw new InvalidOperationException(id + ": material/submesh count mismatch");

                            foreach (var material in materials)
                            {
                                if (material == null || material.shader == null)
                                    throw new InvalidOperationException(id + ": missing material/shader");
                                string shaderName = material.shader.name;
                                shaders.Add(shaderName);
                                materialCount++;
                                // Reporting non-URP shaders is a release HOLD, never silently rewrite
                                // authentic imported FBX material slots in this QA-only source gate.
                                if (!shaderName.StartsWith("Universal Render Pipeline/", StringComparison.Ordinal))
                                    throw new InvalidOperationException(id + ": non-URP material: " + shaderName);
                            }
                        }
                        if (filters == 0 || tris != ExpectedTriangles[i] || outside != 0)
                            throw new InvalidOperationException(id +
                                ": triangle/collider fit FAIL. triangles=" + tris +
                                " outside=" + outside);

                        evidence.assets.Add(new AssetEvidence
                        {
                            id = id,
                            fbxSha256 = Sha256(sourcePath),
                            triangles = tris,
                            meshFilters = filters,
                            boxColliders = boxes.Length,
                            materials = materialCount,
                            shaders = string.Join(";", shaders.ToArray()),
                            verticesOutsideColliders = outside
                        });
                    }
                    finally { UnityEngine.Object.DestroyImmediate(instance); }
                }
            }
            finally { EditorSceneManager.ClosePreviewScene(preview); }

            evidence.status = "UNITY_EDITOR_SMOKE_PASS";
            Debug.Log("C01-11 PASS19 real Unity 6 URP QA-only smoke PASS 4/4; approval still requires C01-02.");
        }
        catch (Exception ex)
        {
            evidence.status = "UNITY_EDITOR_SMOKE_HOLD";
            evidence.error = ex.ToString();
            Debug.LogError("C01-11 PASS19 Unity smoke HOLD: " + ex);
            throw; // Never turn a failed batchmode QA into a false PASS.
        }
        finally
        {
            Directory.CreateDirectory(ReportDir);
            File.WriteAllText(reportPath, JsonUtility.ToJson(evidence, true));
            AssetDatabase.Refresh();
        }
    }

    private static string Sha256(string path)
    {
        using (var stream = File.OpenRead(path))
        using (var hash = SHA256.Create())
            return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
}
#endif
