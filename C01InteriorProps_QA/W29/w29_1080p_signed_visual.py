#!/usr/bin/env python3
"""C01-02 W29: independent original signed FBX 1920x1080 visual evidence only.
No source edits; excludes D01/D02, W04, all Claude-assigned ship doors and gates.
Does NOT claim Unity URP/PhysX or subjective visual PASS.
"""
import bpy,pathlib,hashlib,json,sys,traceback,os
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
PROD=ROOT/"producers"
OUT=ROOT/"C01InteriorProps_QA"/"W29"/"visual_1080p"
OUT.mkdir(parents=True,exist_ok=True)
SPECS={
 "P15-03":("p15","Assets/C01InteriorProps/P15/Sources/Blender/P15-03.blend","Assets/C01InteriorProps/P15/Models/FBX/P15-03.fbx","e787a9455baa08d5e6b198b4c47d236376b240e08781792020b93be899ca38de","ea25d2d7b47baa50fdca3000b101c65b19ba252994553ee6fe6691ca89d5c149",34,672,"hinge"),
 "P18-03":("p18","Assets/C01InteriorProps/C01-18/Sources/P18-03.blend","Assets/C01InteriorProps/C01-18/Models/P18-03.fbx","1c8086b048ac1c62a6791bea5df22a22168b5aea4bc17008a2ce233d86ede41e","f932c5fb36624ef91c039b1de04367fff4e99da7c400bbcb4cadd4138f83618f",63,1780,"hub"),
 "P19-03":("p19","Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.blend","Assets/C01InteriorProps/C01-19/Models/P19-03/P19-03.fbx","ce43931f9116fe3aef6f795c98e505665c921e6c1080c7d61c5cd518e7f7f5b8","4a1ad590e79515b0a699f0fb643d9999b4d1726bd68fce97505f401bb8375967",5,128,"leg")
}
def verified(path,sha,magic):
    b=path.read_bytes()
    if not b.startswith(magic) or hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError("Current source asset NOT exact pinned full bytes: "+str(path))
    return {"path":str(path.relative_to(ROOT)),"sha256":sha,"bytes":len(b)}
def objects():return [o for o in bpy.context.scene.objects if o.type=="MESH"]
def bounds(meshes):
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    if not pts:raise RuntimeError("No actual original FBX mesh vertices")
    lo=Vector([min(p[i] for p in pts) for i in range(3)])
    hi=Vector([max(p[i] for p in pts) for i in range(3)])
    return lo,hi
def camera(scene,meshes,scale=1.8,orientation=(1.35,-1.8,1.10)):
    lo,hi=bounds(meshes);m=(lo+hi)*.5;dim=max((hi-lo))
    camdata=bpy.data.cameras.new("W29_TEMP_QA_CAMERA")
    cam=bpy.data.objects.new("W29_TEMP_QA_CAMERA",camdata);scene.collection.objects.link(cam)
    camdata.type="ORTHO";camdata.ortho_scale=max(.10,dim*scale)
    cam.location=m+Vector(orientation)*max(dim,.15)
    cam.rotation_euler=(m-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.view_layer.update()
    local=cam.matrix_world.inverted()
    projected=[local@(o.matrix_world@v.co) for o in meshes for v in o.data.vertices]
    span_x=max(v.x for v in projected)-min(v.x for v in projected)
    span_y=max(v.y for v in projected)-min(v.y for v in projected)
    aspect=scene.render.resolution_x/scene.render.resolution_y
    camdata.ortho_scale=max(.10,span_x,span_y*aspect)*1.25
    scene.camera=cam;return cam
def original_edges(scene,meshes,scale):
    cr=bpy.data.curves.new("W29_TEMP_ORIGINAL_FBX_TRUE_INDEXED_EDGES","CURVE")
    cr.dimensions="3D";cr.resolution_u=1;cr.bevel_depth=max(.00025,scale*.00025);cr.bevel_resolution=0
    count=0
    for ob in meshes:
        for e in ob.data.edges:
            p=ob.matrix_world@ob.data.vertices[e.vertices[0]].co
            q=ob.matrix_world@ob.data.vertices[e.vertices[1]].co
            if (p-q).length<1e-12:continue
            s=cr.splines.new("POLY");s.points.add(1);s.points[0].co=(*p,1);s.points[1].co=(*q,1);count+=1
    black=bpy.data.materials.new("W29_TEMP_QA_BLACK_EDGE")
    black.diffuse_color=(.006,.006,.006,1)
    cr.materials.append(black)
    wire=bpy.data.objects.new("W29_TEMP_WIREFRAME_NOT_ASSET",cr);scene.collection.objects.link(wire)
    return wire,count
def take(scene,id,suffix):
    path=OUT/f"{id}_{suffix}_1920x1080.png"
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    b=path.read_bytes()
    if len(b)<10000 or not b.startswith(b"\x89PNG\r\n\x1a\n"):raise RuntimeError("No real rendered 1080p "+str(path))
    return {"file":path.name,"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"dimensions":[1920,1080]}
def main():
    if bpy.app.version[0]!=4:raise RuntimeError("Blender4 only")
    res=[]
    target=os.environ.get('C01_W29_TARGET','all')
    if target!='all' and target not in SPECS:raise RuntimeError('Unknown target '+target)
    for id, spec in SPECS.items():
      if target!='all' and id!=target:continue
      lane,blend_path,fbx_path,blendsha,fbxsha,count,tricount,macro=spec
      row={"asset":id,"status":"INCOMPLETE","unity":"NOT_RUN","visual_signoff":"NOT_RUN__HUMAN_AND_URP_STILL_REQUIRED"}
      try:
        blender_file=PROD/lane/blend_path; fbx_file=PROD/lane/fbx_path
        row["source_blend"]=verified(blender_file,blendsha,b"BLENDER")
        row["original_fbx"]=verified(fbx_file,fbxsha,b"Kaydara FBX Binary")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(fbx_file))
        meshes=objects()
        nt=sum(len(o.data.loop_triangles) if o.data.loop_triangles else sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
        row["mesh_count"]=len(meshes);row["triangle_count"]=nt
        if len(meshes)!=count or nt!=tricount:raise RuntimeError("Imported FBX geometry count changed!")
        scene=bpy.context.scene
        scene.render.engine="BLENDER_WORKBENCH"
        scene.display.shading.color_type="MATERIAL";scene.display.shading.light="STUDIO"
        scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
        scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format="PNG"
        lo,hi=bounds(meshes)
        camera(scene,meshes)
        row["screenshots"]={"whole_shaded":take(scene,id,"WHOLE_SHADED")}
        wire,edgecount=original_edges(scene,meshes,max(hi-lo))
        row["original_edge_segments"]=edgecount
        row["screenshots"]["whole_wire"]=take(scene,id,"WHOLE_ORIGINAL_FBX_WIRE")
        wire.hide_render=True
        selections=[o for o in meshes if macro.lower() in o.name.lower()]
        row["macro_target_count"]=len(selections)
        if selections:
          oldcam=scene.camera
          macrocam=camera(scene,selections,2.7)
          row["screenshots"]["macro_shaded"]=take(scene,id,"MACRO_"+macro.upper()+"_SHADED")
          scene.camera=oldcam
          if macrocam:pass
        row["actual_fbx_material_names"]=sorted({m.name for o in meshes for m in o.data.materials if m})
        row["status"]="ACTUAL_FBX_SHA_VERIFIED_NATIVE_1080P_SHADED_AND_INDEXED_WIRE_CAPTURED__NO_VISUAL_URP_ACCEPTANCE"
        if row["screenshots"]["whole_wire"]["sha256"]==row["screenshots"]["whole_shaded"]["sha256"]:raise RuntimeError("Wire image identical to shaded")
      except Exception as exc:
        row["status"]="FAILED_OR_INCOMPLETE";row["error"]=repr(exc);row["traceback"]=traceback.format_exc(limit=2)
      (OUT/f"{id}_W29_REAL_1080P_VISUAL_RECEIPT.json").write_text(json.dumps(row,indent=2)+"\n")
      print("W29_C01_02_VISUAL",id,row["status"],row.get("error",""),flush=True)
      res.append({"id":id,"status":row["status"],"fbx_sha256":fbxsha})
    (OUT/"W29_VISUAL_RECEIPTS_SUMMARY.json").write_text(json.dumps({"models":res,"asset_modifications":0,"unity":"NOT_RUN","release":"HOLD","scope":"C01-02 only; all external Claude doors/gates absent"},indent=2)+"\n")
    if any(x["status"]=="FAILED_OR_INCOMPLETE" for x in res):sys.exit(1)
main()
