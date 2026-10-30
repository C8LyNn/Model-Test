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

    [MenuItem("Tools/C01/C01-11/Build W01-W04 Prefabs")]
    public static void Build()
    {
        var shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
            throw new InvalidOperationException("Unity 6 URP/Lit shader missing.");
        Directory.CreateDirectory(Root + "/Materials");
        Directory.CreateDirectory(Root + "/Prefabs");
        for (int index = 0; index < Ids.Length; index++)
        {
            var id = Ids[index];
            var assetPath = Root + "/FBX/" + id + "_" + Names[index] + ".fbx";
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
