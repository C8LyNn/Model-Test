using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.TestTools.TestRunner.Api;
using C01.Ship.Editor;

namespace C01.Integration {
    // Runs only on an explicit menu action or a local Library request; never on normal project opening.
    [InitializeOnLoad]
    public static class ModelTestIntegration {
        const string Key = "C01.ModelTest.IntegrationStage";
        static readonly string Project = Path.GetDirectoryName(Application.dataPath);
        static readonly string Request = Path.Combine(Project, "Library/C01ShipIntegration.request");
        static readonly string Output = Path.Combine(Project, "C01Ship_QA");
        static TestRunnerApi api;
        static readonly Results callbacks = new Results();
        static ModelTestIntegration() {
            api = ScriptableObject.CreateInstance<TestRunnerApi>();
            api.RegisterCallbacks(callbacks);
            EditorApplication.update += Update;
            File.WriteAllText(Path.Combine(Project, "Library/C01ShipIntegration.driver"), "2");
        }
        static void Progress(string message) {
            Directory.CreateDirectory(Output);
            File.AppendAllText(Path.Combine(Output, "integration_progress.txt"), DateTime.UtcNow.ToString("o") + " " + message + "\n");
            Debug.Log("C01_MODEL_TEST " + message);
        }
        [MenuItem("Tools/C01 Ship/Open imported ship")]
        public static void OpenShip() {
            if (EditorApplication.isPlayingOrWillChangePlaymode) throw new InvalidOperationException("Exit Play mode first.");
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(ShipBuilder.ScenePath);
            FrameShip();
        }
        [MenuItem("Tools/C01 Ship/Verify imported project")]
        public static void Verify() { File.WriteAllText(Request, "verify"); }
        static void FrameShip() {
            var master = ShipValidation.Master();
            if (master != null) Selection.activeGameObject = master;
            var view = SceneView.lastActiveSceneView;
            if (view != null) { view.orthographic = true; view.LookAtDirect(new Vector3(21.5f, 0, 10.5f), Quaternion.Euler(55, 0, 0), 44); }
        }
        static void Update() {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorApplication.isPlayingOrWillChangePlaymode) return;
            string stage = SessionState.GetString(Key, "");
            try {
                if (stage == "" && File.Exists(Request)) {
                    try { File.Delete(Request); } catch (IOException) { return; }
                    for (int i = 0; i < SceneManager.sceneCount; i++)
                        if (SceneManager.GetSceneAt(i).isDirty) throw new InvalidOperationException("Unsaved scene detected. Save it, then use Tools/C01 Ship/Verify imported project.");
                    SessionState.SetInt(Key + ".failures", 0);
                    Progress("START Unity " + Application.unityVersion);
                    EditorSceneManager.OpenScene(ShipBuilder.ScenePath);
                    var scenes = EditorBuildSettings.scenes.Where(s => s.path != ShipBuilder.ScenePath).ToList();
                    scenes.Insert(0, new EditorBuildSettingsScene(ShipBuilder.ScenePath, true));
                    const string baseScene = "Assets/C01Modular/Scenes/C01_PASS02_ThreeRooms.unity";
                    if (!scenes.Any(s => s.path == baseScene)) scenes.Add(new EditorBuildSettingsScene(baseScene, true));
                    EditorBuildSettings.scenes = scenes.ToArray();
                    Progress("Scene opened; existing build scenes and render pipeline retained.");
                    ShipValidation.Run();
                    ShipValidation.Capture();
                    Progress("Geometry/navigation/FBX audit and 12 renders completed.");
                    SessionState.SetString(Key, "edit-running");
                    api.Execute(new ExecutionSettings(new Filter { testMode = TestMode.EditMode, assemblyNames = new[] { "C01.EditTests", "C01Ship.EditTests" } }));
                } else if (stage == "play-queued") {
                    SessionState.SetString(Key, "play-running");
                    api.Execute(new ExecutionSettings(new Filter { testMode = TestMode.PlayMode, assemblyNames = new[] { "C01.PlayTests", "C01Ship.PlayTests" } }));
                } else if (stage == "restore") {
                    EditorSceneManager.OpenScene(ShipBuilder.ScenePath);
                    FrameShip();
                    SessionState.SetString(Key, "");
                    string status = SessionState.GetInt(Key + ".failures", 0) == 0 ? "PASS" : "FAIL";
                    File.WriteAllText(Path.Combine(Output, "integration_status.txt"), status + "\nUnity " + Application.unityVersion + "\n");
                    Progress("DONE " + status + "; imported ship scene left open.");
                }
            } catch (Exception e) {
                SessionState.SetString(Key, "");
                Progress("FAIL " + e);
                File.WriteAllText(Path.Combine(Output, "integration_status.txt"), "FAIL\n" + e);
                Debug.LogException(e);
            }
        }
        sealed class Results : ICallbacks {
            public void RunStarted(ITestAdaptor tests) { }
            public void TestStarted(ITestAdaptor test) { }
            public void TestFinished(ITestResultAdaptor result) { }
            public void RunFinished(ITestResultAdaptor result) {
                string stage = SessionState.GetString(Key, "");
                if (stage != "edit-running" && stage != "play-running") return;
                string mode = stage == "edit-running" ? "editmode" : "playmode";
                TestRunnerApi.SaveResultToFile(result, Path.Combine(Output, "model_test_" + mode + ".xml"));
                int failures = result.FailCount + result.SkipCount + (result.PassCount == 0 ? 1 : 0);
                SessionState.SetInt(Key + ".failures", SessionState.GetInt(Key + ".failures", 0) + failures);
                Progress(mode + " " + result.ResultState + " passed=" + result.PassCount + " failed=" + result.FailCount + " skipped=" + result.SkipCount);
                SessionState.SetString(Key, stage == "edit-running" ? "play-queued" : "restore");
            }
        }
    }
}
