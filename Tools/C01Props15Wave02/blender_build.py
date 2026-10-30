# C01-15 WAVE02 | executable geometric authoring in actual Blender
# All design positions below are in Unity meters: X-right Y-up Z-forward.
import bpy, math, json, hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/"Assets/C01InteriorProps/P15Wave02"
for x in ["Sources/Blender","Models/FBX","Previews/Blender","QA","Manifests"]:
 (P/x).mkdir(parents=True,exist_ok=True)
PALETTE={"STEEL":(.42,.50,.57,1),"DARK":(.09,.12,.16,1),"WARN":(.92,.48,.11,1),"COOLANT":(.09,.40,.54,1)}
objects=[]
def B(p):return (p[0],-p[2],p[1])
def mat(role):
 m=bpy.data.materials.new("C01_P15_"+role);m.diffuse_color=PALETTE[role];m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF")
 if bs:
  bs.inputs["Base Color"].default_value=PALETTE[role]
  bs.inputs["Metallic"].default_value=.6 if role in ("STEEL","DARK") else .18
  bs.inputs["Roughness"].default_value=.43
 return m
def mesh(name,verts,faces,role,uv_mode="auto"):
 data=bpy.data.meshes.new(name+"_MESH");data.from_pydata([B(v) for v in verts],[],faces);data.update()
 uv=data.uv_layers.new(name="UVMap")
 for face in data.polygons:
  for lid in face.loop_indices:
   vi=data.loops[lid].vertex_index;vx,vy,vz=verts[vi]
   uv.data[lid].uv=(vx*.5+vz*.7,vy*.65+vz*.35)
 ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.data.materials.append(mats[role]);ob.parent=assetroot
 objects.append(ob)
 return ob
def box(name,lo,hi,role):
 x,y,z=lo;X,Y,Z=hi
 v=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
 faces=[(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(0,1,5,4),(3,7,6,2)]
 return mesh(name,v,faces,role)
def cub(name,c,size,role):
 return box(name,tuple(c[i]-size[i]*.5 for i in range(3)),tuple(c[i]+size[i]*.5 for i in range(3)),role)
def tube(name,points,r,role,sides=12):
 # Procedural pipe with continuous ring cross sections, UV0 and closed ends.
 n=len(points);verts=[]
 for i,p in enumerate(points):
  pr=Vector(points[max(0,i-1)]);nx=Vector(points[min(n-1,i+1)])
  t=(nx-pr).normalized();bi=t.cross(Vector((0,1,0))).normalized()
  if bi.length<1e-7:bi=t.cross(Vector((0,0,1))).normalized()
  u=bi.cross(t).normalized()
  for j in range(sides):
   q=Vector(p)+r*(math.cos(2*math.pi*j/sides)*u+math.sin(2*math.pi*j/sides)*bi)
   verts.append(tuple(q))
 faces=[]
 for i in range(n-1):
  for j in range(sides):
   jj=(j+1)%sides
   faces.append((i*sides+j,i*sides+jj,(i+1)*sides+jj,(i+1)*sides+j))
 faces.append(tuple(reversed(range(sides))))
 faces.append(tuple((n-1)*sides+j for j in range(sides)))
 return mesh(name,verts,faces,role)
def arc_point(t,w,y,R=.55):
 # Centerline: x=R*sin(t), z=R*(1-cos(t)); normal=(-sin(t),cos(t))
 return (R*math.sin(t)-w*math.sin(t),y,R*(1-math.cos(t))+w*math.cos(t))
def bent_strip(name,wrange,yrange,role,segments=24):
 verts=[];faces=[]
 for k in range(segments+1):
  t=math.pi*k/(2*segments)
  for y,w in [(yrange[0],wrange[0]),(yrange[0],wrange[1]),(yrange[1],wrange[1]),(yrange[1],wrange[0])]:
   verts.append(arc_point(t,w,y))
 for k in range(segments):
  for j in range(4):
   faces.append((4*k+j,4*k+(j+1)%4,4*(k+1)+(j+1)%4,4*(k+1)+j))
 faces.append((3,2,1,0))
 j=4*segments;faces.append((j,j+1,j+2,j+3))
 return mesh(name,verts,faces,role)
def rings_of_cable_bend():
 for i,w in enumerate([-.10,0,.10]):
  pts=[arc_point(math.pi*j/64,w,-.132) for j in range(65)]
  tube("Elbow_Cable_%d"%i,pts,.0115,"COOLANT" if i==1 else "DARK",10)
def make_straight():
 # Connector ports x=0 and x=3, Y=-.18..-.05, Z=-.19..+.19.
 box("Tray_Bottom",(0,-.18,-.19),(3,-.16,.19),"STEEL")
 box("Tray_Rail_Left",(0,-.16,-.19),(3,-.05,-.17),"STEEL")
 box("Tray_Rail_Right",(0,-.16,.17),(3,-.05,.19),"STEEL")
 for i,w in enumerate([-.10,0,.10]):
  tube("Cable_3m_%02d"%i,[(3*j/24,-.132,w) for j in range(25)],.0115,"COOLANT" if i==1 else "DARK",10)
 for i,x in enumerate([.24,.94,1.64,2.34,2.80]):
  cub("Mount_Bridge_%02d"%i,(x,-.035,0),(.075,.060,.33),"DARK")
  for side,z in enumerate([-.16,.16]):
   cub("Mount_Bolt_%d_%d"%(i,side),(x,-.004,z),(.022,.008,.025),"WARN")
 for i,x in enumerate([.40,1.50,2.60]):
  cub("Tray_Warning_%d"%i,(x,-.048,.185),(.17,.006,.009),"WARN")
def make_elbow():
 for name,w,y in [("Elbow_Base",(-.19,.19),(-.18,-.16)),
                    ("Elbow_LeftRail",(-.19,-.17),(-.16,-.05)),
                    ("Elbow_RightRail",(.17,.19),(-.16,-.05))]:
  bent_strip(name,w,y,"STEEL")
 rings_of_cable_bend()
 for idx,t in enumerate([.28,.78,1.30]):
  c=arc_point(t,0,-.027)
  # Safety bridge is small, fully internal and below ceiling mounting plane.
  cub("Elbow_Mount_%d"%idx,c,(.065,.038,.065),"DARK")
def make_bundle():
 # Wall plane Z=0. 1.5 m cable spine and repeated retaining clips.
 for k in range(6):
  y0=-.044+(k//3)*.064
  z0=.086+(k%3)*.046
  pts=[]
  for i in range(49):
   x=1.5*i/48
   pts.append((x,y0+.011*math.sin(x*5+k*.8),z0+.010*math.sin(x*4+k*.4)))
  tube("Wire_%d"%k,pts,.013,"COOLANT" if k in (1,4) else "DARK",12)
 for i,x in enumerate([.13,.50,.87,1.24,1.43]):
  cub("Wall_Saddle_%d"%i,(x,0,.014),(.078,.138,.028),"STEEL")
  cub("Cable_Hoop_Top_%d"%i,(x,.091,.145),(.055,.014,.159),"STEEL")
  cub("Cable_Hoop_Bottom_%d"%i,(x,-.091,.145),(.055,.014,.159),"STEEL")
  for side,z in enumerate([.072,.223]):
   cub("Hoop_Foot_%d_%d"%(i,side),(x,0,z),(.055,.17,.016),"STEEL")
 for x in (.43,1.08):
  cub("Harness_ID_band_"+str(x),(x,.054,.16),(.045,.014,.18),"WARN")
def make_coolant():
 # Backplate is flush on Z=0 plane; all details face +Z.
 cub("Distribution_Backplate",(0,.45,.023),(1.20,.90,.046),"DARK")
 for i,y in enumerate([.09,.81]):
  cub("Mount_Crossbar_"+str(i),(0,y,.064),(1.10,.043,.038),"STEEL")
 for k,x in enumerate([-.48,.48]):
  for j,y in enumerate([.12,.78]):
   cub("Fixing_%d_%d"%(k,j),(x,y,.078),(.048,.048,.025),"WARN")
 for k,x in enumerate([-.37,0,.37]):
  tube("Upright_Pipe_"+str(k),[(x,.15+.56*i/16,.165) for i in range(17)],.039,"COOLANT",16)
  tube("Coolant_Outlet_"+str(k),[(x,.145,.165),(x,.125,.22)],.035,"STEEL",16)
 tube("Pressure_Header",[(x/100,.48,.165) for x in range(-46,47,2)],.049,"STEEL",16)
 for j,x in enumerate([-.255,.255]):
  # Pressure gauges protrude but remain within overall 0.35m depth.
  z=.265;y=.705
  tube("Gauge_Ring_"+str(j),[(x+.098*math.cos(2*math.pi*k/40),y+.098*math.sin(2*math.pi*k/40),z) for k in range(41)],.013,"STEEL",12)
  # Dial uses 16-segment disk; cylinder axis local Z.
  v=[(x,y,z-.009)]
  v += [(x+.083*math.cos(2*math.pi*k/24),y+.083*math.sin(2*math.pi*k/24),z-.009) for k in range(24)]
  f=[(0,1+k,1+((k+1)%24)) for k in range(24)]
  mesh("Gauge_Face_"+str(j),v,f,"DARK")
  tube("Gauge_Needle_"+str(j),[(x,y,z+.006),(x+.047,y+.025,z+.006)],.009,"WARN",8)
 cub("Coolant_Identification",(0,.255,.075),(.24,.073,.013),"WARN")
def bounds(objects):
 lo=[1e9]*3;hi=[-1e9]*3
 for o in objects:
  for v in o.data.vertices:
   w=o.matrix_world@v.co
   p=(float(w.x),float(w.z),float(-w.y))
   for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
 return [lo,hi]
def export_fbx(aid):
 bpy.ops.object.select_all(action="DESELECT")
 arr=[assetroot]+objects
 for o in arr:o.select_set(True)
 bpy.context.view_layer.objects.active=assetroot
 bpy.ops.export_scene.fbx(filepath=str(P/"Models/FBX"/(aid+".fbx")),use_selection=True,
    global_scale=1,apply_unit_scale=True,axis_forward="-Z",axis_up="Y",add_leaf_bones=False,
    bake_anim=False,object_types={"EMPTY","MESH"},path_mode="AUTO")
def preview(aid,view,center,size):
 data=bpy.data.cameras.new("QA_CAMERA");camera=bpy.data.objects.new("QA_CAMERA",data)
 bpy.context.collection.objects.link(camera)
 offsets={"front":(0,.3,2.7),"iso":(1.75,1.35,2.25),"side":(2.6,.25,0)}
 d=offsets[view];p=(center[0]+d[0]*size,center[1]+d[1]*size,center[2]+d[2]*size)
 camera.location=B(p)
 camera.rotation_euler=(Vector(B(center))-camera.location).to_track_quat("-Z","Y").to_euler()
 data.type="ORTHO";data.ortho_scale=size*1.62
 sc=bpy.context.scene;sc.camera=camera;sc.render.engine="BLENDER_WORKBENCH"
 sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
 sc.render.resolution_x=1000;sc.render.resolution_y=760;sc.render.resolution_percentage=100
 sc.render.image_settings.file_format="PNG"
 sc.render.filepath=str(P/"Previews/Blender"/(aid+"_"+view+".png"))
 bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(camera,do_unlink=True)
models={
"P15-04":{"name":"Ceiling cable tray straight 3m","mount":"ceiling; local Y=0 is mounting plane","extent_wdh_m":[3,.38,.18],"socket_in":"X=0, Y[-.18,-.05], Z[-.19,.19]","socket_out":"X=3, Y[-.18,-.05], Z[-.19,.19]","builder":make_straight,"camera":(1.50,-.10,0)},
"P15-05":{"name":"Cable tray elbow 90 degrees","mount":"ceiling; local Y=0 is mounting plane","extent_wdh_m":[.74,.74,.18],"socket_in":"X=0, Y[-.18,-.05], Z[-.19,.19]","socket_out":"Z=.55, Y[-.18,-.05], X[.36,.74]","builder":make_elbow,"camera":(.27,-.10,.27)},
"P15-06":{"name":"Technical wire harness with clips","mount":"wall; local Z=0 is mounting plane","extent_wdh_m":[1.5,.245,.21],"builder":make_bundle,"camera":(.75,0,.12)},
"P15-07":{"name":"Wall coolant distribution and manometers","mount":"wall; local Z=0 is mounting plane; bottom at local Y=0","extent_wdh_m":[1.2,.35,.90],"builder":make_coolant,"camera":(0,.45,.15)}
}
report={}
for aid,data in models.items():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.scene.unit_settings.system="METRIC";bpy.context.scene.unit_settings.scale_length=1
 mats={name:mat(name) for name in PALETTE}
 assetroot=bpy.data.objects.new(aid+"_ROOT",None);bpy.context.collection.objects.link(assetroot);objects=[]
 data["builder"]()
 bpy.context.view_layer.update()
 bbox=bounds(objects)
 bpy.ops.wm.save_as_mainfile(filepath=str(P/"Sources/Blender"/(aid+".blend")),compress=False)
 export_fbx(aid)
 for view in ["front","iso","side"]:
  preview(aid,view,data["camera"],max(data["extent_wdh_m"]))
 tris=sum(sum(len(poly.vertices)-2 for poly in o.data.polygons) for o in objects)
 manifest={
  "id":aid,"owner":"C01-15","version":"0.1.0","project":"C01 — INTERIOR PROPS / WAVE 02",
  "name":data["name"],"mounting_surface":data["mount"],"root_pivot_local_m":[0,0,0],
  "coordinate_system":"Unity X-right Y-up Z-forward","root_scale":[1,1,1],
  "nominal_extent_WDH_m":data["extent_wdh_m"],"measured_bounds_XYZ_m":bbox,
  "triangle_count_blender":tris,"mesh_objects":len(objects),"materials":[x for x in PALETTE if any(x in m.name for o in objects for m in o.data.materials)],
  "input_port":data.get("socket_in"),"output_port":data.get("socket_out"),
  "blender_file":"Sources/Blender/"+aid+".blend","fbx_file":"Models/FBX/"+aid+".fbx",
  "previews":["Previews/Blender/"+aid+"_"+v+".png" for v in ["front","iso","side"]],
  "unity_prefab":"PENDING — build via C01Props15Wave02PrefabBuilder in Unity 6",
  "blender_fbX":"SEE QA/blender_roundtrip.json","unity_import":"NOT RUN","independent_QA":"NOT RUN"
 }
 (P/"Manifests"/(aid+".json")).write_text(json.dumps(manifest,indent=2)+"\n")
 report[aid]={"bbox":bbox,"triangles":tris,"meshes":len(objects)}
print("C01-15 WAVE02 Blender sources FBX and actual renders",json.dumps(report))
