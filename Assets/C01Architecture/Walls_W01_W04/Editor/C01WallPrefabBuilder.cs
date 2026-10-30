#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class C01WallPrefabBuilder
{
    private const string Root = "Assets/C01Architecture/Walls_W01_W04";
    private static readonly string[] Ids = { "W01", "W02", "W03", "W04" };
    private static readonly string[] Names =
    {
        "FULL_WALL_1M", "PANEL_WALL_1M", "CORNER_90_1M", "DOOR_OPENING_2M"
    };



    // Detailed W02 (572 tris) exists only as archived r2 binary source.
    // An earlier candidate named W02_PANEL_WALL_1M has 12 triangles:
    // never silently substitute it, regardless of matching bounds.
    private static readonly string[] OriginalR2Names =
    {
        "W01_FULL_WALL_1M.fbx", "W02_TECH_PANEL_WALL_1M.fbx",
        "W03_CORNER_90_1M.fbx", "W04_DOOR_OPENING_2M.fbx"
    };
    private static readonly int[] ExpectedTriangles = { 12, 572, 20, 28 };
    private static readonly int[] CandidateIndices = { 0, 2, 3 };
    private static readonly int[] AllIndices = { 0, 1, 2, 3 };

    private static string GetSourcePath(int index, bool qaCandidates)
    {
        if (!qaCandidates)
            return Root + "/OriginalR2/FBX/" + OriginalR2Names[index];

        if (index == 1)
            throw new InvalidOperationException(
                "W02 is blocked: 12-triangle prototype is NOT detailed original r2.");

        // Physically existing PR22 native FBX candidates, not original r2.
        return Root + "/FBX/" + Ids[index] + "_" + Names[index] + ".fbx";
    }

    // All source checks complete BEFORE writing any Unity assets.
    // These are authoring preflight checks, NOT C01-02 or Unity runtime acceptance.
    private static void PreflightMeshes(int[] indices, bool qaCandidates)
    {
        foreach (int index in indices)
        {
            string path = GetSourcePath(index, qaCandidates);
            var source = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (source == null)
                throw new FileNotFoundException("Required hydrated FBX missing: " + path);
            int triangles = 0;
            int meshes = 0;
            foreach (var filter in source.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh = filter.sharedMesh;
                if (mesh == null) continue;
                meshes++;
                int[] indexBuffer = mesh.triangles;
                triangles += indexBuffer.Length / 3;
                if (indexBuffer.Length % 3 != 0 || indexBuffer.Length == 0)
                    throw new InvalidOperationException(Ids[index] +
                        ": missing or malformed triangle index buffer");
                if (mesh.uv == null || mesh.uv.Length != mesh.vertexCount)
                    throw new InvalidOperationException(Ids[index] +
                        ": missing or incomplete UV0 on " + mesh.name);
                if (mesh.normals == null || mesh.normals.Length != mesh.vertexCount)
                    throw new InvalidOperationException(Ids[index] +
                        ": missing or incomplete normals on " + mesh.name);
                if (mesh.subMeshCount < 1)
                    throw new InvalidOperationException(Ids[index] +
                        ": missing material submeshes on " + mesh.name);
            }
            if (meshes < 1 || triangles != ExpectedTriangles[index])
                throw new InvalidOperationException(Ids[index] +
                    ": FBX has " + triangles + " triangles across " + meshes +
                    " meshes; expected " + ExpectedTriangles[index] +
                    ". Candidate rejected without any prefab output.");
        }
    }

    [MenuItem("Tools/C01/C01-11/Build W01-W04 Original R2 Prefabs")]
    public static void Build()
    {
        // FAIL CLOSED if any original FBX is missing. This currently includes
        // W02 original r2 until it is staged from the immutable source archive.
        BuildSelected(AllIndices, false);
    }

    [MenuItem("Tools/C01/C01-11/QA Only/Build W01 W03 W04 Existing Candidate Prefabs")]
    public static void BuildExistingCandidatesQaOnly()
    {
        // Always QUARANTINED: no detail-loss W02 and no active ship scene edits.
        BuildSelected(CandidateIndices, true);
    }

    private static void BuildSelected(int[] indices, bool qaCandidates)
    {
        PreflightMeshes(indices, qaCandidates);

        string prefabDir = Root + (qaCandidates ? "/QA_Candidates/Prefabs" : "/Prefabs");
        // Full original-r2 builds require URP, but must NOT overwrite
        // model-authored material slots with a single synthetic steel material.
        // Source geometry/material preflight happens before any prefab writes.
        if (!qaCandidates && Shader.Find("Universal Render Pipeline/Lit") == null)
            throw new InvalidOperationException("Unity 6 URP/Lit shader missing.");
        // Do not replace any ship prefab or touch the active spacecraft scene.
        Directory.CreateDirectory(prefabDir);

        // Preview scene prevents the QA utility from dirtying the artist's open
        // spacecraft scene, even on a failed imported mesh or prefab save.
        Scene previewScene = EditorSceneManager.NewPreviewScene();
        try
        {
        foreach (int index in indices)
        {
            string id = Ids[index];
            string assetPath = GetSourcePath(index, qaCandidates);
            var imported = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
            if (imported == null)
                throw new FileNotFoundException("Required FBX disappeared: " + assetPath);
            // Instantiate directly in previewScene. Creating an intermediate
            // GameObject in the active ship scene would risk dirtying that scene.
            var temp = (GameObject)PrefabUtility.InstantiatePrefab(imported, previewScene);
            if (temp == null)
                throw new InvalidOperationException(id + ": FBX prefab could not instantiate");
            try
            {
                temp.name = "C01-11_" + id + (qaCandidates ? "_QA_ONLY" : "");
                temp.transform.position = Vector3.zero;
                temp.transform.rotation = Quaternion.identity;
                temp.transform.localScale = Vector3.one;
                var renderers = temp.GetComponentsInChildren<MeshRenderer>(true);
                if (renderers.Length == 0)
                    throw new InvalidOperationException(id + ": no imported MeshRenderer");

                // Preserve every imported FBX material slot; changing
                // sharedMaterial here would collapse multi-material meshes.
                // This builder does not claim URP shader remapping QA.
                foreach (var renderer in renderers)
                {
                    var assigned = renderer.sharedMaterials;
                    if (assigned == null || assigned.Length == 0)
                        throw new InvalidOperationException(
                            id + ": imported FBX renderer has no material slots");
                    var filter = renderer.GetComponent<MeshFilter>();
                    if (filter != null && filter.sharedMesh != null &&
                        assigned.Length < filter.sharedMesh.subMeshCount)
                        throw new InvalidOperationException(
                            id + ": fewer imported material slots than submeshes");
                }
                AddColliders(temp, id);
                string output = prefabDir + "/C01-11_" + id +
                    (qaCandidates ? "_QA_ONLY.prefab" : ".prefab");
                PrefabUtility.SaveAsPrefabAsset(temp, output);
                Debug.Log("C01-11 prefab candidate saved (Unity QA pending): " + output);
            }
            finally { UnityEngine.Object.DestroyImmediate(temp); }
        }
        }
        finally { EditorSceneManager.ClosePreviewScene(previewScene); }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("C01-11 prefab authoring complete; engine QA and C01-02 approval NOT RUN.");
    }

    private static void AddBox(GameObject go, Vector3 center, Vector3 size)
    {
        var box = go.AddComponent<BoxCollider>();
        box.center = center;
        box.size = size;
    }
    private static void AddColliders(GameObject go, string id)
    {
        switch (id)
        {
            case "W01":
            case "W02":
                AddBox(go, new Vector3(.5f, 1.5f, .1f), new Vector3(1f, 3f, .2f));
                break;
            case "W03":
                AddBox(go, new Vector3(0f, 1.5f, -.4f), new Vector3(1f, 3f, .2f));
                AddBox(go, new Vector3(-.4f, 1.5f, .1f), new Vector3(.2f, 3f, .8f));
                break;
            case "W04":
                AddBox(go, new Vector3(.1f, 1.2f, .1f), new Vector3(.2f, 2.4f, .2f));
                AddBox(go, new Vector3(1.9f, 1.2f, .1f), new Vector3(.2f, 2.4f, .2f));
                AddBox(go, new Vector3(1f, 2.7f, .1f), new Vector3(2f, .6f, .2f));
                break;
            default: throw new ArgumentException("Unknown wall ID " + id);
        }
    }
}
#endif
