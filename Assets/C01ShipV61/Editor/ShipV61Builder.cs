using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using C01.Ship.V61.Signage;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class ShipV61Builder
{
    public const string ScenePath = "Assets/C01ShipV61/Scenes/C01_Ship_Multideck_v61.unity";
    [MenuItem("Tools/C01 Ship v6.1/Build polished scene")]
    public static void Build()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Stop Play mode before building");
        if (Enumerable.Range(0, UnityEngine.SceneManagement.SceneManager.sceneCount)
            .Any(i => UnityEngine.SceneManagement.SceneManager.GetSceneAt(i).isDirty))
            throw new InvalidOperationException("Save open scenes before building v6.1");
        var scene = EditorSceneManager.OpenScene("Assets/C01ShipV6/Scenes/C01_Ship_Multideck_v6.unity");
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if (explorer == null || explorer.master == null) throw new Exception("Ship master missing");
        var shader = AssetDatabase.LoadAssetAtPath<Shader>("Assets/C01ShipV61/Signage/ButtonText.shader");
        if (shader == null || !shader.isSupported) throw new Exception("Button shader unavailable");
        var signage = explorer.master.AddComponent<ButtonSignage>();
        signage.Configure(shader);
        // A modest neutral ambient lift restores readability in large spaces without
        // increasing the 102 existing real-time lights or changing geometry.
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(.40f, .46f, .54f);
        Directory.CreateDirectory("Assets/C01ShipV61/Scenes");
        if (!EditorSceneManager.SaveScene(scene, ScenePath)) throw new Exception("Could not save v6.1 scene");
        if (!EditorBuildSettings.scenes.Any(s => s.path == ScenePath))
            EditorBuildSettings.scenes = EditorBuildSettings.scenes.Concat(new[] { new EditorBuildSettingsScene(ScenePath, true) }).ToArray();
        AssetDatabase.SaveAssets();
        Debug.Log("C01 V6.1 BUILD COMPLETE");
    }

    public static void Export()
    {
        var folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../C01ShipV61_QA"));
        Directory.CreateDirectory(folder);
        AssetDatabase.ExportPackage(new[] { "Assets/C01ShipV61", "Assets/C01ShipV6", "Assets/C01ShipV5/Runtime" },
            Path.Combine(folder, "C01_Ship_Multideck_v6.1.unitypackage"), ExportPackageOptions.Recurse | ExportPackageOptions.IncludeDependencies);
    }
}
