#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class C01WallPrefabBuilder
{
    private const string Root = "Assets/C01Architecture/Walls_W01_W04";
    private static readonly string[] Ids = { "W01", "W02", "W03", "W04" };
    private static readonly string[] Names =
    {
        "FULL_WALL_1M", "PANEL_WALL_1M", "CORNER_90_1M", "DOOR_OPENING_2M"
    };


    // PASS04: fail closed before writing any prefab or material.
    // Archived detailed r2 W02 contains 572 actual triangles; the 12-triangle
    // replacement candidate is NOT an authorized topology repair.
    private static void PreflightOriginalMeshIntegrity()
    {
        int[] expectedTriangles = { 12, 572, 20, 28 };
        for (int i = 0; i < Ids.Length; i++)
        {
            string path = GetOriginalSourcePath(i);
            var source = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (source == null)
                throw new FileNotFoundException("Original imported FBX missing: " + path);
            int count = 0;
            foreach (var filter in source.GetComponentsInChildren<MeshFilter>(true))
            {
                if (filter.sharedMesh == null) continue;
                count += (int)filter.sharedMesh.triangles.Length / 3;
            }
            if (count != expectedTriangles[i])
                throw new InvalidOperationException(
                    Ids[i] + ": source mismatch (" + count + " triangles, required " +
                    expectedTriangles[i] + "). Refuse to replace original r2 geometry.");
        }
        // This is only a source identity triangle gate, not independent QA or
        // approval for replacing any existing ship prefab.
    }


    // PASS05: load ONLY authentic archived r2 FBX; never the simplified
    // 12-triangle candidate W02 from the earlier authoring prototype.
    private static readonly string[] OriginalR2Names =
    {
        "W01_FULL_WALL_1M.fbx", "W02_TECH_PANEL_WALL_1M.fbx",
        "W03_CORNER_90_1M.fbx", "W04_DOOR_OPENING_2M.fbx"
    };
    private static string GetOriginalSourcePath(int index)
    {
        return Root + "/OriginalR2/FBX/" + OriginalR2Names[index];
    }

    [MenuItem("Tools/C01/C01-11/Build W01-W04 Prefabs")]
    public static void Build()
    {
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
            throw new InvalidOperationException("Unity 6 URP/Lit shader missing.");
        PreflightOriginalMeshIntegrity();
        Directory.CreateDirectory(Root + "/Materials");
        Directory.CreateDirectory(Root + "/Prefabs");
        for (int index = 0; index < Ids.Length; index++)
        {
            var id = Ids[index];
            var assetPath = GetOriginalSourcePath(index);
            var imported = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
            if (imported == null)
                throw new FileNotFoundException("Required imported FBX missing: " + assetPath);
            var temp = new GameObject("C01-11_" + id);
            try
            {
                temp.transform.position = Vector3.zero;
                temp.transform.rotation = Quaternion.identity;
                temp.transform.localScale = Vector3.one;
                var mesh = (GameObject)PrefabUtility.InstantiatePrefab(imported);
                mesh.transform.SetParent(temp.transform, false);
                mesh.transform.localPosition = Vector3.zero;
                mesh.transform.localRotation = Quaternion.identity;
                mesh.transform.localScale = Vector3.one;
                var renderers = mesh.GetComponentsInChildren<MeshRenderer>();
                if (renderers.Length == 0)
                    throw new InvalidOperationException(id + ": imported mesh has no renderers");
                var matPath = Root + "/Materials/C01-11_" + id + "_Steel.mat";
                var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                if (mat == null)
                {
                    mat = new Material(shader);
                    AssetDatabase.CreateAsset(mat, matPath);
                }
                var tint = id == "W02" ? new Color(.26f, .38f, .48f) :
                           id == "W03" ? new Color(.49f, .53f, .57f) :
                           id == "W04" ? new Color(.40f, .54f, .62f) :
                                         new Color(.43f, .51f, .58f);
                mat.SetColor("_BaseColor", tint);
                mat.SetFloat("_Metallic", .45f);
                mat.SetFloat("_Smoothness", .32f);
                EditorUtility.SetDirty(mat);
                foreach (var r in renderers) r.sharedMaterial = mat;
                AddColliders(temp, id);
                var prefabPath = Root + "/Prefabs/C01-11_" + id + ".prefab";
                PrefabUtility.SaveAsPrefabAsset(temp, prefabPath);
                Debug.Log("C01-11 prefab candidate written: " + prefabPath);
            }
            finally { UnityEngine.Object.DestroyImmediate(temp); }
        }
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("C01-11 W01-W04 prefab build complete. UNITY PHYSICAL QA STILL REQUIRED.");
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
