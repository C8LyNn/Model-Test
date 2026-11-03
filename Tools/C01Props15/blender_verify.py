import bpy,json,math,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
base=root/"Assets/C01InteriorProps/P15"
spec=json.loads((base/"Sources/geometry_spec.json").read_text())
result=[]
def check(name,ok,details):
 result.append({"test":name,"status":"PASS" if ok else "FAIL","details":details})
for aid,meta in spec["assets"].items():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 path=base/"Sources/Blender"/(aid+".blend")
 bpy.ops.wm.open_mainfile(filepath=str(path))
 objs=[o for o in bpy.data.objects if o.type=="MESH"]
 check(aid+"_blend_meshes",len(objs)>0,{"mesh_objects":len(objs)})
 check(aid+"_blend_uv",all(o.data.uv_layers.active is not None for o in objs),{"missing_uv":[o.name for o in objs if o.data.uv_layers.active is None]})
 check(aid+"_blend_normals",all(len(o.data.polygons)>0 and all(p.area>0 for p in o.data.polygons) for o in objs),{"polygon_count":sum(len(o.data.polygons) for o in objs)})
 check(aid+"_blend_scale",all(all(abs(v-1)<1e-6 for v in o.scale) for o in objs),{"non_unit_scales":[o.name for o in objs if any(abs(v-1)>1e-6 for v in o.scale)]})
 # Roundtrip import of actual FBX (not just signature checks).
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(base/"Models/FBX"/(aid+".fbx")))
 meshes=[o for o in bpy.data.objects if o.type=="MESH"]
 check(aid+"_fbx_meshes",len(meshes)>0,{"mesh_count":len(meshes)})
 check(aid+"_fbx_uv",all(o.data.uv_layers.active is not None for o in meshes),{"missing_uv":[o.name for o in meshes if o.data.uv_layers.active is None]})
 check(aid+"_fbx_normals",all(len(o.data.polygons)>0 and all(p.area>1e-12 for p in o.data.polygons) for o in meshes),{"faces":sum(len(o.data.polygons) for o in meshes)})
 check(aid+"_fbx_material",all(len(o.data.materials)>0 for o in meshes),{"missing_material":[o.name for o in meshes if not o.data.materials]})
check("three_source_files",len([r for r in result if r["test"].endswith("_blend_meshes")])==3,{})
out={"scope":"actual Blender source and FBX import, UV polygons and material presence; Unity physics NOT RUN","checks":result,"result":"PASS" if all(x["status"]=="PASS" for x in result) else "FAIL","blender_runtime":bpy.app.version_string,"unity":"NOT RUN","independent_qa":"NOT RUN"}
(base/"QA/blender_mesh_roundtrip.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"result":out["result"],"pass":sum(x["status"]=="PASS" for x in result),"fail":[x for x in result if x["status"]=="FAIL"]}))
if out["result"]!="PASS":sys.exit(1)
