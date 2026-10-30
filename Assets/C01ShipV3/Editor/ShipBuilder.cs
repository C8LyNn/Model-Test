using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEditor;
using UnityEditor.SceneManagement;

namespace C01.Ship.Editor {
    public static class ShipBuilder {
        public const string Root="Assets/C01ShipV3",MasterName="C01_SHIP_FROM_PLAN_MASTER",MasterPath=Root+"/Prefabs/C01_SHIP_FROM_PLAN_MASTER.prefab",ScenePath=Root+"/Scenes/C01_Ship_FromPlan.unity";
        public static string ResolveQaPath(string project){string container=Path.GetDirectoryName(Path.GetFullPath(project));return File.Exists(Path.Combine(container,"Tools/build_ship.py"))?Path.Combine(container,"QA"):Path.Combine(Path.GetFullPath(project),"C01Ship_QA");}
        public static string QA=>ResolveQaPath(Path.GetDirectoryName(Application.dataPath));
        public static ShipData Read()=>JsonUtility.FromJson<ShipData>(File.ReadAllText(Root+"/Data/ship.json"));
        static Dictionary<string,Material> materials;
        public static Vector3 V(float[] p)=>new Vector3(p[0],p[1],p[2]);
        static Color ColorOf(float[] c)=>new Color(c[0],c[1],c[2],c.Length>3?c[3]:1);
        static void Save(UnityEngine.Object obj,string path){
            var old=AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path);
            if(old!=null){
                if(old is Mesh mesh&&obj is Mesh generated){
                    // Mesh setters invalidate the existing GPU buffers; serialized copies can leave the preview stale until reload.
                    mesh.Clear();mesh.indexFormat=generated.indexFormat;mesh.vertices=generated.vertices;mesh.uv=generated.uv;mesh.normals=generated.normals;mesh.triangles=generated.triangles;mesh.bounds=generated.bounds;mesh.name=generated.name;mesh.UploadMeshData(false);
                }else EditorUtility.CopySerialized(obj,old);
                EditorUtility.SetDirty(old);UnityEngine.Object.DestroyImmediate(obj);
            }else AssetDatabase.CreateAsset(obj,path);
        }
        public static Mesh Prism(ShipPartData p){
            int n=p.outline.Length/2;var vertices=new List<Vector3>();var tris=new List<int>();var uv=new List<Vector2>();
            void Vertex(int i,float y){vertices.Add(new Vector3(p.outline[i*2],y,p.outline[i*2+1]));uv.Add(new Vector2(p.outline[i*2],p.outline[i*2+1]));}
            for(int i=0;i<n;i++)Vertex(i,p.y0);for(int i=1;i<n-1;i++)tris.AddRange(new[]{0,i,i+1});
            for(int i=0;i<n;i++)Vertex(i,p.y1);for(int i=1;i<n-1;i++)tris.AddRange(new[]{n,n+i+1,n+i});
            for(int i=0;i<n;i++){int j=(i+1)%n,b=vertices.Count;Vertex(i,p.y0);Vertex(i,p.y1);Vertex(j,p.y1);Vertex(j,p.y0);tris.AddRange(new[]{b,b+1,b+2,b,b+2,b+3});}
            var mesh=new Mesh();mesh.SetVertices(vertices);mesh.SetUVs(0,uv);mesh.SetTriangles(tris,0);mesh.RecalculateNormals();mesh.RecalculateBounds();return mesh;
        }
        static Material Material(string role,Color color,bool glass=false){
            var m=new Material(Shader.Find("Universal Render Pipeline/Lit"));m.name="Ship_"+role;m.SetColor("_BaseColor",color);m.SetFloat("_Smoothness",glass?.72f:.28f);m.SetFloat("_Metallic",glass?0:.25f);
            if(role=="SCREEN"||role=="THRUST"){m.EnableKeyword("_EMISSION");m.SetColor("_EmissionColor",color*1.3f);}
            if(glass){m.SetFloat("_Surface",1);m.SetFloat("_Blend",0);m.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);m.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);m.SetFloat("_ZWrite",0);m.SetFloat("_Cull",0);m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");m.renderQueue=3000;}
            string path=Root+"/Materials/"+m.name+".mat";Save(m,path);return AssetDatabase.LoadAssetAtPath<Material>(path);
        }
        [MenuItem("Tools/C01 Ship/Build ship from reference plan")]
        public static void Build(){
            if(!Application.isBatchMode&&Enumerable.Range(0,UnityEngine.SceneManagement.SceneManager.sceneCount).Any(i=>UnityEngine.SceneManagement.SceneManager.GetSceneAt(i).isDirty))throw new InvalidOperationException("Save modified scenes before rebuilding the ship.");
            foreach(var dir in new[]{"Meshes","Materials","Prefabs","Scenes","Models"})Directory.CreateDirectory(Root+"/"+dir);Directory.CreateDirectory(QA);AssetDatabase.Refresh();
            var data=Read();materials=new Dictionary<string,Material>();
            foreach(var d in data.materials)materials[d.role]=Material(d.role,ColorOf(d.color),d.role=="GLASS");
            foreach(string role in new[]{"FLOOR","ROOF"})materials[role]=AssetDatabase.LoadAssetAtPath<Material>("Assets/C01Modular/Materials/C01_"+role+".mat");
            var tint=data.zones.ToDictionary(z=>z.id,z=>Material("FLOOR_"+z.id,ColorOf(z.color)));
            var sources=new Dictionary<string,GameObject>();
            foreach(var d in data.modules){
                var go=new GameObject(d.id);
                for(int i=0;i<d.parts.Length;i++){
                    var p=d.parts[i];var mesh=Prism(p);mesh.name=d.id+"_"+i;string meshPath=Root+"/Meshes/"+mesh.name+".asset";Save(mesh,meshPath);
                    var child=new GameObject(p.role+"_"+i);child.transform.SetParent(go.transform,false);var saved=AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);child.AddComponent<MeshFilter>().sharedMesh=saved;child.AddComponent<MeshRenderer>().sharedMaterial=materials[p.role];
                    var solid=child.AddComponent<ShipSolid>();solid.role=p.role;solid.moduleId=d.id;solid.partIndex=i;
                    bool box=p.outline.Length==8&&p.outline.Select((v,k)=>new {v,k}).Where(a=>a.k%2==0).Select(a=>a.v).Distinct().Count()==2&&p.outline.Select((v,k)=>new {v,k}).Where(a=>a.k%2==1).Select(a=>a.v).Distinct().Count()==2;
                    if(box){var bc=child.AddComponent<BoxCollider>();bc.center=saved.bounds.center;bc.size=saved.bounds.size;}else{var mc=child.AddComponent<MeshCollider>();mc.sharedMesh=saved;mc.convex=true;}
                }
                sources[d.id]=PrefabUtility.SaveAsPrefabAsset(go,Root+"/Prefabs/"+d.id+".prefab");UnityEngine.Object.DestroyImmediate(go);
            }
            foreach(var id in data.placements.Select(p=>p.module).Distinct())if(!sources.ContainsKey(id)){sources[id]=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/C01Modular/Prefabs/"+id+".prefab");if(sources[id]==null)throw new Exception("Missing reused module "+id);}
            var master=new GameObject(MasterName);var groups=new Dictionary<string,Transform>();var instances=new Dictionary<string,GameObject>();
            foreach(var p in data.placements){
                if(!groups.ContainsKey(p.category)){var group=new GameObject(p.category);group.transform.SetParent(master.transform,false);groups[p.category]=group.transform;}
                var go=(GameObject)PrefabUtility.InstantiatePrefab(sources[p.module]);go.name=p.id;go.transform.SetParent(groups[p.category],false);go.transform.localPosition=new Vector3(p.x,p.y,p.z);go.transform.localRotation=Quaternion.Euler(0,p.yaw,0);instances[p.id]=go;
                var info=go.AddComponent<ShipInstance>();info.placementId=p.id;info.moduleId=p.module;info.category=p.category;info.zone=p.zone;
                if(p.category=="Floors"&&tint.ContainsKey(p.zone)){
                    foreach(var solid in go.GetComponentsInChildren<C01Solid>())if(solid.role=="FLOOR")solid.GetComponent<Renderer>().sharedMaterial=tint[p.zone];
                    foreach(var solid in go.GetComponentsInChildren<ShipSolid>())solid.GetComponent<Renderer>().sharedMaterial=tint[p.zone];
                }
            }
            var labels=new GameObject("Labels");labels.transform.SetParent(master.transform,false);
            var markers=new GameObject("Zones");markers.transform.SetParent(master.transform,false);var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            foreach(var z in data.zones){
                var marker=new GameObject(z.id);marker.transform.SetParent(markers.transform,false);marker.transform.localPosition=V(z.waypoint);var zone=marker.AddComponent<ShipZone>();zone.zoneId=z.id;zone.displayName=z.label;zone.kind=z.kind;
                if(z.id.StartsWith("X")||z.id.StartsWith("MAIN"))continue;
                var label=new GameObject(z.label);label.transform.SetParent(labels.transform,false);label.transform.localPosition=V(z.waypoint)+Vector3.up*3.3f;label.transform.localRotation=Quaternion.Euler(90,0,0);
                var text=label.AddComponent<TextMesh>();text.font=font;text.fontSize=64;text.characterSize=z.id=="STERN"?.105f:z.kind=="sector"?.19f:z.kind=="cabin"?.13f:.19f;text.anchor=TextAnchor.MiddleCenter;text.alignment=TextAlignment.Center;text.color=new Color(.82f,.93f,1);text.text=z.id=="STERN"?"RUFA\nWĘZEŁ\nŚLUZ":z.label;
                label.GetComponent<MeshRenderer>().sharedMaterial=font.material;
            }
            var locks=new GameObject("Airlocks");locks.transform.SetParent(master.transform,false);
            foreach(var d in data.airlocks){var g=new GameObject(d.id);g.transform.SetParent(locks.transform,false);var a=g.AddComponent<ShipAirlock>();a.doorA=instances[d.doors[0]].GetComponent<C01Door>();a.doorB=instances[d.doors[1]].GetComponent<C01Door>();}
            groups["Ceilings"].gameObject.SetActive(false);
            PrefabUtility.SaveAsPrefabAsset(master,MasterPath);UnityEngine.Object.DestroyImmediate(master);
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);master=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(MasterPath));
            if(GraphicsSettings.defaultRenderPipeline==null){var rp=AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/C01Modular/Settings/C01_URP.asset");GraphicsSettings.defaultRenderPipeline=rp;QualitySettings.renderPipeline=rp;}
            RenderSettings.ambientMode=AmbientMode.Flat;RenderSettings.ambientLight=new Color(.32f,.39f,.48f);RenderSettings.fog=false;
            var sun=new GameObject("Ship key light");sun.transform.rotation=Quaternion.Euler(48,-35,0);var light=sun.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.4f;light.shadows=LightShadows.Soft;
            foreach(var z in data.zones.Where(z=>z.kind!="cabin"&&z.kind!="exterior"&&!z.id.StartsWith("X"))){var g=new GameObject(z.id+" light");g.transform.position=V(z.waypoint)+Vector3.up*2.72f;var l=g.AddComponent<Light>();l.type=LightType.Point;l.range=z.kind=="sector"?13:8;l.intensity=2.6f;l.color=z.id=="ENGINEERING"?new Color(1,.72f,.4f):new Color(.6f,.84f,1);}
            float centerZ=(data.body[2]+data.body[3])*.5f;
            var cameraGO=new GameObject("Main Camera");cameraGO.tag="MainCamera";var camera=cameraGO.AddComponent<Camera>();camera.nearClipPlane=.03f;camera.farClipPlane=300;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.018f,.027f,.045f);camera.orthographic=true;camera.orthographicSize=26+(data.body[3]-data.body[2]-21)*.5f;cameraGO.AddComponent<AudioListener>();cameraGO.AddComponent<UniversalAdditionalCameraData>();cameraGO.transform.position=new Vector3(45,65,centerZ-65);cameraGO.transform.LookAt(new Vector3(21,0,centerZ));
            var playerGO=new GameObject("Explorer Player");playerGO.transform.position=V(data.zones.First(z=>z.id=="BRIDGE").waypoint)+Vector3.up*.02f;playerGO.transform.rotation=Quaternion.Euler(0,90,0);var controller=playerGO.AddComponent<CharacterController>();controller.height=1.8f;controller.radius=.28f;controller.center=new Vector3(0,.9f,0);controller.stepOffset=.18f;controller.enabled=false;
            var controls=new GameObject("Ship Controls").AddComponent<ShipExplorer>();controls.master=master;controls.roofs=master.transform.Find("Ceilings").gameObject;controls.labels=master.transform.Find("Labels").gameObject;controls.player=controller;controls.view=camera;controls.doors=master.GetComponentsInChildren<C01Door>();controls.airlocks=master.GetComponentsInChildren<ShipAirlock>();
            EditorSceneManager.SaveScene(scene,ScenePath);var buildScenes=EditorBuildSettings.scenes.Where(s=>s.path!=ScenePath).ToList();buildScenes.Insert(0,new EditorBuildSettingsScene(ScenePath,true));if(!buildScenes.Any(s=>s.path==C01.Editor.C01Builder.ScenePath))buildScenes.Add(new EditorBuildSettingsScene(C01.Editor.C01Builder.ScenePath,true));EditorBuildSettings.scenes=buildScenes.ToArray();AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            Debug.Log("C01_SHIP_BUILD: "+data.placements.Length+" editable source placements; "+controls.doors.Length+" doors");
        }
        public static void Export(){
            string container=Path.GetFullPath(Path.Combine(Application.dataPath,"../.."));string doc=Root+"/Documentation";Directory.CreateDirectory(doc);
            if(File.Exists(Path.Combine(container,"Tools/build_ship.py")))foreach(string relative in new[]{"README_PL.md","docs/QA_REPORT_PL.md","docs/PLAN_MAPPING_PL.md","QA/layout_qa.json","QA/geometry_qa.json","QA/sweep_qa.json","QA/unity_ship_qa.json","QA/blender_ship_qa.json","QA/verification_summary.json","Reference/ship_plan.png"}){string source=Path.Combine(container,relative);if(File.Exists(source))File.Copy(source,Path.Combine(doc,Path.GetFileName(source)),true);}
            AssetDatabase.Refresh();
            Directory.CreateDirectory(QA);var folders=new List<string>{"Assets/C01Modular",Root};if(AssetDatabase.IsValidFolder("Assets/C01Integration"))folders.Add("Assets/C01Integration");AssetDatabase.ExportPackage(folders.ToArray(),Path.Combine(QA,"C01_Ship_FromPlan_v3.1.unitypackage"),ExportPackageOptions.Recurse);
        }
        public static void Batch(){
            try{Build();ShipValidation.Run();ShipValidation.Capture();Export();File.WriteAllText(Path.Combine(QA,"unity_success.txt"),Application.unityVersion+"\n"+DateTime.UtcNow.ToString("O"));if(Application.isBatchMode)EditorApplication.Exit(0);}
            catch(Exception e){Debug.LogException(e);File.WriteAllText(Path.Combine(QA,"unity_failure.txt"),e.ToString());if(Application.isBatchMode)EditorApplication.Exit(1);throw;}
        }
        public static void ExportOnly(){Export();if(Application.isBatchMode)EditorApplication.Exit(0);}
    }
}
