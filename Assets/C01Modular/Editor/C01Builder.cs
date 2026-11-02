using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace C01.Editor {
    public static class C01Builder {
        public const string Root="Assets/C01Modular";
        public const string MasterPath=Root+"/Prefabs/C01_PASS02_ThreeRooms_MASTER.prefab";
        public const string ScenePath=Root+"/Scenes/C01_PASS02_ThreeRooms.unity";
        public static string ResolveQaPath(string projectRoot){
            string container=Path.GetDirectoryName(Path.GetFullPath(projectRoot));
            return File.Exists(Path.Combine(container,"Tools/build_kit.py"))?Path.Combine(container,"QA"):Path.Combine(Path.GetFullPath(projectRoot),"C01_QA");
        }
        public static string QA => ResolveQaPath(Path.GetDirectoryName(Application.dataPath));
        public static KitData Read() => JsonUtility.FromJson<KitData>(File.ReadAllText(Root+"/Data/kit.json"));
        public static Vector3 V(float[] v) => new Vector3(v[0],v[1],v[2]);

        static Dictionary<string,Material> materials;
        static Dictionary<string,GameObject> sources;
        static Mesh BoxMesh(PartData p) {
            var lo=V(p.lo);var hi=V(p.hi);var v=new List<Vector3>();var ns=new List<Vector3>();var uv=new List<Vector2>();var tris=new List<int>();
            var corners=new [] {new Vector3(lo.x,lo.y,lo.z),new Vector3(hi.x,lo.y,lo.z),new Vector3(hi.x,hi.y,lo.z),new Vector3(lo.x,hi.y,lo.z),new Vector3(lo.x,lo.y,hi.z),new Vector3(hi.x,lo.y,hi.z),new Vector3(hi.x,hi.y,hi.z),new Vector3(lo.x,hi.y,hi.z)};
            int[][] faces={new[]{0,3,2,1},new[]{4,5,6,7},new[]{0,4,7,3},new[]{1,2,6,5},new[]{0,1,5,4},new[]{3,7,6,2}};
            Vector3[] normals={Vector3.back,Vector3.forward,Vector3.left,Vector3.right,Vector3.down,Vector3.up};
            for(int f=0;f<6;f++){
                int b=v.Count;
                for(int j=0;j<4;j++){v.Add(corners[faces[f][j]]);ns.Add(normals[f]);uv.Add(new Vector2(j==1||j==2?1:0,j>=2?1:0));}
                tris.AddRange(new[]{b,b+1,b+2,b,b+2,b+3});
            }
            var mesh=new Mesh();mesh.SetVertices(v);mesh.SetNormals(ns);mesh.SetUVs(0,uv);mesh.SetTriangles(tris,0);mesh.RecalculateBounds();return mesh;
        }
        static void SaveAsset(UnityEngine.Object value,string path) {
            var old=AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path);
            if(old!=null){EditorUtility.CopySerialized(value,old);UnityEngine.Object.DestroyImmediate(value);}else AssetDatabase.CreateAsset(value,path);
        }
        static void SetupURP() {
            string rpPath=Root+"/Settings/C01_URP.asset";
            var rp=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(rpPath);
            if(rp==null){var renderer=ScriptableObject.CreateInstance<UniversalRendererData>();AssetDatabase.CreateAsset(renderer,Root+"/Settings/C01_Renderer.asset");rp=UniversalRenderPipelineAsset.Create(renderer);AssetDatabase.CreateAsset(rp,rpPath);}
            GraphicsSettings.defaultRenderPipeline=rp;QualitySettings.renderPipeline=rp;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.companyName="C01";PlayerSettings.productName="C01 PASS02 Modular Repair";
        }
        [MenuItem("Tools/C01 PASS02/Build all prefabs and scenes")]
        public static void Build() {
            foreach(var dir in new[]{"Prefabs","Meshes","Materials","Scenes","Settings"})Directory.CreateDirectory(Root+"/"+dir);
            Directory.CreateDirectory(QA);AssetDatabase.Refresh();SetupURP();
            var spec=Read();materials=new Dictionary<string,Material>();sources=new Dictionary<string,GameObject>();
            foreach(var d in spec.materials){
                var mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));mat.name="C01_"+d.role;
                mat.SetColor("_BaseColor",new Color(d.color[0],d.color[1],d.color[2],d.color[3]));mat.SetFloat("_Smoothness",.22f);
                string path=Root+"/Materials/"+mat.name+".mat";SaveAsset(mat,path);materials[d.role]=AssetDatabase.LoadAssetAtPath<Material>(path);
            }
            // First save source modules; nested children are attached in a second pass.
            foreach(var m in spec.modules){
                var go=new GameObject(m.id);var info=go.AddComponent<C01Module>();info.moduleId=m.id;info.family=m.family;info.sockets=m.sockets;
                for(int i=0;i<m.parts.Length;i++){
                    var p=m.parts[i];string meshPath=Root+"/Meshes/"+m.id+"_"+i+".asset";var mesh=BoxMesh(p);mesh.name=m.id+"_"+i;SaveAsset(mesh,meshPath);
                    var part=new GameObject(p.role+"_"+i);part.transform.SetParent(go.transform,false);
                    part.AddComponent<MeshFilter>().sharedMesh=AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);part.AddComponent<MeshRenderer>().sharedMaterial=materials[p.role];
                    var bc=part.AddComponent<BoxCollider>();bc.center=(V(p.lo)+V(p.hi))*.5f;bc.size=V(p.hi)-V(p.lo);
                    var solid=part.AddComponent<C01Solid>();solid.role=p.role;solid.partIndex=i;solid.lo=V(p.lo);solid.hi=V(p.hi);
                }
                foreach(var s in m.sockets){var socket=new GameObject("Socket_"+s.name);socket.transform.SetParent(go.transform,false);socket.transform.localPosition=V(s.position);}
                sources[m.id]=PrefabUtility.SaveAsPrefabAsset(go,Root+"/Prefabs/"+m.id+".prefab");UnityEngine.Object.DestroyImmediate(go);
            }
            foreach(var m in spec.modules.Where(x=>x.children!=null&&x.children.Length>0)){
                var go=PrefabUtility.LoadPrefabContents(Root+"/Prefabs/"+m.id+".prefab");
                foreach(var child in m.children){
                    var instance=(GameObject)PrefabUtility.InstantiatePrefab(sources[child.module]);instance.name=child.socket;instance.transform.SetParent(go.transform,false);instance.transform.localPosition=V(child.position);instance.transform.localRotation=Quaternion.Euler(0,child.yaw,0);
                    if(child.socket=="Hinge"){
                        var rb=instance.AddComponent<Rigidbody>();rb.isKinematic=true;rb.useGravity=false;
                        var dc=go.AddComponent<C01Door>();dc.hinge=instance.transform;
                    }
                }
                PrefabUtility.SaveAsPrefabAsset(go,Root+"/Prefabs/"+m.id+".prefab");PrefabUtility.UnloadPrefabContents(go);sources[m.id]=AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Prefabs/"+m.id+".prefab");
            }
            var master=new GameObject("C01_PASS02_ThreeRooms_MASTER");var groups=new Dictionary<string,Transform>();
            foreach(var p in spec.placements){
                if(!groups.ContainsKey(p.group)){var g=new GameObject(p.group);g.transform.SetParent(master.transform,false);groups[p.group]=g.transform;}
                var go=(GameObject)PrefabUtility.InstantiatePrefab(sources[p.id]);go.name=p.tag;go.transform.SetParent(groups[p.group],false);go.transform.localPosition=new Vector3(p.x,p.y,p.z);go.transform.localRotation=Quaternion.Euler(0,p.yaw,0);go.GetComponent<C01Module>().placementTag=p.tag;
            }
            PrefabUtility.SaveAsPrefabAsset(master,MasterPath);UnityEngine.Object.DestroyImmediate(master);
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            master=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(MasterPath));
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.6f,.65f,.7f);RenderSettings.fog=false;
            var sun=new GameObject("Key Light");sun.transform.rotation=Quaternion.Euler(55,-30,0);var light=sun.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.8f;
            for(int i=0;i<3;i++){var g=new GameObject("Room Light "+i);g.transform.position=new Vector3(3+6*i,2.7f,4.5f);var l=g.AddComponent<Light>();l.type=LightType.Point;l.range=10;l.intensity=6;l.color=new Color(.8f,.9f,1);}
            var cameraGO=new GameObject("Main Camera");cameraGO.tag="MainCamera";var cam=cameraGO.AddComponent<Camera>();cameraGO.AddComponent<AudioListener>();cam.nearClipPlane=.03f;cam.farClipPlane=200;cam.backgroundColor=new Color(.025f,.035f,.05f);cam.clearFlags=CameraClearFlags.SolidColor;
            cameraGO.AddComponent<UniversalAdditionalCameraData>();cameraGO.transform.position=new Vector3(9,19,-15);cameraGO.transform.LookAt(new Vector3(9,0,4.5f));cam.fieldOfView=48;
            var demo=cameraGO.AddComponent<C01Demo>();demo.master=master;demo.doors=master.GetComponentsInChildren<C01Door>(true);
            EditorSceneManager.SaveScene(scene,ScenePath);EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(ScenePath,true)};AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            BuildJointLab();EditorSceneManager.OpenScene(ScenePath);
            Debug.Log("C01_BUILD_COMPLETE: "+spec.modules.Length+" source module prefabs + master; "+spec.placements.Length+" placements");
        }
        static void BuildJointLab(){
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            string[] types={"END","STRAIGHT","CORNER","T","CROSS"};
            float[][] directions={new[]{0f},new[]{0f,180f},new[]{0f,90f},new[]{0f,90f,180f},new[]{0f,90f,180f,270f}};
            for(int i=0;i<types.Length;i++){
                Vector3 center=new Vector3(i*9,0,0);var pad=new GameObject(types[i]);
                var node=(GameObject)PrefabUtility.InstantiatePrefab(sources["N_"+types[i]]);node.transform.SetParent(pad.transform,false);node.transform.position=center;
                foreach(float yaw in directions[i]){
                    var wall=(GameObject)PrefabUtility.InstantiatePrefab(sources["W01_Wall_3m"]);wall.transform.SetParent(pad.transform,false);wall.transform.SetPositionAndRotation(center,Quaternion.Euler(0,yaw,0));
                    var cap=(GameObject)PrefabUtility.InstantiatePrefab(sources["N_END"]);cap.transform.SetParent(pad.transform,false);cap.transform.position=wall.transform.TransformPoint(new Vector3(3,0,0));
                }
            }
            EditorSceneManager.SaveScene(scene,Root+"/Scenes/C01_PASS02_JointLab.unity");
        }
        [MenuItem("Tools/C01 PASS02/Run build, QA, renders and export")]
        public static void Batch(){
            try { Build();C01Validation.Run();C01Validation.Capture();ExportPackage();File.WriteAllText(Path.Combine(QA,"unity_batch_success.txt"),Application.unityVersion+"\n"+DateTime.UtcNow.ToString("O"));if(Application.isBatchMode)EditorApplication.Exit(0); }
            catch(Exception e){Debug.LogException(e);File.WriteAllText(Path.Combine(QA,"unity_batch_failure.txt"),e.ToString());if(Application.isBatchMode)EditorApplication.Exit(1);throw;}
        }
        static void ExportPackage(){
            string taskRoot=Path.GetFullPath(Path.Combine(Application.dataPath,"../.."));string docs=Root+"/Documentation";Directory.CreateDirectory(docs);
            foreach(string relative in File.Exists(Path.Combine(taskRoot,"Tools/build_kit.py"))?new[]{"README_PL.md","docs/STANDARD_PL.md","docs/QA_REPORT_PL.md","QA/static_qa.json","QA/blender_export.json","QA/unity_geometry_qa.json","QA/verification_summary.json"}:Array.Empty<string>()){
                string source=Path.Combine(taskRoot,relative);if(File.Exists(source))File.Copy(source,Path.Combine(docs,Path.GetFileName(source)),true);
            }
            AssetDatabase.Refresh();AssetDatabase.ExportPackage(Root,Path.Combine(QA,"C01_PASS02_v2.0.unitypackage"),ExportPackageOptions.Recurse);
        }
        public static void ExportOnly(){ExportPackage();if(Application.isBatchMode)EditorApplication.Exit(0);}
    }
}
