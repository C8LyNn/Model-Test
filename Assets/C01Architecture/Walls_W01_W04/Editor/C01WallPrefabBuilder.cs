#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
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



    // PASS17 restores the detailed 572-triangle W02 native source in QA-only.
    // The old production W02_PANEL_WALL_1M is a 12-triangle prototype:
    // never silently substitute it, regardless of matching bounds.
    private static readonly string[] OriginalR2Names =
    {
        "W01_FULL_WALL_1M.fbx", "W02_TECH_PANEL_WALL_1M.fbx",
        "W03_CORNER_90_1M.fbx", "W04_DOOR_OPENING_2M.fbx"
    };
    private enum SourceVariant { OriginalR2, LegacyNative, Pass17Native }
    private static readonly int[] ExpectedTriangles = { 12, 572, 20, 28 };
    private static readonly string[] Pass17NativeFbxSha256 =
    {
        "c644e95d548cafbac61cebe000d7b0fb4b584a1fe4527565ba55d4c8e0415a79",
        "a23f602d8dd61a6dc61ee52af347e472f2e6f6ce546988f50409911d1b11a317",
        "9dcc8feca9475626e393910b4176d8c2eadf9c645d34e32718a417a10214807a",
        "6236dbb22a71d8ef0c8137ec263c14d59fbeda2a62eb299fe7cc05e1421dd51f"
    };

    // Byte-for-byte source identity pins. Original r2 hashes were recomputed
    // from the actual binary FBX files in the PASS13/PASS14 physical archives.
    // QA-only native candidate hashes come from the exact PR22 Git LFS OIDs,
    // NOT from the different historical Blender QA artifacts.
    private static readonly string[] OriginalR2Sha256 =
    {
        "7cc73ea116aa82cab5aa4833db2e6d3ce58888b47907402169d13ac2d7a7ff10",
        "3df87b6e69ca3dffb336356fcc80912854b836b45261311b488af8a38fd9f037",
        "3f6d37472239fe2ab61be27eaafb928ee9cf0253c9783d465d81ec649a9b2ee2",
        "c492539f3d33f65c90e0a0ac5279a6feded45d7cb14c3fefc147358dc9d7ecfe"
    };
    private static readonly string[] NativeCandidateLfsSha256 =
    {
        "4260732720f10688e9ee370d2a254b67c9263e3e8241b4da42f08e12fe99632f",
        null, // W02 candidate is never authorized.
        "4c268d554d4e5948ea1927e29b0d32fc581a6f9f14f41fd070bf116a8eb7864c",
        "b8751c3816ac6745b99ca17cf0489187dda6f1fd3e5fe4f209030aaccef0ddc8"
    };

    private static void VerifySourceSha256(string path, int index, SourceVariant variant)
    {
        string expected = variant == SourceVariant.Pass17Native
            ? Pass17NativeFbxSha256[index]
            : variant == SourceVariant.LegacyNative
                ? NativeCandidateLfsSha256[index] : OriginalR2Sha256[index];
        if (string.IsNullOrEmpty(expected))
            throw new InvalidOperationException(Ids[index] + ": no authorized FBX SHA256");
        if (!File.Exists(path))
            throw new FileNotFoundException("Physical hydrated binary FBX not found: " + path);
        string actual;
        using (var input = File.OpenRead(path))
        using (var sha = SHA256.Create())
            actual = BitConverter.ToString(sha.ComputeHash(input))
                .Replace("-", "").ToLowerInvariant();
        if (!string.Equals(actual, expected, StringComparison.Ordinal))
            throw new InvalidOperationException(
                Ids[index] + ": physical source FBX SHA256 mismatch at " + path +
                " (expected " + expected + ", actual " + actual +
                "). Reject stale/replaced/unhydrated LFS source.");
    }
    private static readonly int[] CandidateIndices = { 0, 2, 3 };
    private static readonly int[] AllIndices = { 0, 1, 2, 3 };

    private static string GetSourcePath(int index, SourceVariant variant)
    {
        if (variant == SourceVariant.OriginalR2)
            return Root + "/OriginalR2/FBX/" + OriginalR2Names[index];
        if (variant == SourceVariant.Pass17Native)
            // Exact files from SUCCESS run #41346578552 / artifact #13098949702,
            // unpacked under the same QA_Candidates path, NOT a production folder.
            return Root + "/QA_Candidates/PASS17_SourceRecovery/FBX/" +
                Ids[index] + "_" + Names[index] + ".fbx";
        if (variant != SourceVariant.LegacyNative)
            throw new ArgumentOutOfRangeException("variant");

        if (index == 1)
            throw new InvalidOperationException(
                "W02 legacy 12-triangle prototype is NOT detailed original r2.");
        return Root + "/FBX/" + Ids[index] + "_" + Names[index] + ".fbx";
    }

    // All source checks complete BEFORE writing any Unity assets.
    // These are authoring preflight checks, NOT C01-02 or Unity runtime acceptance.
    private static void PreflightMeshes(int[] indices, SourceVariant variant)
    {
        foreach (int index in indices)
        {
            string path = GetSourcePath(index, variant);
            // Hash must match before any Unity asset is written or staged.
            VerifySourceSha256(path, index, variant);
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
            var sourceRenderers = source.GetComponentsInChildren<MeshRenderer>(true);
            if (sourceRenderers.Length == 0)
                throw new InvalidOperationException(Ids[index] + ": source has no mesh renderers");
            foreach (var renderer in sourceRenderers)
            {
                var materials = renderer.sharedMaterials;
                var filter = renderer.GetComponent<MeshFilter>();
                if (materials == null || materials.Length == 0 ||
                    (filter != null && filter.sharedMesh != null &&
                     materials.Length < filter.sharedMesh.subMeshCount))
                    throw new InvalidOperationException(
                        Ids[index] + ": missing/insufficient FBX material slots");
            }
            if (meshes < 1 || triangles != ExpectedTriangles[index])
                throw new InvalidOperationException(Ids[index] +
                    ": FBX has " + triangles + " triangles across " + meshes +
                    " meshes; expected " + ExpectedTriangles[index] +
                    ". Candidate rejected without any prefab output.");
        }
    }

    [MenuItem("Tools/C01/C01-11/QA Only/Build W01-W04 Original R2 Prefabs")]
    public static void Build()
    {
        // Immutable original-r2 files must be staged by the owner first.
        BuildSelected(AllIndices, SourceVariant.OriginalR2);
    }

    [MenuItem("Tools/C01/C01-11/QA Only/Build W01 W03 W04 Existing Candidate Prefabs")]
    public static void BuildExistingCandidatesQaOnly()
    {
        // Always QUARANTINED: no detail-loss W02 and no active ship scene edits.
        BuildSelected(CandidateIndices, SourceVariant.LegacyNative);
    }

    [MenuItem("Tools/C01/C01-11/QA Only/Build PASS17 Real Blender W01-W04 Prefabs")]
    public static void BuildPass17NativeQaOnly()
    {
        // The first genuinely native detailed W02 (572 tris) is supported here.
        BuildSelected(AllIndices, SourceVariant.Pass17Native);
    }

    private static void BuildSelected(int[] indices, SourceVariant variant)
    {
        // Refresh imports before the SHA and mesh preflight. Does not edit the ship scene.
        AssetDatabase.Refresh();
        PreflightMeshes(indices, variant);

        // Never write into production prefab paths, regardless of mode.
        string prefabDir = Root + (variant == SourceVariant.Pass17Native
            ? "/QA_Candidates/PASS18_Unity/Prefabs"
            : variant == SourceVariant.LegacyNative
                ? "/QA_Candidates/LegacyNative/Prefabs"
                : "/QA_Candidates/OriginalR2/Prefabs");

        // Fail closed for ALL destinations before creating ANY prefab.
        foreach (int index in indices)
        {
            string output = prefabDir + "/C01-11_" + Ids[index] + "_QA_ONLY.prefab";
            if (File.Exists(output) ||
                AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(output) != null)
                throw new IOException("Refuse overwrite of existing QA prefab: " + output);
        }
        // Full original-r2 builds require URP, but must NOT overwrite
        // model-authored material slots with a single synthetic steel material.
        // Source geometry/material preflight happens before any prefab writes.
        if (Shader.Find("Universal Render Pipeline/Lit") == null)
            throw new InvalidOperationException("Unity 6 URP/Lit shader missing.");
        // Do not replace any ship prefab or touch the active spacecraft scene.
        Directory.CreateDirectory(prefabDir);

        // Preview scene prevents the QA utility from dirtying the artist's open
        // spacecraft scene, even on a failed imported mesh or prefab save.
        // Preflight above established all output paths absent. Track only
        // this invocation's attempted QA prefabs, so an interrupted build
        // cannot leave a misleading partial 1/4 or 2/4 result.
        var attemptedPrefabs = new List<string>();
        try
        {
        Scene previewScene = EditorSceneManager.NewPreviewScene();
        try
        {
        foreach (int index in indices)
        {
            string id = Ids[index];
            string assetPath = GetSourcePath(index, variant);
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
                temp.name = "C01-11_" + id + "_QA_ONLY";
                // Keep root transform/pivot exactly as imported from source FBX.
                var renderers = temp.GetComponentsInChildren<MeshRenderer>(true);
                if (renderers.Length == 0)
                    throw new InvalidOperationException(id + ": no imported MeshRenderer");

                // Renderer slots validated on every source BEFORE any write.
                // No synthetic steel material assignment or UV pivot mutation.
                AddColliders(temp, id);
                string output = prefabDir + "/C01-11_" + id +
                    "_QA_ONLY.prefab";
                // Record BEFORE saving: Unity may write bytes then throw.
                attemptedPrefabs.Add(output);
                var saved = PrefabUtility.SaveAsPrefabAsset(temp, output);
                if (saved == null)
                    throw new IOException(id + ": prefab save failed: " + output);
                Debug.Log("C01-11 prefab candidate saved (Unity QA pending): " + output);
            }
            finally { UnityEngine.Object.DestroyImmediate(temp); }
        }
        }
        finally { EditorSceneManager.ClosePreviewScene(previewScene); }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        }
        catch
        {
            // QA outputs only. Preserve the original exception while trying
            // to remove every prefab this invocation may have created.
            foreach (string output in attemptedPrefabs)
            {
                try
                {
                    if (AssetDatabase.LoadMainAssetAtPath(output) != null)
                    {
                        if (!AssetDatabase.DeleteAsset(output))
                            Debug.LogError("C01-11 QA rollback could not delete: " + output);
                    }
                    else if (File.Exists(output))
                    {
                        // Handles a partial on-disk file before AssetDatabase import.
                        // These paths are inside the isolated QA_Candidates folder.
                        File.Delete(output);
                        string meta = output + ".meta";
                        if (File.Exists(meta)) File.Delete(meta);
                    }
                }
                catch (Exception rollbackError)
                {
                    Debug.LogError("C01-11 QA rollback failed for " + output +
                                   ": " + rollbackError);
                }
            }
            AssetDatabase.Refresh();
            throw;
        }
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
