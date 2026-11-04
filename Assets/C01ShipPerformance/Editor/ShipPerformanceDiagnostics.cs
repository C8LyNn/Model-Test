using System;
using System.IO;
using System.Reflection;
using System.Diagnostics;
using C01.Ship.V5;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ShipPerformanceDiagnostics
{
    [Serializable] private class Counts
    {
        public int gates, leaves, lifts, airlocks, renderers, colliders, lights;
    }

    public static void Baseline() { Run("v68_perf_baseline"); }
    public static void After() { Run("v68_perf_after"); }
    public static void GatesBaseline() { MeasureGates("gates_before"); }
    public static void GatesAfter() { MeasureGates("gates_after"); }
    public static void LaddersBaseline() { MeasureLadders("ladders_before"); }
    public static void LaddersAfter() { MeasureLadders("ladders_after"); }
    public static void MeasureAndExport() { After(); Export(); }

    public static void Export()
    {
        Directory.CreateDirectory("C01ShipPerformance_QA");
        var path = Path.GetFullPath("C01ShipPerformance_QA/C01_Ship_Multideck_v6.8.1.unitypackage");
        AssetDatabase.ExportPackage(new[] {
            "Assets/C01ShipV68", "Assets/C01ShipV5/Runtime",
            "Assets/C01ShipV6/Cargo/Runtime", "Assets/C01ShipV61/Signage"
        }, path, ExportPackageOptions.Recurse | ExportPackageOptions.IncludeDependencies);
        if (!File.Exists(path) || new FileInfo(path).Length < 1024)
            throw new IOException("Unity package export failed: " + path);
        UnityEngine.Debug.Log("C01 PERFORMANCE PACKAGE " + path);
    }

    [Serializable] private class LadderTiming
    {
        public int markers, validLadders, iterations;
        public double[] millisecondsPerQuery;
    }

    private static void MeasureLadders(string tag)
    {
        EditorSceneManager.OpenScene("Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity");
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        explorer.SetWalking(true);
        explorer.player.enabled = true;
        explorer.player.transform.position = new Vector3(10000,10000,10000);
        var markers = explorer.master.GetComponentsInChildren<ShipInstanceV5>(true);
        var result = new LadderTiming { markers=markers.Length, iterations=100, millisecondsPerQuery=new double[5] };
        foreach (var marker in markers)
            if (marker.modelId == "P_Ladder_3m" && marker.placementId != null && marker.placementId.EndsWith("_LADDER_0")) result.validLadders++;
        for (int i=0;i<5;i++) explorer.TryBeginClimb();
        for (int sample=0; sample<result.millisecondsPerQuery.Length; sample++)
        {
            var watch = Stopwatch.StartNew();
            for (int i=0;i<result.iterations;i++) if (explorer.TryBeginClimb()) throw new Exception("Unexpected ladder");
            watch.Stop();
            result.millisecondsPerQuery[sample] = watch.Elapsed.TotalMilliseconds / result.iterations;
        }
        Directory.CreateDirectory("C01ShipPerformance_QA");
        File.WriteAllText("C01ShipPerformance_QA/"+tag+".json", JsonUtility.ToJson(result, true));
        UnityEngine.Debug.Log("C01 LADDER QUERY " + JsonUtility.ToJson(result));
    }

    [Serializable] private class GateTiming
    {
        public int gates, leaves, iterations;
        public double[] millisecondsPerTick;
    }

    private static void MeasureGates(string tag)
    {
        EditorSceneManager.OpenScene("Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity");
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        var gates = explorer.master.GetComponentsInChildren<ShipGateV5>(true);
        foreach (var gate in gates) gate.SetImmediate(0);
        var method = typeof(ShipGateV5).GetMethod("FixedUpdate", BindingFlags.Instance | BindingFlags.NonPublic);
        if (method == null) throw new Exception("FixedUpdate not found");
        for (int j = 0; j < 2; j++) foreach (var gate in gates) method.Invoke(gate, null);
        var result = new GateTiming { gates=gates.Length, iterations=20, millisecondsPerTick=new double[5] };
        foreach (var gate in gates) result.leaves += gate.leaves.Length;
        for (int sample = 0; sample < result.millisecondsPerTick.Length; sample++)
        {
            var watch = Stopwatch.StartNew();
            for (int j = 0; j < result.iterations; j++) foreach (var gate in gates) method.Invoke(gate, null);
            watch.Stop();
            result.millisecondsPerTick[sample] = watch.Elapsed.TotalMilliseconds / result.iterations;
        }
        Directory.CreateDirectory("C01ShipPerformance_QA");
        File.WriteAllText("C01ShipPerformance_QA/" + tag + ".json", JsonUtility.ToJson(result, true));
        UnityEngine.Debug.Log("C01 IDLE GATES " + JsonUtility.ToJson(result));
    }

    private static void Run(string tag)
    {
        const string scene = "Assets/C01ShipV68/Scenes/C01_Ship_Multideck_v68.unity";
        ShipV61Diagnostics.Capture(scene, tag);
        var explorer = UnityEngine.Object.FindFirstObjectByType<ShipExplorerV5>();
        var gates = explorer.master.GetComponentsInChildren<ShipGateV5>(true);
        var counts = new Counts {
            gates = gates.Length,
            lifts = explorer.master.GetComponentsInChildren<ShipLiftV5>(true).Length,
            airlocks = explorer.master.GetComponentsInChildren<ShipAirlockV5>(true).Length,
            renderers = explorer.master.GetComponentsInChildren<Renderer>(true).Length,
            colliders = explorer.master.GetComponentsInChildren<Collider>(true).Length,
            lights = UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None).Length
        };
        foreach (var gate in gates) counts.leaves += gate.leaves.Length;
        Directory.CreateDirectory("C01ShipPerformance_QA");
        File.WriteAllText("C01ShipPerformance_QA/" + tag + "_counts.json", JsonUtility.ToJson(counts, true));
        UnityEngine.Debug.Log("C01 PERFORMANCE COUNTS " + JsonUtility.ToJson(counts));
    }
}
