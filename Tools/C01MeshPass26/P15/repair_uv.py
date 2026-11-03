"""C01-15 PASS26: targeted real Blender4 UV0 repair for original P15-03 ONLY.

Open exact signed original .blend + three binary FBXs, fix UV of three preexisting
custom parts; save SAME P15-03 .blend, real full/Body/Door FBX exports; reimport
genuine full FBX; preserve all 34 mesh topologies, material roles, parent pivots,
normal orientations, moving hinge structure, and 31 untouched source UV maps.
No other P15 model or delegated Claude door/gate is opened or written.
"""
import bpy, hashlib, json, os, shutil, sys, tempfile, traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from uv_layout import layout_custom_mesh_uv
BASE=ROOT/"Assets/C01InteriorProps/P15"
SRC=BASE/"Sources/Blender/P15-03.blend"
FBX=BASE/"Models/FBX/P15-03.fbx"
BODY=BASE/"Models/FBX/P15-03_Body.fbx"
DOOR=BASE/"Models/FBX/P15-03_Door.fbx"
SPEC=BASE/"Sources/geometry_spec.json"
OUT=BASE/"QA/Pass26"
PRE=OUT/"Previews"
PRE.mkdir(parents=True,exist_ok=True)
ORIGINAL={
 "P15-03.blend":"1deb3df36a1c87be8fe6ebec7529233b1d9eececa38230f4d9f693bf40fceb9a",
 "P15-03.fbx":"7be76765763308deb8c0fa9d4c11cec8c74b60777e0199a160ebab088c59189d",
 "P15-03_Body.fbx":"e03f774da5977f0aeb8dcb7eadf8e09aaf2cd4f16fa184c7ad92c672ee8cc112",
 "P15-03_Door.fbx":"96f2d542fc0bdb2376642f1ed082ca77c9b03aed28d7bffb0ef6c111a7cca03d",
 "geometry_spec.json":"9394e90c72b78ce8d33e0629e383fe32b9faafb0a1cbf3fcb817281623cf05f3"}
TARGET={"DoorSkin":"notched_box","Hinge_Lower_Sleeve":"hollow_cylinder","Hinge_Upper_Sleeve":"hollow_cylinder"}
R={"asset":"P15-03","owner":"C01-15","wave":26,"blender":bpy.app.version_string,
   "scope":"REAL ORIGINAL NATIVE UV0 REPAIR ON 3 PARTS; NO GEOMETRY/MATERIAL/PIVOT EDIT",
   "old_sha256":{},"new_sha256":{},"checks":[],
   "independent_C01_02":"PENDING","unity6":"NOT_RUN","final":"HOLD","result":"FAIL"}
def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def check(c,name,details=None):
 R["checks"].append({"name":name,"pass":bool(c),"details":details})
 if not c:raise RuntimeError(name+" "+str(details))
def snap(obj):
 m=obj.data
 return {"vertices":[tuple(round(float(c),9) for c in v.co) for v in m.vertices],
         "edges":[tuple(e.vertices) for e in m.edges],
         "polygons":[tuple(p.vertices) for p in m.polygons],
         "smooth":[bool(p.use_smooth) for p in m.polygons],
         "material":[x.name for x in m.materials],
         "parent":obj.parent.name if obj.parent else None,
         "loc":tuple(round(float(c),9) for c in obj.location),
         "rot":tuple(round(float(c),9) for c in obj.rotation_euler),
         "scale":tuple(round(float(c),9) for c in obj.scale)}
def uvcoords(obj):
 return [tuple(round(float(v),9) for v in l.uv) for l in obj.data.uv_layers.active.data]
def uvbad(obj):
 m=obj.data; uv=m.uv_layers.active
 if not uv:return -1
 count=0
 for p in m.polygons:
  lids=list(p.loop_indices)
  for j in range(1,len(lids)-1):
   a,b,c=[uv.data[lids[k]].uv for k in (0,j,j+1)]
   count+= abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5<1e-10
 return count
def stats(ms):
 return {"mesh_objects":len(ms),"vertices":sum(len(o.data.vertices) for o in ms.values()),
         "edges":sum(len(o.data.edges) for o in ms.values()),
         "faces":sum(len(o.data.polygons) for o in ms.values()),
         "triangles":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in ms.values()),
         "uv0_collapsed_triangles":sum(uvbad(o) for o in ms.values())}
def image(center,scale,style,path):
 camdata=bpy.data.cameras.new("C01_PASS26_TEMP_CAMERA")
 cam=bpy.data.objects.new("C01_PASS26_TEMP_CAMERA",camdata)
 bpy.context.scene.collection.objects.link(cam)
 v=Vector((center[0],-center[2],center[1]))
 cam.location=v+Vector((2.2*scale,-2.6*scale,2*scale))
 cam.rotation_euler=(v-cam.location).to_track_quat("-Z","Y").to_euler()
 camdata.type="ORTHO";camdata.ortho_scale=scale*1.6
 sc=bpy.context.scene;sc.camera=cam;sc.render.engine="BLENDER_WORKBENCH"
 sh=sc.display.shading;sh.light="STUDIO";sh.color_type="MATERIAL"
 if hasattr(sh,"show_wireframes"):sh.show_wireframes=(style=="wire")
 if hasattr(sh,"wireframe_threshold"):sh.wireframe_threshold=1
 sc.render.resolution_x=900;sc.render.resolution_y=700;sc.render.resolution_percentage=100
 sc.render.image_settings.file_format="PNG";sc.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(cam,do_unlink=True)
 check(path.is_file() and path.stat().st_size>1000,"genuine_blender_image_"+path.name)
def export(path,objects):
 bpy.ops.object.select_all(action="DESELECT")
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,global_scale=1,
   apply_unit_scale=True,axis_forward="-Z",axis_up="Y",add_leaf_bones=False,
   bake_anim=False,object_types={"EMPTY","MESH"},path_mode="AUTO")
 check(path.is_file() and path.stat().st_size>500 and path.read_bytes().startswith(b"Kaydara FBX Binary"),"binary_FBX_export_"+path.name)
def imported(path):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 result={}
 for ob in bpy.data.objects:
  if ob.type!="MESH":continue
  m=ob.data
  result[ob.name]={"vertices":[tuple(round(float(x),7) for x in v.co) for v in m.vertices],
     "polygons":[tuple(p.vertices) for p in m.polygons],
     "face_areas":[round(float(p.area),8) for p in m.polygons],
     "materials":[v.name for v in m.materials],
     "uvbad":uvbad(ob)}
 return result
def main():
 for p in [SRC,FBX,BODY,DOOR,SPEC]:
  h=digest(p);R["old_sha256"][p.name]=h
  check(h==ORIGINAL[p.name],"strict_signed_original_"+p.name,h)
  if p==SRC:check(p.read_bytes().startswith(b"BLENDER-"),"real_original_blend")
  if p.suffix==".fbx":check(p.read_bytes().startswith(b"Kaydara FBX Binary"),"real_original_fbx_"+p.name)
 with tempfile.TemporaryDirectory(prefix="C01_P15_PASS26_") as td:
  oldfull=Path(td)/"original_P15-03.fbx";shutil.copy2(FBX,oldfull)
  pre=imported(oldfull)
  check(len(pre)==34 and sum(v["uvbad"] for v in pre.values())==120,"original_true_import_UV_collapses_120",
        {"mesh_count":len(pre),"uvbad":sum(v["uvbad"] for v in pre.values())})
  bpy.ops.wm.open_mainfile(filepath=str(SRC))
  objs={o.name:o for o in bpy.data.objects if o.type=="MESH"}
  check(len(objs)==34,"original_true_blender_34_meshes")
  oldstat=stats(objs)
  check(oldstat["triangles"]==672 and oldstat["uv0_collapsed_triangles"]==120,
      "original_blender_672T_and_120_UVbad",oldstat)
  oldgeo={n:snap(o) for n,o in objs.items()}
  olduv={n:uvcoords(o) for n,o in objs.items()}
  spec=json.loads(SPEC.read_text())
  parts={p["name"]:p for p in spec["parts"] if p["asset"]=="P15-03"}
  roots={o.name:o for o in bpy.data.objects if o.type=="EMPTY"}
  check(set(["P15-03_Body_ROOT","P15-03_Door_ROOT"])<=set(roots),"existing_roots")
  dr=roots["P15-03_Door_ROOT"]
  check(tuple(round(float(x),3) for x in dr.matrix_world.translation)==(-.352,-.138,0),"existing_functional_hinge_pivot",tuple(dr.matrix_world.translation))
  for mode in ("wire","shaded"):image((0,.9,0),2.,mode,PRE/("BEFORE_"+mode+".png"))
  for name,shape in TARGET.items():
   check(name in objs and parts[name]["shape"]==shape,"original_part_"+name)
   layout_custom_mesh_uv(objs[name].data,shape,parts[name])
  bpy.context.view_layer.update()
  newstat=stats(objs)
  check(newstat["uv0_collapsed_triangles"]==0,"actual_blender_target_UV_120_to_0",newstat)
  check(all(snap(o)==oldgeo[n] for n,o in objs.items()),"34_MESH_GEOMETRY_NORMAL_MATERIAL_TRANSFORM_UNCHANGED")
  check(all(uvcoords(o)==olduv[n] for n,o in objs.items() if n not in TARGET),"31_NON_TARGET_UV_MAPS_UNCHANGED")
  check(all(uvcoords(objs[n])!=olduv[n] for n in TARGET),"3_TARGET_UV_MAPS_CHANGED")
  check({k:newstat[k] for k in ("vertices","edges","faces","triangles")}==
        {k:oldstat[k] for k in ("vertices","edges","faces","triangles")},"V_E_F_T_IDENTICAL")
  R["source_mesh_stats_before"]=oldstat
  R["source_mesh_stats_after"]=newstat
  R["per_part_uv0_bad_before_after"]={n:[sum(0 for _ in [])+0,uvbad(o)] for n,o in objs.items() if n in TARGET}
  R["per_part_uv0_bad_before_after"]={n:[{"DoorSkin":24,"Hinge_Lower_Sleeve":48,"Hinge_Upper_Sleeve":48}[n],uvbad(objs[n])] for n in TARGET}
  bpy.ops.wm.save_as_mainfile(filepath=str(SRC),compress=False)
  bodyroot=roots["P15-03_Body_ROOT"];doorroot=roots["P15-03_Door_ROOT"]
  bodyparts=sorted([o for o in objs.values() if o.parent==bodyroot],key=lambda x:x.name)
  doorparts=sorted([o for o in objs.values() if o.parent==doorroot],key=lambda x:x.name)
  check(len(bodyparts)+len(doorparts)==34,"component_partition_34")
  export(FBX,[bodyroot]+bodyparts+[doorroot]+doorparts)
  export(BODY,[bodyroot]+bodyparts)
  originaldoor=doorroot.location.copy()
  doorroot.location=(0,0,0);bpy.context.view_layer.update()
  export(DOOR,[doorroot]+doorparts)
  doorroot.location=originaldoor;bpy.context.view_layer.update()
  for mode in ("wire","shaded"):image((0,.9,0),2.,mode,PRE/("AFTER_"+mode+".png"))
  for p in [SRC,FBX,BODY,DOOR]:R["new_sha256"][p.name]=digest(p)
  check(R["new_sha256"]["P15-03.fbx"]!=ORIGINAL["P15-03.fbx"],"truly_new_binary_FBX")
  new=imported(FBX)
  check(len(new)==34 and set(new)==set(pre),"new_real_FBX_import_all_original_mesh_names")
  changes=[]
  for name in pre:
   for field in ("vertices","polygons","face_areas","materials"):
    if pre[name][field]!=new[name][field]:changes.append(name+"/"+field)
  check(not changes,"original_vs_new_IMPORT_geometry_material_parity",changes)
  check(sum(x["uvbad"] for x in new.values())==0,"actual_reimported_new_FBX_zero_collapsed_UV0")
  check(sum(sum(len(p)-2 for p in x["polygons"]) for x in new.values())==672,"actual_reimported_FBX_672_triangles")
  check(BODY.stat().st_size>500 and DOOR.stat().st_size>500,"body_door_split_FBX_physically_created")
  R["real_FBX_before_uvbad"]=sum(x["uvbad"] for x in pre.values())
  R["real_FBX_after_uvbad"]=sum(x["uvbad"] for x in new.values())
  R["previews"]={p.name:{"size":p.stat().st_size,"sha256":digest(p)} for p in sorted(PRE.glob("*.png"))}
  R["result"]="PRODUCER_REAL_BLENDER_AND_FBX_UV_REPAIR_PASS_INDEPENDENT_QA_PENDING"
if __name__=="__main__":
 try:main()
 except Exception as e:
  R["error"]=repr(e)
  R["traceback"]=traceback.format_exc()
  R["result"]="FAIL"
 finally:
  (OUT/"P15-03_PASS26_REAL_UV0_REPAIR.json").write_text(json.dumps(R,indent=2)+"\n")
  print("C01_P15_PASS26_RESULT",json.dumps({k:R.get(k) for k in
      ("result","error","source_mesh_stats_before","source_mesh_stats_after",
       "real_FBX_before_uvbad","real_FBX_after_uvbad","old_sha256","new_sha256")}))
 if R["result"]=="FAIL":sys.exit(1)
