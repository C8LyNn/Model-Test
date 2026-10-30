using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;

namespace C01.Ship.V4.Editor {
    public static class ShipV4Capture {
        public static void Capture(){
            var data=ShipV4Builder.Read();var root=ShipV4Validation.Master();if(root==null)throw new Exception("Capture requires built ship");var explorer=UnityEngine.Object.FindFirstObjectByType<ShipExplorerV4>();var cam=explorer.view;
            var renderers=root.GetComponentsInChildren<Renderer>(true);var visible=renderers.Select(r=>r.enabled).ToArray();var gates=root.GetComponentsInChildren<ShipGateV4>();var openings=gates.Select(g=>g.openness).ToArray();var targets=gates.Select(g=>g.target).ToArray();
            var pos=cam.transform.position;var rot=cam.transform.rotation;var parent=cam.transform.parent;bool ortho=cam.orthographic;float size=cam.orthographicSize,fov=cam.fieldOfView,aspect=cam.aspect,near=cam.nearClipPlane;var textureTarget=cam.targetTexture;var active=RenderTexture.active;int deck=explorer.selectedDeck;bool walking=explorer.walking;
            var physical=renderers.Where(r=>r.GetComponent<ShipSolidV4>()!=null).ToArray();var shipBounds=physical[0].bounds;foreach(var renderer in physical)shipBounds.Encapsulate(renderer.bounds);
            string folder=Path.Combine(ShipV4Builder.QA,"Screenshots");Directory.CreateDirectory(folder);var images=new List<string>();
            void Shot(string name,Vector3 position,Vector3 target,bool plan,float scale){
                cam.transform.SetPositionAndRotation(position,Quaternion.LookRotation(target-position,plan?Vector3.forward:Vector3.up));cam.orthographic=true;cam.orthographicSize=scale;cam.aspect=1.6f;cam.nearClipPlane=plan?Mathf.Max(.05f,position.y-target.y-5.9f):.05f;
                var rt=new RenderTexture(1920,1200,24);var png=new Texture2D(1920,1200,TextureFormat.RGB24,false);try{cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;png.ReadPixels(new Rect(0,0,1920,1200),0,0);png.Apply();var path=Path.Combine(folder,name+".png");File.WriteAllBytes(path,png.EncodeToPNG());images.Add(name+".png | Camera.Render | target="+target+" | ortho="+scale);}finally{cam.targetTexture=textureTarget;RenderTexture.active=active;UnityEngine.Object.DestroyImmediate(png);rt.Release();UnityEngine.Object.DestroyImmediate(rt);}
            }
            void Select(int level){explorer.SetDeck(level);foreach(var r in renderers)if(r.GetComponentInParent<TextMesh>()!=null)r.enabled=false;}
            void Zone(string id,string file){var z=data.zones.Single(v=>v.id==id);Select(z.deck);float sx=z.bounds[1]-z.bounds[0],sz=z.bounds[3]-z.bounds[2];var center=new Vector3((z.bounds[0]+z.bounds[1])*.5f,z.floor,(z.bounds[2]+z.bounds[3])*.5f);Shot(file,center+Vector3.up*60,center,true,Mathf.Max(sz*.5f,sx/3.2f)+1);}
            try{
                explorer.SetWalking(false);foreach(var g in gates)ShipV4Validation.GeometryPose(g,1);
                for(int d=0;d<3;d++){Select(d);foreach(var text in root.GetComponentsInChildren<TextMesh>(true)){var zone=text.GetComponentInParent<ShipZoneV4>();if(zone!=null)text.GetComponent<Renderer>().enabled=zone.deck==d;}var floor=data.decks.Single(v=>v.id==d).y;var center=new Vector3(shipBounds.center.x,floor,shipBounds.center.z);Shot("deck"+d+"_plan",new Vector3(center.x,90,center.z),center,true,Mathf.Max(shipBounds.extents.x/1.6f,shipBounds.extents.z)+2);}
                Select(-1);foreach(var r in renderers){var marker=r.GetComponentInParent<ShipInstanceV4>();if(marker!=null&&((marker.category=="Floors"&&marker.deck>0)||(marker.category=="Walls"&&r.bounds.center.z<3)))r.enabled=false;}Shot("all_deck_cutaway",new Vector3(54,95,-65),new Vector3(25,0,22.5f),false,43);
                foreach(string core in new[]{"BRIDGE","STERN"}){var zones=data.zones.Where(z=>z.id.EndsWith("_"+core,StringComparison.Ordinal)).ToArray();var min=zones.Min(z=>z.bounds[0]);var max=zones.Max(z=>z.bounds[1]);var z0=zones.Min(z=>z.bounds[2]);var z1=zones.Max(z=>z.bounds[3]);var center=new Vector3((min+max)*.5f,-1,(z0+z1)*.5f);Select(-1);foreach(var r in renderers){var b=r.bounds;if(b.max.x<min-.5f||b.min.x>max+.5f||b.max.z<z0-.5f||b.min.z>z1+.5f)r.enabled=false;var marker=r.GetComponentInParent<ShipInstanceV4>();if(marker!=null&&(marker.category=="Walls"||marker.category=="Hull")&&b.center.z< center.z)r.enabled=false;}Shot(core.ToLowerInvariant()+"_vertical_core",center+new Vector3(8,24,-42),center,false,Mathf.Max(24,(z1-z0)*.6f));}
                Zone(data.zones.First(z=>z.kind=="cabin"&&z.deck==1).id,"cabin_4beds_bath");Zone("L1_GYM","gym_no_beds");Zone("L1_MED","med_2beds");Zone("L0_ENGINE_ROOM","engine_lower");Zone("L1_ENGINE_CONTROL","engine_control_upper");Zone("L0_PURIFICATION","purification");Zone("L0_HYDROPONICS","plants");Zone("L0_EVAC_HANGAR","escape_craft_hangar");
                var gateRecord=data.gates.First(g=>string.IsNullOrEmpty(g.lift)&&string.IsNullOrEmpty(g.airlock)&&g.zones.Any(z=>z.StartsWith("L1_C",StringComparison.Ordinal)&&!z.EndsWith("BATH",StringComparison.Ordinal)));var gate=gates.Single(g=>g.id==gateRecord.id);Select(gateRecord.deck);var target=new Vector3(gateRecord.x,gateRecord.y+gateRecord.height*.45f,gateRecord.z)+Quaternion.Euler(0,gateRecord.yaw,0)*Vector3.right*(gateRecord.width*.5f);var normal=Quaternion.Euler(0,gateRecord.yaw,0)*Vector3.forward;
                gate.SetImmediate(0);Shot("gate_closed",target-normal*10+Vector3.up*3,target,false,4.5f);gate.SetImmediate(1);Shot("gate_open",target-normal*10+Vector3.up*3,target,false,4.5f);
                var lift=data.lifts[0];Select(-1);var liftCenter=new Vector3(lift.x,.5f,lift.z);foreach(var r in renderers){var b=r.bounds;if(Mathf.Abs(b.center.x-lift.x)>7||Mathf.Abs(b.center.z-lift.z)>8)r.enabled=false;}Shot("elevator",liftCenter+new Vector3(10,17,-18),liftCenter,false,12);
                File.WriteAllLines(Path.Combine(ShipV4Builder.QA,"unity_renders.txt"),new[]{"Actual Unity "+Application.unityVersion+" Camera.Render evidence; no synthetic images."}.Concat(images));
            }finally{for(int i=0;i<gates.Length;i++){ShipV4Validation.GeometryPose(gates[i],openings[i]);gates[i].target=targets[i];}explorer.SetDeck(deck);explorer.SetWalking(walking);for(int i=0;i<renderers.Length;i++)renderers[i].enabled=visible[i];cam.transform.SetParent(parent,true);cam.transform.SetPositionAndRotation(pos,rot);cam.orthographic=ortho;cam.orthographicSize=size;cam.fieldOfView=fov;cam.aspect=aspect;cam.nearClipPlane=near;cam.targetTexture=textureTarget;RenderTexture.active=active;Physics.SyncTransforms();}
        }
    }
}
