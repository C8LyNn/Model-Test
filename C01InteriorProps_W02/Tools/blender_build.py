#!/usr/bin/env python3
"""Actual Blender 4.x import/export for C01-17 Wave02 (NOT a simulator)."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path(".").resolve()
SRC=R/"C01InteriorProps_W02"; MODELS=R/"Assets/C01InteriorProps/W02/Models"
for x in (SRC/"Blender",SRC/"Previews"): x.mkdir(parents=True,exist_ok=True)
for id in ("P17-04","P17-05","P17-06","P17-07"):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(MODELS/(id+".gltf")))
 obj=list(bpy.context.scene.objects);mesh=[o for o in obj if o.type=="MESH"]
 spec=json.loads((SRC/"Specs"/(id+".json")).read_text())
 if len(mesh)!=spec["mesh_parts"]:raise RuntimeError("Unexpected mesh count "+id)
 for o in mesh:
  if not o.data.uv_layers or len(o.data.uv_layers[0].data)==0:raise RuntimeError("UV0 missing "+o.name)
  if not o.data.polygons:raise RuntimeError("Missing faces "+o.name)
 for pivot in spec["moving_parts"]:
  if not any(pivot["name"] in o.name and o.type=="EMPTY" for o in obj):
   raise RuntimeError("Missing movable pivot "+id+"/"+pivot["name"])
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(c) for o in mesh for c in o.bound_box]
 low=[min(v[i] for v in pts) for i in range(3)]
 high=[max(v[i] for v in pts) for i in range(3)]
 measured=[high[i]-low[i] for i in range(3)]  # Blender: X,Y(depth),Z(height)
 wanted=spec["dimensions_WDH_m"]
 if any(abs(measured[i]-wanted[i])>.003 for i in range(3)):
  raise RuntimeError(id+" size mismatch "+str(measured)+" versus "+str(wanted))
 bpy.ops.wm.save_as_mainfile(filepath=str(SRC/"Blender"/(id+".blend")))
 bpy.ops.object.select_all(action="DESELECT")
 for o in obj:o.select_set(True)
 bpy.context.view_layer.objects.active=mesh[0]
 bpy.ops.export_scene.fbx(filepath=str(MODELS/(id+".fbx")),
      use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',
      apply_unit_scale=True,global_scale=1.0,bake_anim=False)
 for kind,az,ht in (("front",-math.pi/2,.2),("side",0,.2),("iso",-math.pi/4,.65)):
  bpy.context.view_layer.objects.active=mesh[0]
  cam=bpy.data.objects.new("QA_CAMERA",bpy.data.cameras.new("QA_CAMERA"))
  bpy.context.scene.collection.objects.link(cam)
  center=Vector([(low[i]+high[i])*.5 for i in range(3)])
  cam.location=center+Vector((math.cos(az)*3,math.sin(az)*3,ht*3))
  cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
  cam.data.type='ORTHO';cam.data.ortho_scale=max(max(measured)*1.55,.5)
  sc=bpy.context.scene;sc.camera=cam;sc.render.engine="BLENDER_WORKBENCH"
  sc.display.shading.color_type="MATERIAL";sc.display.shading.light="STUDIO"
  sc.render.resolution_x=960;sc.render.resolution_y=960;sc.render.resolution_percentage=100
  sc.render.image_settings.file_format="PNG"
  sc.render.filepath=str(SRC/"Previews"/(id+"_"+kind+".png"))
  bpy.ops.render.render(write_still=True)
  bpy.data.objects.remove(cam,do_unlink=True)
 print("PASS BLENDER",id,measured,"parts",len(mesh),"UV0",len(mesh),flush=True)
print("C01-17 W02 Blender FBX PNG output PASS",flush=True)
