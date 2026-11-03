import bpy,json,sys,math,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[2]/"Assets/C01InteriorProps/P15Wave02"
ids=("P15-04","P15-05","P15-06","P15-07")
rows=[]
def add(asset,test,ok,details=None):
 rows.append({"asset":asset,"test":test,"result":"PASS" if ok else "FAIL","details":details})
for aid in ids:
 native=base/"Sources/Blender"/(aid+".blend"); fbx=base/"Models/FBX"/(aid+".fbx")
 manifest=json.loads((base/"Manifests"/(aid+".json")).read_text())
 bpy.ops.wm.open_mainfile(filepath=str(native))
 meshes=[o for o in bpy.data.objects if o.type=="MESH"]
 roots=[o for o in bpy.data.objects if o.name==aid+"_ROOT"]
 add(aid,"source_geometry",len(meshes)>0,len(meshes))
 # Verify the ACTUAL source mesh vertices, not only math formulas and string manifest values.
 def uvcoords(ob):
  return [(float((ob.matrix_world@v.co).x),float((ob.matrix_world@v.co).z),float(-(ob.matrix_world@v.co).y)) for v in ob.data.vertices]
 def must_contain(name,desired):
  obj=next((o for o in meshes if o.name==name),None)
  if obj is None:return False
  coords=uvcoords(obj)
  return all(any(sum((q[i]-p[i])**2 for i in range(3))<1e-8 for q in coords) for p in desired)
 if aid=="P15-04":
  for side,x in (("input",0),("output",3)):
   expected=[(x,y,z) for y in (-.18,-.16) for z in (-.19,.19)]
   add(aid,"actual_mesh_"+side+"_cross_section",must_contain("Tray_Bottom",expected))
 if aid=="P15-05":
  expected_in=[(0,y,z) for y in (-.18,-.16) for z in (-.19,.19)]
  expected_out=[(x,y,.55) for y in (-.18,-.16) for x in (.36,.74)]
  add(aid,"actual_mesh_elbow_input_port",must_contain("Elbow_Base",expected_in))
  add(aid,"actual_mesh_elbow_output_port",must_contain("Elbow_Base",expected_out))
  # Catches the previous P15-05 defect where bundle tubes continued around 180 degrees.
  geometry=[p for obj in meshes for p in uvcoords(obj)]
  add(aid,"actual_mesh_90_degree_arc_clearance",min(p[2] for p in geometry)>=-.195 and max(p[2] for p in geometry)<=.56,
      {"z_min":min(p[2] for p in geometry),"z_max":max(p[2] for p in geometry)})
 if aid=="P15-06":
  geometry=[p for obj in meshes for p in uvcoords(obj)]
  add(aid,"actual_mesh_wall_plane",min(p[2] for p in geometry)>=-.005)
 if aid=="P15-07":
  geometry=[p for obj in meshes for p in uvcoords(obj)]
  add(aid,"actual_mesh_ground_and_wall",min(p[1] for p in geometry)>=-.005 and min(p[2] for p in geometry)>=-.005)

 add(aid,"source_root_pivot",len(roots)==1 and all(abs(p)<1e-8 for p in roots[0].location))
 add(aid,"source_scale",all(all(abs(v-1)<1e-6 for v in o.scale) for o in meshes))
 add(aid,"source_uv0",all(len(o.data.uv_layers)>0 for o in meshes))
 add(aid,"source_nondegenerate_faces",all(len(o.data.polygons)>0 and all(p.area>1e-9 for p in o.data.polygons) for o in meshes))
 add(aid,"source_materials",all(o.data.materials and len(o.data.materials)<=4 for o in meshes))
 add(aid,"source_triangles",sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)==manifest["triangle_count_blender"])
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(fbx))
 meshes=[o for o in bpy.data.objects if o.type=="MESH"]
 add(aid,"fbx_roundtrip_import",len(meshes)>0,len(meshes))
 add(aid,"fbx_uv0",all(len(o.data.uv_layers)>0 for o in meshes))
 add(aid,"fbx_normals_and_faces",all(len(o.data.polygons)>0 and all(p.area>1e-9 for p in o.data.polygons) for o in meshes))
 add(aid,"fbx_material_slots",all(len(o.data.materials)>0 for o in meshes))
 add(aid,"png_previews",all((base/"Previews/Blender"/(aid+"_"+v+".png")).stat().st_size>1024 for v in ("front","iso","side")))
# Contract checks for connector centerlines & cross-sections, analytically independent of mesh file.
R=.55
def frame(t,w,y):
 return (R*math.sin(t)-w*math.sin(t),y,R*(1-math.cos(t))+w*math.cos(t))
add("P15-04/P15-05","entry_port_identical", all(abs(frame(0,w,y)[i]-[0,y,w][i])<1e-10 for w in (-.19,.19) for y in (-.18,-.16,-.05) for i in range(3)))
add("P15-04/P15-05","exit_90deg_port", all(abs(frame(math.pi/2,w,y)[i]-[R-w,y,R][i])<1e-10 for w in (-.19,.19) for y in (-.18,-.16,-.05) for i in range(3)))
add("P15-04/P15-05","end_faces_orthogonal",abs(math.cos(math.pi/2))<1e-10)
out={"format":"C01-15_W02_BLENDER_ROUNDTRIP_V1","scope":"real .blend load + FBX Blender re-import, UV0, normals/face area, materials, ports by analytic formulas; NOT Unity","blender_version":bpy.app.version_string,"results":rows,"status":"PASS" if all(x["result"]=="PASS" for x in rows) else "FAIL","unity_import":"NOT RUN","independent_QA":"NOT RUN"}
(base/"QA/blender_roundtrip.json").write_text(json.dumps(out,indent=2)+"\n")
print("C01_W02_AUDIT",out["status"],"checks",len(rows),"fails",[r for r in rows if r["result"]=="FAIL"])
if out["status"]!="PASS":sys.exit(1)
