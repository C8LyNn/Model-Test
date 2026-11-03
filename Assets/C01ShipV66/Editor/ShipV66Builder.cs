using System;
using System.IO;
using System.Linq;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class ShipV66Builder
{
    public const string Source = "Assets/C01ShipV65/Scenes/C01_Ship_Multideck_v65.unity";
    public const string Scene = "Assets/C01ShipV66/Scenes/C01_Ship_Multideck_v66.unity";
    [MenuItem("Tools/C01 Ship v6.6/Build player view")]
    public static void Build()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Cannot build during Play mode");
        if (Enumerable.Range(0, SceneManager.sceneCount).Any(i => SceneManager.GetSceneAt(i).isDirty)) throw new InvalidOperationException("Save open scenes before building");
        Directory.CreateDirectory("Assets/C01ShipV66/Scenes");
        EditorSceneManager.OpenScene(Source, OpenSceneMode.Single);
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        if (explorer == null || explorer.player == null || explorer.view == null) throw new InvalidOperationException("Source scene has no complete explorer");
        var player = explorer.player;
        player.enabled = false;
        player.transform.SetPositionAndRotation(new Vector3(-4.5f, .02f, 43.5f), Quaternion.Euler(0, 90, 0));
        player.height = 1.8f; player.radius = .28f; player.center = new Vector3(0, .9f, 0); player.stepOffset = .18f;
        player.enabled = true;
        explorer.walkSpeed = 2.5f; explorer.sprintMultiplier = 2f; explorer.walkingFieldOfView = 75f;
        explorer.scaleAwareOverviewControls = true;
        explorer.view.nearClipPlane = .05f;
        explorer.SetWalking(true);
        EditorUtility.SetDirty(explorer);
        if (!EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), Scene)) throw new InvalidOperationException("Scene save failed");
        if (!EditorBuildSettings.scenes.Any(s => s.path == Scene))
            EditorBuildSettings.scenes = EditorBuildSettings.scenes.Concat(new[] { new EditorBuildSettingsScene(Scene, true) }).ToArray();
        AssetDatabase.SaveAssets();
    }

    public static void CaptureAndExport()
    {
        Directory.CreateDirectory("C01ShipV66_QA/Screenshots");
        EditorSceneManager.OpenScene(Scene, OpenSceneMode.Single);
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        explorer.SetWalking(true);
        Capture(explorer.view, "C01ShipV66_QA/Screenshots/player_bridge.png");
        explorer.SetWalking(false);
        Capture(explorer.view, "C01ShipV66_QA/Screenshots/ship_overview.png");
        AssetDatabase.ExportPackage(new[] { "Assets/C01ShipV66", "Assets/C01ShipV65", "Assets/C01ShipV5/Runtime" },
            Path.GetFullPath("C01ShipV66_QA/C01_Ship_Multideck_v6.6.unitypackage"), ExportPackageOptions.Recurse | ExportPackageOptions.IncludeDependencies);
    }
    static void Capture(Camera camera, string path)
    {
        var previous = camera.targetTexture; var active = RenderTexture.active;
        var texture = new RenderTexture(1280, 720, 24);
        try {
            camera.targetTexture = texture; camera.Render(); RenderTexture.active = texture;
            var image = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); image.Apply();
            File.WriteAllBytes(path, image.EncodeToPNG()); UnityEngine.Object.DestroyImmediate(image);
        } finally { camera.targetTexture = previous; RenderTexture.active = active; texture.Release(); UnityEngine.Object.DestroyImmediate(texture); }
    }
}
