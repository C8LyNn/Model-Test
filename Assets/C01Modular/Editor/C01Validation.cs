using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace C01.Editor {
    public static class C01Validation {
        [Serializable] class Report {
            public string unityVersion, pipeline, status;
            public int placementCount, solidCount, penetrationPairs, doorPoses, doorSolidTests, coverageRays, importModels, socketChecks;
            public List<string> errors=new List<string>();
            public List<string> importedBounds=new List<string>();
        }
        const float Tol=.0001f;
        static GameObject Master() => GameObject.Find("C01_PASS02_ThreeRooms_MASTER");
        static bool Near(Vector3 a,Vector3 b) => Vector3.Distance(a,b)<Tol;
        [MenuItem("Tools/C01 PASS02/Validate current scene")]
        public static void Run() => Run("unity_geometry_qa.json");
        public static void Run(string reportName) {
            var r=new Report{unityVersion=Application.unityVersion,pipeline=UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline?.GetType().FullName};
            void Check(bool ok,string detail){if(!ok)r.errors.Add(detail);}
            Check(UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset,"URP is not active");
            var master=Master();if(master==null)throw new Exception("Master missing");
            var spec=C01Builder.Read();var modules=spec.modules.ToDictionary(m=>m.id);
            foreach(var p in spec.placements){
                var t=master.transform.Find(p.group+"/"+p.tag);Check(t!=null,"Missing placement "+p.tag);if(t==null)continue;
                r.placementCount++;Check(Near(t.position,new Vector3(p.x,p.y,p.z)),"Position "+p.tag);Check(Quaternion.Angle(t.rotation,Quaternion.Euler(0,p.yaw,0))<.001f,"Rotation "+p.tag);Check(Near(t.lossyScale,Vector3.one),"Scale "+p.tag);
                Check(PrefabUtility.IsPartOfPrefabInstance(t),"Unlinked module "+p.tag);
                foreach(var socket in modules[p.id].sockets){
                    var actual=t.Find("Socket_"+socket.name);Check(actual!=null && Near(actual.localPosition,C01Builder.V(socket.position)),"Socket "+p.tag+"/"+socket.name);r.socketChecks++;
                }
            }
            var solids=master.GetComponentsInChildren<C01Solid>(true);r.solidCount=solids.Length;
            foreach(var instance in master.GetComponentsInChildren<C01Module>(true)) {
                var actual=instance.GetComponentsInChildren<C01Solid>(true).Where(s=>s.GetComponentInParent<C01Module>()==instance).ToArray();
                var expected=modules[instance.moduleId].parts;
                Check(actual.Length==expected.Length,"Missing/duplicate solid in "+instance.name);
                Check(actual.Select(s=>s.partIndex).Distinct().Count()==expected.Length,"Missing part index in "+instance.name);
                foreach(var s in actual)Check(Near(s.transform.localPosition,Vector3.zero)&&Quaternion.Angle(s.transform.localRotation,Quaternion.identity)<.001f&&Near(s.transform.localScale,Vector3.one),"Moved solid "+instance.name+"/"+s.name);
                var requiredChildren=modules[instance.moduleId].children??Array.Empty<ChildData>();
                var directChildren=instance.GetComponentsInChildren<C01Module>(true).Where(c=>c!=instance&&c.transform.parent==instance.transform).ToArray();
                Check(directChildren.Length==requiredChildren.Length,"Missing/duplicate nested module in "+instance.name);
                foreach(var child in requiredChildren){
                    var t=instance.transform.Find(child.socket);Check(t!=null,"Missing nested child "+instance.name+"/"+child.socket);if(t==null)continue;
                    var info=t.GetComponent<C01Module>();Check(info!=null&&info.moduleId==child.module,"Nested module identity "+instance.name+"/"+child.socket);
                    Check(Near(t.localPosition,C01Builder.V(child.position))&&Quaternion.Angle(t.localRotation,Quaternion.Euler(0,child.yaw,0))<.001f&&Near(t.localScale,Vector3.one),"Nested socket transform "+instance.name+"/"+child.socket);
                    Check(PrefabUtility.IsPartOfPrefabInstance(t),"Unlinked nested prefab "+instance.name+"/"+child.socket);
                }
            }
            foreach(var s in solids){
                var collider=s.GetComponent<BoxCollider>();var mesh=s.GetComponent<MeshFilter>().sharedMesh;
                Check(collider!=null,"Missing detail collider "+s.name);Check(mesh!=null,"Missing mesh "+s.name);
                if(mesh==null||collider==null)continue;
                var m=s.GetComponentInParent<C01Module>();var part=modules[m.moduleId].parts[s.partIndex];
                Check(Near(mesh.bounds.min,C01Builder.V(part.lo))&&Near(mesh.bounds.max,C01Builder.V(part.hi)),"Mesh envelope "+m.moduleId+"/"+s.name);
                Check(Near(collider.center-collider.size*.5f,mesh.bounds.min)&&Near(collider.center+collider.size*.5f,mesh.bounds.max),"Collider mesh mismatch "+s.name);
                Check(mesh.triangles.Length==36,"Incomplete box triangles "+s.name);
                Check(mesh.normals.Length==24,"Mesh normals missing "+s.name);
            }
            Physics.SyncTransforms();var all=solids.Select(s=>s.GetComponent<BoxCollider>()).ToArray();
            for(int i=0;i<all.Length;i++)for(int j=i+1;j<all.Length;j++){
                var a=all[i];var b=all[j];if(!a.bounds.Intersects(b.bounds))continue;
                if(Physics.ComputePenetration(a,a.transform.position,a.transform.rotation,b,b.transform.position,b.transform.rotation,out var dir,out float depth)&&depth>Tol){r.penetrationPairs++;if(r.errors.Count<100)r.errors.Add("Solid penetration "+a.transform.parent.name+"/"+a.name+" <> "+b.transform.parent.name+"/"+b.name+" depth="+depth);}
            }
            // Physical ray coverage on both surface planes, including every material patch centre.
            foreach(var s in solids){
                var m=s.GetComponentInParent<C01Module>();if(m.family!="floor"&&m.family!="ceiling")continue;
                var bc=s.GetComponent<BoxCollider>();bool floor=m.family=="floor";
                float plane=floor?0:3;if(Mathf.Abs((floor?bc.bounds.max.y:bc.bounds.min.y)-plane)>Tol)continue;
                Vector3 target=new Vector3(bc.bounds.center.x,plane,bc.bounds.center.z);Vector3 origin=target+(floor?Vector3.up:Vector3.down)*.05f;
                var hits=Physics.RaycastAll(origin,floor?Vector3.down:Vector3.up,.1f);Check(hits.Any(h=>Mathf.Abs(h.point.y-plane)<Tol),"Surface ray gap "+m.placementTag+"/"+s.name);r.coverageRays++;
            }
            var doors=master.GetComponentsInChildren<C01Door>(true);Check(doors.Length==3,"Door count");
            var fixedColliders=all.Where(b=>b.GetComponentInParent<Rigidbody>()==null).ToArray();
            foreach(var door in doors){
                Check(door.hinge!=null && Near(door.hinge.localPosition,new Vector3(.66f,.02f,0)),"Hinge socket "+door.name);
                var rb=door.hinge.GetComponent<Rigidbody>();Check(rb!=null&&rb.isKinematic&&!rb.useGravity,"Hinge rigidbody "+door.name);
                var leaf=door.hinge.GetComponentsInChildren<BoxCollider>(true);
                for(int angle=0;angle<=90;angle++){
                    door.SetAngleImmediate(angle);Physics.SyncTransforms();r.doorPoses++;
                    foreach(var moving in leaf)foreach(var fixedBody in fixedColliders){
                        if(!moving.bounds.Intersects(fixedBody.bounds))continue;r.doorSolidTests++;
                        bool hit=Physics.ComputePenetration(moving,moving.transform.position,moving.transform.rotation,fixedBody,fixedBody.transform.position,fixedBody.transform.rotation,out var dir,out var depth);
                        Check(!hit||depth<=Tol,"Door collision "+door.name+" @"+angle+" "+fixedBody.name+" depth="+depth);
                    }
                }
                // At 90 degrees a 0.6m diameter / 1.8m human capsule passes through centre.
                for(int i=0;i<=20;i++){
                    float z=-1+i*.1f;Vector3 bottom=door.transform.TransformPoint(new Vector3(1.5f,.3f,z));Vector3 top=door.transform.TransformPoint(new Vector3(1.5f,1.5f,z));
                    var hits=Physics.OverlapCapsule(bottom,top,.3f-.001f).Where(b=>b.transform.IsChildOf(master.transform)).ToArray();
                    Check(hits.Length==0,"Passage capsule blocked "+door.name+" at z="+z+" by "+string.Join(",",hits.Select(h=>h.name)));
                }
                door.SetAngleImmediate(0);
            }
            Physics.SyncTransforms();
            // Measure ACTUAL imported FBX render bounds against manifest, including complete details.
            foreach(var m in spec.modules){
                string path=C01Builder.Root+"/Models/"+m.id+".fbx";var asset=AssetDatabase.LoadAssetAtPath<GameObject>(path);Check(asset!=null,"FBX import missing "+m.id);if(asset==null)continue;
                var instance=UnityEngine.Object.Instantiate(asset);var renderers=instance.GetComponentsInChildren<Renderer>();
                if(renderers.Length>0){var bounds=renderers[0].bounds;foreach(var ren in renderers.Skip(1))bounds.Encapsulate(ren.bounds);
                    var lo=new Vector3(m.parts.Min(p=>p.lo[0]),m.parts.Min(p=>p.lo[1]),m.parts.Min(p=>p.lo[2]));var hi=new Vector3(m.parts.Max(p=>p.hi[0]),m.parts.Max(p=>p.hi[1]),m.parts.Max(p=>p.hi[2]));
                    r.importedBounds.Add(m.id+": "+bounds.min.ToString("F5")+" .. "+bounds.max.ToString("F5"));
                    Check(Near(bounds.min,lo)&&Near(bounds.max,hi),"FBX scale/axis/pivot mismatch "+m.id+" actual "+bounds+" expected "+lo+".."+hi);
                    Check(renderers.Length==m.parts.Length,"FBX missing/duplicate detail objects "+m.id);
                    for(int i=0;i<m.parts.Length;i++){
                        var matches=renderers.Where(ren=>ren.name.StartsWith(m.id+"__"+i.ToString("D2")+"_",StringComparison.Ordinal)).ToArray();
                        Check(matches.Length==1,"FBX detail identity "+m.id+"/"+i);if(matches.Length!=1)continue;
                        var ren=matches[0];var part=m.parts[i];
                        Check(Near(ren.bounds.min,C01Builder.V(part.lo))&&Near(ren.bounds.max,C01Builder.V(part.hi)),"FBX detail envelope "+m.id+"/"+i);
                        var mesh=ren.GetComponent<MeshFilter>().sharedMesh;Check(mesh.triangles.Length==36,"FBX missing faces "+m.id+"/"+i);
                    }
                }else Check(false,"FBX has no renderer "+m.id);
                UnityEngine.Object.DestroyImmediate(instance);r.importModels++;
            }
            r.status=r.errors.Count==0?"PASS":"FAIL";Directory.CreateDirectory(C01Builder.QA);File.WriteAllText(Path.Combine(C01Builder.QA,reportName),JsonUtility.ToJson(r,true));
            Debug.Log("C01_UNITY_QA "+r.status+": "+r.solidCount+" complete solids, "+r.doorPoses+" door poses, "+r.coverageRays+" surface rays, "+r.importModels+" FBX imports");
            if(r.errors.Count>0)throw new Exception(string.Join("\n",r.errors.Take(30)));
        }
        public static void Capture(){
            string dir=Path.Combine(C01Builder.QA,"Screenshots");Directory.CreateDirectory(dir);var master=Master();var cam=Camera.main;
            var ceilings=master.GetComponentsInChildren<C01Module>(true).Where(m=>m.family=="ceiling").ToArray();var doors=master.GetComponentsInChildren<C01Door>(true);
            void Roof(bool value){foreach(var c in ceilings)c.gameObject.SetActive(value);}
            void Shot(string name,Vector3 position,Vector3 target,bool ortho=false,float size=10){
                cam.transform.SetPositionAndRotation(position,Quaternion.LookRotation(target-position));cam.orthographic=ortho;cam.orthographicSize=size;
                var rt=new RenderTexture(1600,1000,24);cam.targetTexture=rt;cam.Render();var old=RenderTexture.active;RenderTexture.active=rt;
                var tex=new Texture2D(1600,1000,TextureFormat.RGB24,false);tex.ReadPixels(new Rect(0,0,1600,1000),0,0);tex.Apply();File.WriteAllBytes(Path.Combine(dir,name+".png"),tex.EncodeToPNG());
                RenderTexture.active=old;cam.targetTexture=null;UnityEngine.Object.DestroyImmediate(tex);UnityEngine.Object.DestroyImmediate(rt);
            }
            Roof(false);Shot("01_Unity_roof_off",new Vector3(21,19,-16),new Vector3(9,.4f,4));
            foreach(var d in doors)d.SetAngleImmediate(90);Physics.SyncTransforms();Shot("02_Unity_doors_open",new Vector3(21,19,-16),new Vector3(9,.4f,4));
            Shot("03_Unity_top_plan",new Vector3(9,28,3),new Vector3(9,0,3),true,10);
            Roof(true);Shot("04_Unity_roof_on",new Vector3(21,19,-16),new Vector3(9,.4f,4));
            Shot("05_Unity_interior",new Vector3(2.2f,1.7f,2.3f),new Vector3(5.7f,1.5f,4.5f));
            Shot("06_Unity_corner",new Vector3(1.6f,1.3f,1.6f),new Vector3(0,1.2f,0));
            Shot("07_Unity_floor_seam",new Vector3(2.3f,.65f,2.3f),new Vector3(3,0,3));
            Shot("08_Unity_ceiling_seam",new Vector3(2.3f,2.4f,2.3f),new Vector3(3,3,3));
            Shot("09_Unity_portal_open",new Vector3(4.1f,1.55f,4.45f),new Vector3(7.1f,1.35f,4.45f));
            foreach(var d in doors)d.SetAngleImmediate(0);Shot("10_Unity_portal_closed",new Vector3(4.1f,1.55f,4.45f),new Vector3(7.1f,1.35f,4.45f));
            // Restore saved scene transforms / roof visibility after evidence capture.
            cam.orthographic=false;cam.transform.position=new Vector3(9,19,-15);cam.transform.LookAt(new Vector3(9,0,4.5f));Roof(true);
            File.WriteAllText(Path.Combine(C01Builder.QA,"unity_screenshots.txt"),"10 actual Unity Camera.Render outputs, URP active; "+Application.unityVersion);
        }
    }
}
