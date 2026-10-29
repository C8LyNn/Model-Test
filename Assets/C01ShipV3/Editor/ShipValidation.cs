using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEditor;

namespace C01.Ship.Editor {
    public static class ShipValidation {
        [Serializable] public class Route {public string zone,status;public float length,sampleDistance;public Vector3[] corners;}
        [Serializable] public class FailureGroup {public string key;public int count;}
        [Serializable] public class Report {
            public string status,unityVersion;
            public int placements,colliders,doors,doorPoses,doorCandidates,penetrations,coverageRays,meshParts,importedModels,reachableZones,errorCount;
            public List<string> errors=new List<string>();public List<Route> routes=new List<Route>();
            public List<FailureGroup> failureGroups=new List<FailureGroup>();
        }
        public static GameObject Master()=>GameObject.Find(ShipBuilder.MasterName);
        static string Owner(Collider c)=>c.GetComponentInParent<ShipInstance>()?.placementId+"/"+c.name;
        public static void SetDoors(GameObject root,float angle){foreach(var d in root.GetComponentsInChildren<C01Door>(true))d.SetAngleImmediate(angle);Physics.SyncTransforms();}
        static bool Near(Vector3 a,Vector3 b)=>Vector3.Distance(a,b)<.0002f;
        [MenuItem("Tools/C01 Ship/Validate scene")]
        public static void Run()=>Run("unity_ship_qa.json");
        public static void Run(string reportFile){
            var data=ShipBuilder.Read();var root=Master();if(root==null)throw new Exception("Ship master missing");var r=new Report{unityVersion=Application.unityVersion};
            var failureGroups=new Dictionary<string,int>();
            void Check(bool ok,string message){if(!ok){r.errorCount++;if(r.errors.Count<5000)r.errors.Add(message);string key=message.Split(new[]{" @"},StringSplitOptions.None)[0].Split(new[]{" depth="},StringSplitOptions.None)[0];failureGroups[key]=failureGroups.TryGetValue(key,out int n)?n+1:1;}}
            var roof=root.transform.Find("Ceilings").gameObject;bool oldRoof=roof.activeSelf;roof.SetActive(true);SetDoors(root,0);
            try{
                var instances=root.GetComponentsInChildren<ShipInstance>(true);r.placements=instances.Length;Check(instances.Length==data.placements.Length,"Placement count");
                var byId=instances.GroupBy(i=>i.placementId).ToDictionary(g=>g.Key,g=>g.ToArray());var custom=data.modules.ToDictionary(m=>m.id);var baseData=C01.Editor.C01Builder.Read().modules.ToDictionary(m=>m.id);
                int CountBase(string id)=>baseData[id].parts.Length+(baseData[id].children??Array.Empty<C01.ChildData>()).Sum(c=>CountBase(c.module));
                foreach(var p in data.placements){
                    Check(byId.ContainsKey(p.id)&&byId[p.id].Length==1,"Missing/duplicate placement "+p.id);if(!byId.ContainsKey(p.id)||byId[p.id].Length!=1)continue;
                    var inst=byId[p.id][0];Check(Near(inst.transform.position,new Vector3(p.x,p.y,p.z))&&Quaternion.Angle(inst.transform.rotation,Quaternion.Euler(0,p.yaw,0))<.001f&&Near(inst.transform.lossyScale,Vector3.one),"Placement transform "+p.id);Check(PrefabUtility.IsPartOfPrefabInstance(inst),"Unlinked prefab "+p.id);
                    int actual=inst.GetComponentsInChildren<MeshFilter>(true).Length;int expected=custom.ContainsKey(p.module)?custom[p.module].parts.Length:CountBase(p.module);Check(actual==expected,"Missing model detail "+p.id+" "+actual+"/"+expected);
                    if(p.module=="W04_DoorWall_3m"){
                        var frame=inst.transform.Find("Frame");var hinge=inst.transform.Find("Hinge");Check(frame!=null&&Near(frame.localPosition,Vector3.zero),"Frame socket "+p.id);Check(hinge!=null&&Near(hinge.localPosition,new Vector3(.66f,.02f,0)),"Hinge socket "+p.id);
                    }
                }
                foreach(var s in root.GetComponentsInChildren<ShipSolid>(true)){
                    var expected=custom[s.moduleId].parts[s.partIndex];var mesh=s.GetComponent<MeshFilter>().sharedMesh;int n=expected.outline.Length/2;r.meshParts++;
                    var lo=new Vector3(expected.outline.Where((v,i)=>i%2==0).Min(),expected.y0,expected.outline.Where((v,i)=>i%2==1).Min());var hi=new Vector3(expected.outline.Where((v,i)=>i%2==0).Max(),expected.y1,expected.outline.Where((v,i)=>i%2==1).Max());
                    Check(Near(mesh.bounds.min,lo)&&Near(mesh.bounds.max,hi)&&mesh.triangles.Length==(4*n-4)*3,"Custom mesh completeness "+s.moduleId+"/"+s.partIndex);Check(s.GetComponent<Collider>()!=null,"Missing custom collider "+s.name);
                }
                foreach(var s in root.GetComponentsInChildren<C01Solid>(true)){
                    r.meshParts++;var m=s.GetComponentInParent<C01Module>();var p=baseData[m.moduleId].parts[s.partIndex];var mesh=s.GetComponent<MeshFilter>().sharedMesh;var bc=s.GetComponent<BoxCollider>();
                    Check(mesh!=null&&Near(mesh.bounds.min,ShipBuilder.V(p.lo))&&Near(mesh.bounds.max,ShipBuilder.V(p.hi))&&mesh.triangles.Length==36,"Reused mesh changed "+m.moduleId+"/"+s.name);
                    Check(bc!=null&&Near(bc.center-bc.size*.5f,mesh.bounds.min)&&Near(bc.center+bc.size*.5f,mesh.bounds.max),"Collider/mesh mismatch "+s.name);
                }
                var all=root.GetComponentsInChildren<Collider>(true);r.colliders=all.Length;Physics.SyncTransforms();var boxes=all.Select(c=>c.bounds).ToArray();var seen=new HashSet<ulong>();
                var buckets=new Dictionary<Vector2Int,List<int>>();
                for(int i=0;i<all.Length;i++){
                    var b=boxes[i];for(int x=Mathf.FloorToInt(b.min.x/3);x<=Mathf.FloorToInt(b.max.x/3);x++)for(int z=Mathf.FloorToInt(b.min.z/3);z<=Mathf.FloorToInt(b.max.z/3);z++){
                        var key=new Vector2Int(x,z);if(!buckets.TryGetValue(key,out var list)){list=new List<int>();buckets[key]=list;}list.Add(i);
                    }
                }
                foreach(var list in buckets.Values)for(int a=0;a<list.Count;a++)for(int b=a+1;b<list.Count;b++){
                    int i=list[a],j=list[b];if(i>j){int swap=i;i=j;j=swap;}ulong key=((ulong)(uint)i<<32)|(uint)j;if(!seen.Add(key)||!boxes[i].Intersects(boxes[j]))continue;
                    if(Physics.ComputePenetration(all[i],all[i].transform.position,all[i].transform.rotation,all[j],all[j].transform.position,all[j].transform.rotation,out var direction,out float depth)&&depth>.0005f){r.penetrations++;Check(false,"Static penetration "+Owner(all[i])+" <> "+Owner(all[j])+" depth="+depth);}
                }
                foreach(var p in data.placements.Where(p=>p.category=="Floors"||p.category=="Ceilings")){
                    if(!byId.TryGetValue(p.id,out var surfaces)||surfaces.Length!=1)continue;
                    var inst=surfaces[0];bool floor=p.category=="Floors";var localColliders=inst.GetComponentsInChildren<Collider>(true);
                    foreach(var c in localColliders){
                        var b=c.bounds;float plane=floor?0:3;if(Mathf.Abs((floor?b.max.y:b.min.y)-plane)>.001f)continue;
                        // A custom clipped polygon uses its vertex centroid, not the possibly empty AABB centre.
                        Vector3 target=b.center;if(c is MeshCollider mc){var vs=mc.sharedMesh.vertices;target=mc.transform.TransformPoint(vs.Aggregate(Vector3.zero,(s,v)=>s+v)/vs.Length);}target.y=plane;
                        var hits=Physics.RaycastAll(target+(floor?Vector3.up:Vector3.down)*.04f,floor?Vector3.down:Vector3.up,.08f);Check(hits.Any(h=>h.collider==c&&Mathf.Abs(h.point.y-plane)<.001f),"Surface ray gap "+p.id+"/"+c.name);r.coverageRays++;
                    }
                }
                var doors=root.GetComponentsInChildren<C01Door>(true);r.doors=doors.Length;Check(doors.Length==36,"Door count");
                var fixedBodies=all.Where(c=>c.GetComponentInParent<Rigidbody>()==null).ToArray();
                foreach(var d in doors){
                    var hinge=d.hinge.position;var broad=new Bounds(hinge,new Vector3(4.2f,6,4.2f));var nearby=fixedBodies.Where(c=>c.bounds.Intersects(broad)).ToArray();var leaf=d.hinge.GetComponentsInChildren<Collider>();
                    for(int angle=0;angle<=90;angle++){
                        d.SetAngleImmediate(angle);Physics.SyncTransforms();r.doorPoses++;
                        foreach(var moving in leaf){var mb=moving.bounds;foreach(var other in nearby){if(!mb.Intersects(other.bounds))continue;r.doorCandidates++;
                            bool hit=Physics.ComputePenetration(moving,moving.transform.position,moving.transform.rotation,other,other.transform.position,other.transform.rotation,out var direction,out float depth);Check(!hit||depth<=.0005f,"Door sweep "+d.name+" @"+angle+" <> "+Owner(other)+" depth="+depth);
                        }}
                    }
                    for(int step=0;step<=16;step++){
                        float offset=-.8f+.1f*step;var a=d.transform.TransformPoint(new Vector3(1.5f,.3f,offset));var b=d.transform.TransformPoint(new Vector3(1.5f,1.5f,offset));
                        var hits=Physics.OverlapCapsule(a,b,.299f).Where(c=>c.transform.IsChildOf(root.transform)).ToArray();Check(hits.Length==0,"Human passage obstructed "+d.name+" @"+offset+" "+string.Join(",",hits.Select(Owner)));
                    }
                    d.SetAngleImmediate(0);
                }
                SetDoors(root,90);ValidateNavigation(root,data,r,Check,reportFile=="unity_ship_qa.json"&&r.errorCount==0);SetDoors(root,0);
                foreach(var m in data.modules){
                    string path=ShipBuilder.Root+"/Models/"+m.id+".fbx";var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);Check(asset!=null,"Missing FBX "+m.id);if(asset==null)continue;
                    var instance=UnityEngine.Object.Instantiate(asset);try{
                        var renderers=instance.GetComponentsInChildren<Renderer>();Check(renderers.Length==m.parts.Length,"FBX detail count "+m.id);
                        for(int i=0;i<m.parts.Length;i++){
                            var found=renderers.Where(ren=>ren.name.StartsWith(m.id+"__"+i.ToString("D2")+"_",StringComparison.Ordinal)).ToArray();Check(found.Length==1,"FBX detail identity "+m.id+"/"+i);if(found.Length!=1)continue;
                            var p=m.parts[i];var lo=new Vector3(p.outline.Where((v,k)=>k%2==0).Min(),p.y0,p.outline.Where((v,k)=>k%2==1).Min());var hi=new Vector3(p.outline.Where((v,k)=>k%2==0).Max(),p.y1,p.outline.Where((v,k)=>k%2==1).Max());Check(Near(found[0].bounds.min,lo)&&Near(found[0].bounds.max,hi),"FBX handedness/scale "+m.id+"/"+i);
                        }r.importedModels++;
                    }finally{UnityEngine.Object.DestroyImmediate(instance);}
                }
            }finally{roof.SetActive(oldRoof);SetDoors(root,0);}
            r.failureGroups=failureGroups.Select(kv=>new FailureGroup{key=kv.Key,count=kv.Value}).ToList();r.status=r.errorCount==0?"PASS":"FAIL";File.WriteAllText(Path.Combine(ShipBuilder.QA,reportFile),JsonUtility.ToJson(r,true));Debug.Log("C01_SHIP_QA "+r.status+": "+r.colliders+" solids, "+r.doorPoses+" door poses, "+r.reachableZones+" reachable zones, "+r.importedModels+" new FBX models");
            if(r.errorCount>0)throw new Exception(string.Join("\n",r.errors));
        }
        static void ValidateNavigation(GameObject root,ShipData data,Report r,Action<bool,string> check,bool persist){
            var sources=new List<NavMeshBuildSource>();
            foreach(var c in root.GetComponentsInChildren<Collider>()){
                var s=new NavMeshBuildSource();s.area=0;
                if(c is BoxCollider b){s.shape=NavMeshBuildSourceShape.Box;s.size=b.size;s.transform=b.transform.localToWorldMatrix*Matrix4x4.Translate(b.center);}
                else if(c is MeshCollider m){s.shape=NavMeshBuildSourceShape.Mesh;s.sourceObject=m.sharedMesh;s.transform=m.transform.localToWorldMatrix;}else continue;
                sources.Add(s);
            }
            var settings=NavMesh.GetSettingsByIndex(0);settings.agentRadius=.28f;settings.agentHeight=1.8f;settings.agentClimb=.18f;settings.agentSlope=45;settings.overrideVoxelSize=true;settings.voxelSize=.07f;settings.overrideTileSize=true;settings.tileSize=128;
            float centerZ=(data.body[2]+data.body[3])*.5f;
            var nav=NavMeshBuilder.BuildNavMeshData(settings,sources,new Bounds(new Vector3(21,1.5f,centerZ),new Vector3(80,10,data.body[3]-data.body[2]+15)),Vector3.zero,Quaternion.identity);check(nav!=null,"NavMesh build failed");if(nav==null)return;
            if(persist){string path=ShipBuilder.Root+"/Data/Ship_OpenDoors_NavMesh.asset";var old=AssetDatabase.LoadAssetAtPath<NavMeshData>(path);if(old!=null){EditorUtility.CopySerialized(nav,old);UnityEngine.Object.DestroyImmediate(nav);nav=old;}else AssetDatabase.CreateAsset(nav,path);}
            var handle=NavMesh.AddNavMeshData(nav);
            try{
                bool start=NavMesh.SamplePosition(ShipBuilder.V(data.zones.First(z=>z.id=="BRIDGE").waypoint)+Vector3.up*.1f,out var from,.6f,NavMesh.AllAreas);check(start,"Bridge NavMesh start not found");
                foreach(var z in data.zones){
                    var target=ShipBuilder.V(z.waypoint)+Vector3.up*.1f;bool sampled=NavMesh.SamplePosition(target,out var to,.6f,NavMesh.AllAreas);var route=new NavMeshPath();bool ok=start&&sampled&&NavMesh.CalculatePath(from.position,to.position,NavMesh.AllAreas,route)&&route.status==NavMeshPathStatus.PathComplete;
                    check(ok,"Unreachable zone "+z.id);if(ok)r.reachableZones++;float length=0;for(int i=1;i<route.corners.Length;i++)length+=Vector3.Distance(route.corners[i-1],route.corners[i]);r.routes.Add(new Route{zone=z.id,status=ok?"PASS":"FAIL",length=length,sampleDistance=sampled?Vector3.Distance(target,to.position):-1,corners=route.corners});
                }
            }finally{handle.Remove();if(!persist)UnityEngine.Object.DestroyImmediate(nav);}
            if(persist)AssetDatabase.SaveAssets();
        }
        public static void Capture(){
            var data=ShipBuilder.Read();float height=data.body[3]-data.body[2],centerZ=(data.body[2]+data.body[3])*.5f;var zones=data.zones.ToDictionary(z=>z.id);
            float north=zones["KOSZARY"].bounds[2],mainNorth=zones["MAIN_W"].bounds[3],cabinNorth=zones["C01"].bounds[2],size=26+(height-21)*.5f;
            string folder=Path.Combine(ShipBuilder.QA,"Screenshots");Directory.CreateDirectory(folder);var root=Master();var roofs=root.transform.Find("Ceilings").gameObject;var labels=root.transform.Find("Labels").gameObject;var cam=Camera.main;
            var originalPosition=cam.transform.position;var originalRotation=cam.transform.rotation;
            bool oldRoof=roofs.activeSelf,oldLabels=labels.activeSelf,oldOrtho=cam.orthographic;float oldSize=cam.orthographicSize,oldFov=cam.fieldOfView;
            void Shot(string file,Vector3 pos,Vector3 target,bool ortho,float size=26,bool plan=false){
                cam.transform.position=pos;cam.transform.rotation=Quaternion.LookRotation(target-pos,plan?Vector3.forward:Vector3.up);cam.orthographic=ortho;cam.orthographicSize=size;cam.fieldOfView=65;
                var rt=new RenderTexture(2200,1250,24);cam.targetTexture=rt;cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;var texture=new Texture2D(2200,1250,TextureFormat.RGB24,false);texture.ReadPixels(new Rect(0,0,2200,1250),0,0);texture.Apply();File.WriteAllBytes(Path.Combine(folder,file+".png"),texture.EncodeToPNG());RenderTexture.active=old;cam.targetTexture=null;UnityEngine.Object.DestroyImmediate(texture);UnityEngine.Object.DestroyImmediate(rt);
            }
            roofs.SetActive(false);labels.SetActive(true);SetDoors(root,90);
            Shot("01_Ship_Plan",new Vector3(21.5f,70,centerZ),new Vector3(21.5f,0,centerZ),true,Mathf.Max(22,(height+10)*.5f),true);
            Shot("02_Ship_Cutaway",new Vector3(42,65,centerZ-65),new Vector3(20,0,centerZ),true,size+1);
            labels.SetActive(false);Shot("03_Ship_Cutaway_Clear",new Vector3(42,65,centerZ-65),new Vector3(20,0,centerZ),true,size+1);
            roofs.SetActive(true);SetDoors(root,0);Shot("04_Ship_Exterior",new Vector3(42,55,centerZ-65),new Vector3(20,.5f,centerZ),true,size+1);
            SetDoors(root,90);Shot("05_Bridge",new Vector3(-1.5f,1.65f,centerZ),new Vector3(-9,1.5f,centerZ),false);
            Shot("06_Main_Corridor",new Vector3(3,1.65f,centerZ),new Vector3(40,1.65f,centerZ),false);
            Shot("07_Cabin",new Vector3(5.3f,1.65f,cabinNorth+.8f),new Vector3(.5f,1.2f,cabinNorth+2),false);
            Shot("08_Laboratory",new Vector3(22.5f,1.65f,north+1.6f),new Vector3(17,1.3f,north+3.5f),false);
            Shot("09_Medical",new Vector3(37.5f,1.65f,north+1.2f),new Vector3(42,1.2f,north+5),false);
            Shot("10_Engineering",new Vector3(22.5f,1.65f,4.8f),new Vector3(18.5f,1.3f,2),false);
            Shot("11_Stern_Airlock",new Vector3(46.5f,1.65f,centerZ+2.5f),new Vector3(46.5f,1.65f,height+1),false);
            Shot("13_Extended_Side_Corridor",new Vector3(7.5f,1.65f,mainNorth+.2f),new Vector3(7.5f,1.65f,north+.5f),false);
            roofs.SetActive(false);Shot("12_Five_Engines",new Vector3(67,32,centerZ-25),new Vector3(51,1.1f,centerZ),true,23);
            SetDoors(root,0);roofs.SetActive(oldRoof);labels.SetActive(oldLabels);cam.orthographic=oldOrtho;cam.orthographicSize=oldSize;cam.fieldOfView=oldFov;cam.transform.SetPositionAndRotation(originalPosition,originalRotation);
            File.WriteAllText(Path.Combine(ShipBuilder.QA,"unity_renders.txt"),"13 actual Unity URP Camera.Render outputs; "+Application.unityVersion);
        }
    }
}
