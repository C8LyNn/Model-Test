using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.TestTools.TestRunner.Api;

namespace C01.Ship.V4.Editor {
    [InitializeOnLoad]
    public static class ShipV4Batch {
        const string Key="C01.ShipV4.Batch";
        static readonly string Project=Path.GetDirectoryName(Application.dataPath);
        static string Request=>Path.Combine(Project,"Library/ShipV4.request");
        static TestRunnerApi api;static bool busy;
        static ShipV4Batch(){api=ScriptableObject.CreateInstance<TestRunnerApi>();api.RegisterCallbacks(new Results());EditorApplication.update+=Update;Directory.CreateDirectory(Path.Combine(Project,"Library"));File.WriteAllText(Path.Combine(Project,"Library/ShipV4.driver"),"4.0");}
        static void Progress(string message){Directory.CreateDirectory(ShipV4Builder.QA);File.AppendAllText(Path.Combine(ShipV4Builder.QA,"progress.txt"),DateTime.UtcNow.ToString("o")+" "+message+"\n");Debug.Log("SHIPV4 "+message);}
        static void Queue(string command){string temporary=Request+".new";File.WriteAllText(temporary,command);if(File.Exists(Request))throw new InvalidOperationException("A ShipV4 request is already pending");File.Move(temporary,Request);}
        static string Claim(){var claimed=Request+".processing";if(File.Exists(claimed))File.Delete(claimed);try{File.Move(Request,claimed);}catch(IOException){return null;}try{return File.ReadAllText(claimed).Trim();}finally{File.Delete(claimed);}}
        [MenuItem("Tools/C01 Ship v4/Rebuild and verify")]
        public static void RebuildAndVerify()=>Queue("rebuild");
        [MenuItem("Tools/C01 Ship v4/Verify")]
        public static void Verify()=>Queue("verify");
        [MenuItem("Tools/C01 Ship v4/Open generated ship")]
        public static void OpenGenerated()=>Queue("open");
        static void PreserveDirtyScenes(){
            const string folder="Assets/C01UserSnapshots";
            for(int i=0;i<SceneManager.sceneCount;i++){
                var scene=SceneManager.GetSceneAt(i);if(!scene.isDirty)continue;
                Directory.CreateDirectory(folder);AssetDatabase.Refresh();
                string name=string.IsNullOrEmpty(scene.name)?"Untitled":scene.name;
                name=string.Concat(name.Select(c=>Path.GetInvalidFileNameChars().Contains(c)?'_':c));
                string path=AssetDatabase.GenerateUniqueAssetPath(folder+"/"+name+"_before_v4.unity");
                if(!EditorSceneManager.SaveScene(scene,path,false))throw new Exception("Could not preserve unsaved scene "+name);
                Progress("User unsaved scene preserved as "+path);
            }
        }
        static void Update(){
            if(!busy&&SessionState.GetString(Key,"")==""&&File.Exists(Request)&&EditorApplication.isPlaying){try{if(File.ReadAllText(Request).Trim()=="preserve-rebuild")EditorApplication.isPlaying=false;}catch(IOException){}return;}
            if(!busy&&SessionState.GetString(Key,"")!=""&&File.Exists(Request)){var command=Claim();if(command=="cancel"){SessionState.SetInt(Key+".failures",1);SessionState.SetBool(Key+".cancelled",true);Progress("CANCEL requested");string run=SessionState.GetString(Key+".run","");if(!string.IsNullOrEmpty(run))TestRunnerApi.CancelTestRun(run);if(!EditorApplication.isPlayingOrWillChangePlaymode)SessionState.SetString(Key,"restore");}else if(command!=null)Progress("Ignored request while v4 runner active: "+command);}
            if(busy||EditorApplication.isCompiling||EditorApplication.isUpdating||EditorApplication.isPlayingOrWillChangePlaymode)return;
            var stage=SessionState.GetString(Key,"");bool canRestore=!string.IsNullOrEmpty(stage);
            try{busy=true;
                if(stage==""&&File.Exists(Request)){
                    string command=Claim();if(command==null)return;if(command=="cancel"){Progress("CANCELLED before start");return;}
                    if(command=="open"){PreserveDirtyScenes();EditorSceneManager.OpenScene(ShipV4Builder.ScenePath);Progress("Opened generated v4 scene");return;}
                    if(command=="preserve-rebuild"){PreserveDirtyScenes();command="rebuild";}
                    if(command!="rebuild"&&command!="verify")throw new Exception("Unknown request: "+command);
                    if(Enumerable.Range(0,SceneManager.sceneCount).Any(i=>SceneManager.GetSceneAt(i).isDirty))throw new Exception("Unsaved scenes: save them before requesting ShipV4");
                    Directory.CreateDirectory(ShipV4Builder.QA);SessionState.SetString(Key+".scene",SceneManager.GetActiveScene().path);SessionState.SetString(Key+".scenes",JsonUtility.ToJson(new SceneState{scenes=EditorSceneManager.GetSceneManagerSetup().Select(s=>new SceneEntry{path=s.path,loaded=s.isLoaded,active=s.isActive}).ToArray()}));canRestore=true;SessionState.SetInt(Key+".failures",0);SessionState.SetBool(Key+".cancelled",false);File.WriteAllText(Path.Combine(ShipV4Builder.QA,"status.txt"),"RUNNING");Progress("START "+command+" Unity "+Application.unityVersion);
                    var host=HostSnapshot.Capture();if(command=="rebuild")ShipV4Builder.Build();host.AssertRetained();File.WriteAllText(Path.Combine(ShipV4Builder.QA,"host_settings_qa.json"),JsonUtility.ToJson(host,true));EditorSceneManager.OpenScene(ShipV4Builder.ScenePath);
                    try{ShipV4Validation.Run();Progress("Source/physics/coverage/NavMesh/FBX audit PASS");}catch(Exception audit){SessionState.SetInt(Key+".failures",1);Progress("Audit FAIL; collecting remaining evidence: "+audit.Message);}try{ShipV4Capture.Capture();Progress("Camera.Render complete");}catch(Exception capture){SessionState.SetInt(Key+".failures",1);Progress("Capture FAIL: "+capture);}SessionState.SetString(Key,"edit-running");SessionState.SetString(Key+".run",api.Execute(new ExecutionSettings(new Filter{testMode=TestMode.EditMode,assemblyNames=new[]{"C01ShipV4.EditTests"}})));
                }else if(stage=="play-queued"){SessionState.SetString(Key,"play-running");SessionState.SetString(Key+".run",api.Execute(new ExecutionSettings(new Filter{testMode=TestMode.PlayMode,assemblyNames=new[]{"C01ShipV4.PlayTests"}})));}
                else if(stage=="restore"){bool pass=SessionState.GetInt(Key+".failures",0)==0;Restore();if(pass)ShipV4Builder.Export();SessionState.SetString(Key,"");File.WriteAllText(Path.Combine(ShipV4Builder.QA,"status.txt"),pass?"PASS":"FAIL");Progress("DONE "+(pass?"PASS":"FAIL"));if(Application.isBatchMode)EditorApplication.Exit(pass?0:1);}
            }catch(Exception e){SessionState.SetString(Key,"");if(canRestore)try{Restore();}catch(Exception restore){Debug.LogException(restore);}Progress("FAIL "+e);File.WriteAllText(Path.Combine(ShipV4Builder.QA,"status.txt"),"FAIL\n"+e);Debug.LogException(e);if(Application.isBatchMode)EditorApplication.Exit(1);}finally{busy=false;}
        }
        [Serializable] class SceneEntry {public string path;public bool loaded,active;}
        [Serializable] class SceneState {public SceneEntry[] scenes;}
        static void Restore(){var json=SessionState.GetString(Key+".scenes","");var saved=string.IsNullOrEmpty(json)?null:JsonUtility.FromJson<SceneState>(json);if(saved!=null&&saved.scenes.Length>0&&saved.scenes.All(s=>!string.IsNullOrEmpty(s.path)&&File.Exists(s.path))){EditorSceneManager.RestoreSceneManagerSetup(saved.scenes.Select(s=>new SceneSetup{path=s.path,isLoaded=s.loaded,isActive=s.active}).ToArray());return;}string previous=SessionState.GetString(Key+".scene","");if(!string.IsNullOrEmpty(previous)&&File.Exists(previous))EditorSceneManager.OpenScene(previous);else if(File.Exists(ShipV4Builder.ScenePath))EditorSceneManager.OpenScene(ShipV4Builder.ScenePath);}
        [Serializable] public class HostSnapshot {
            public string product,defaultPipeline,qualityPipeline,colorSpace;public string[] scenes,qualityPipelines;public int quality;public bool retained;
            public static HostSnapshot Capture(){var h=new HostSnapshot{product=PlayerSettings.productName,defaultPipeline=AssetDatabase.GetAssetPath(GraphicsSettings.defaultRenderPipeline),qualityPipeline=AssetDatabase.GetAssetPath(QualitySettings.renderPipeline),colorSpace=PlayerSettings.colorSpace.ToString(),scenes=EditorBuildSettings.scenes.Select(s=>s.path+"|"+s.enabled).ToArray(),quality=QualitySettings.GetQualityLevel()};h.qualityPipelines=Enumerable.Range(0,QualitySettings.names.Length).Select(i=>AssetDatabase.GetAssetPath(QualitySettings.GetRenderPipelineAssetAt(i))).ToArray();return h;}
            public void AssertRetained(){var n=Capture();retained=product==n.product&&defaultPipeline==n.defaultPipeline&&qualityPipeline==n.qualityPipeline&&colorSpace==n.colorSpace&&quality==n.quality&&qualityPipelines.SequenceEqual(n.qualityPipelines)&&scenes.Where(s=>!s.StartsWith(ShipV4Builder.ScenePath+"|",StringComparison.Ordinal)).All(s=>n.scenes.Contains(s));if(!retained)throw new Exception("Host product/pipeline/quality/color/build scenes changed");}
        }
        sealed class Results:ICallbacks {
            public void RunStarted(ITestAdaptor tests){}public void TestStarted(ITestAdaptor test){}public void TestFinished(ITestResultAdaptor result){}
            public void RunFinished(ITestResultAdaptor result){var stage=SessionState.GetString(Key,"");if(stage!="edit-running"&&stage!="play-running")return;string mode=stage=="edit-running"?"editmode":"playmode";TestRunnerApi.SaveResultToFile(result,Path.Combine(ShipV4Builder.QA,mode+".xml"));int failed=result.FailCount+result.SkipCount+(result.PassCount==0?1:0);SessionState.SetInt(Key+".failures",SessionState.GetInt(Key+".failures",0)+failed);Progress(mode+" "+result.ResultState+" pass="+result.PassCount+" fail="+result.FailCount+" skipped="+result.SkipCount);SessionState.SetString(Key,stage=="edit-running"&&!SessionState.GetBool(Key+".cancelled",false)?"play-queued":"restore");}
        }
    }
}
