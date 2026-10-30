"""C01-14 experimental RMP-01 and RAI-01 Blender binary exporter. Does not edit ship."""
import bpy, os, json, hashlib, sys, argparse
from pathlib import Path
SPECS={
 "RMP-01":{"size":[4,1.2,1],"purpose":"25% grade ramp, 4m run/1m rise"},
 "RAI-01":{"size":[2,1.1,.1],"purpose":"2m level-only guardrail"}
}
MATS={"Steel":(.46,.53,.58,1),"Dark":(.11,.15,.19,1),"Caution":(.92,.59,.09,1),"Collider":(.10,.10,.10,1)}
def prism(a,b,lo_a,lo_b,z0,z1,hi_a,hi_b):
 v=[(a,lo_a,z0),(b,lo_b,z0),(b,lo_b,z1),(a,lo_a,z1),
    (a,hi_a,z0),(b,hi_b,z0),(b,hi_b,z1),(a,hi_a,z1)]
 f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
    (3,7,6),(3,6,2),(0,4,7),(0,7,3),(1,2,6),(1,6,5)]
 return v,[tuple(reversed(x)) for x in f]
def box(mn,mx):
 x0,y0,z0=mn; x1,y1,z1=mx
 return prism(x0,x1,y0,y0,z0,z1,y1,y1)
def parts(asset):
 if asset=="RMP-01":
  data=[("Deck_Main","Steel",*prism(0,4,-.2,.8,0,1,0,1)),
        ("COL_RampDeck","Collider",*prism(0,4,-.2,.8,0,1,0,1))]
  for i,x in enumerate((.42,1.48,2.54,3.60),1):
   data.append(("AntiSlipMark_%02d"%i,"Caution",*prism(x,x+.07,x/4+.0006,(x+.07)/4+.0006,.08,.92,x/4+.003,(x+.07)/4+.003)))
  return data
 return [("TopRail","Steel",*box((0,1.02,-.05),(2,1.1,.05))),
         ("MiddleRail","Dark",*box((0,.45,-.035),(2,.51,.035))),
         ("Post_Start","Steel",*box((.06,0,-.04),(.14,1.05,.04))),
         ("Post_End","Steel",*box((1.86,0,-.04),(1.94,1.05,.04)))]
def build(root):
 root=Path(root).resolve()
 for asset in SPECS:
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.context.scene.unit_settings.system="METRIC"
  bpy.context.scene.unit_settings.scale_length=1.0
  mats={}
  for name,color in MATS.items():
   mat=bpy.data.materials.new("M_C01_"+name.upper());mat.diffuse_color=color;mat.use_nodes=True
   bsdf=mat.node_tree.nodes.get("Principled BSDF")
   if bsdf:bsdf.inputs["Base Color"].default_value=color
   mats[name]=mat
  selected=[]
  for name,kind,verts,faces in parts(asset):
   mesh=bpy.data.meshes.new(name+"_Mesh")
   # Unity [X,Y,Z] to Blender [X,-Z,Y], per C01 axis proposal.
   mesh.from_pydata([(x,-z,y) for x,y,z in verts],[],faces)
   mesh.update(calc_edges=True)
   uv=mesh.uv_layers.new(name="UVMap")
   for polygon in mesh.polygons:
    axis=max(range(3),key=lambda i:abs(polygon.normal[i]))
    dims=[i for i in range(3) if i!=axis]
    for idx in polygon.loop_indices:
     co=mesh.vertices[mesh.loops[idx].vertex_index].co
     uv.data[idx].uv=(co[dims[0]],co[dims[1]])
   obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
   obj.data.materials.append(mats[kind]);obj["asset_id"]=asset
   obj["is_collider_reference"]=name.startswith("COL_")
   if name.startswith("COL_"): obj.hide_render=True
   selected.append(obj)
  (root/"Blender").mkdir(parents=True,exist_ok=True)
  (root/"FBX").mkdir(parents=True,exist_ok=True)
  src=root/"Blender"/("C01_14_"+asset+"_v001.blend")
  out=root/"FBX"/("C01_14_"+asset+"_v001.fbx")
  bpy.ops.wm.save_as_mainfile(filepath=str(src))
  bpy.ops.object.select_all(action="DESELECT")
  for ob in selected: ob.select_set(True)
  bpy.context.view_layer.objects.active=selected[0]
  bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,
    object_types={"MESH"},axis_forward="-Z",axis_up="Y",
    global_scale=1,apply_unit_scale=True,bake_anim=False,mesh_smooth_type="FACE")
  if not src.read_bytes().startswith(b"BLENDER"): raise RuntimeError("invalid .blend signature")
  if not out.read_bytes().startswith(b"Kaydara FBX Binary"): raise RuntimeError("invalid FBX signature")
  print("PASS native export:",asset,src.stat().st_size,out.stat().st_size)
 rows=[]
 for file in sorted(list((root/"Blender").glob("*.blend"))+list((root/"FBX").glob("*.fbx"))):
  rows.append({"path":str(file.relative_to(root)),"size":file.stat().st_size,
               "sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
 (root/"QA").mkdir(exist_ok=True)
 (root/"QA"/"native_binary_manifest.json").write_text(json.dumps({"files":rows,"blender_native":"PASS","unity_import":"NOT_RUN","independent_QA":"NOT_RUN"},indent=2))
if __name__=="__main__":
 argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
 ap=argparse.ArgumentParser();ap.add_argument("--out",default="Assets/C01StructuralPrototypes/P14")
 args=ap.parse_args(argv)
 build(args.out)
