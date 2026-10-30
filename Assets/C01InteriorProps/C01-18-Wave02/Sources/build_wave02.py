"""C01-18 Wave02 real geometry producer. Requires Blender >=4 and FBX exporter.
Run: blender -b --python build_wave02.py -- /absolute/output/root
Authoritative geometry generated from primitives, not placeholder text.
Coordinates and manifest defined in Unity XYZ (Y up); converted to Blender XYZ (Z up).
"""
import bpy, math, sys, pathlib, json, hashlib
from mathutils import Vector
ROOT=pathlib.Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else pathlib.Path(__file__).resolve().parents[1]
for d in ["Sources","Models","Previews","QA"]: (ROOT/d).mkdir(parents=True,exist_ok=True)
PAL={
 "STEEL":(.31,.39,.46,1),"DARK":(.07,.11,.16,1),
 "CAUTION":(.94,.52,.13,1),"GASKET":(.11,.15,.19,1)
}
SPEC={
 "P18-04":{"title":"Transport cylinder","dimensions_WDH":[.56,.56,1.08],"function":"hand-carried technical material canister"},
 "P18-05":{"title":"Lockable equipment case","dimensions_WDH":[.68,.46,.34],"function":"portable latching equipment case"},
 "P18-06":{"title":"Hazardous sample containment","dimensions_WDH":[.66,.58,.78],"function":"protected movable specimen container"},
 "P18-07":{"title":"Portable tool bin","dimensions_WDH":[.56,.34,.38],"function":"portable maintenance tools caddy"},
}
# Blender is Z up. Transform Unity (X,Y,Z) -> Blender (X,-Z,Y).
def xyz(p):return (p[0],-p[2],p[1])
def dims(s):return (s[0],s[2],s[1])
def mat(name):
 m=bpy.data.materials.new("C01_"+name);m.diffuse_color=PAL[name]
 m.use_nodes=True;bs=m.node_tree.nodes.get("Principled BSDF")
 if bs:
  bs.inputs["Base Color"].default_value=PAL[name]
  bs.inputs["Metallic"].default_value=.55 if name!="GASKET" else .12
  bs.inputs["Roughness"].default_value=.66
 return m
def material_assign(obj,key):obj.data.materials.clear();obj.data.materials.append(MATERIALS[key]);obj.color=PAL[key]
def cube(name,p,s,role,root,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p))
 o=bpy.context.object;o.name=name;o.dimensions=dims(s)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 material_assign(o,role)
 if bevel:
  mod=o.modifiers.new("Soft manufacturing edge","BEVEL");mod.width=bevel;mod.segments=1
  mod.affect="EDGES" if hasattr(mod,"affect") else None
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.modifier_apply(modifier=mod.name)
 o.parent=root;return o
def cyl(name,p,r,height,role,root,vertices=16):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=height,location=xyz(p))
 o=bpy.context.object;o.name=name;material_assign(o,role);o.parent=root
 return o
def hinge(name,p,root,parts):
 e=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(e);e.empty_display_type="ARROWS"
 e.location=xyz(p);e.parent=root;parts.append({"name":name,"pivot_unity_xyz":list(p),"type":"hinge"})
 return e
def attach_preserve(o,parent):
 mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
def build(pid,root,parts):
 def box(n,p,s,r="STEEL",col=False):
  o=cube(n,p,s,r,root);parts.append({"name":n,"role":r,"collider":col,"type":"box"});return o
 def tube(n,p,r,h,role="STEEL",col=False):
  o=cyl(n,p,r,h,role,root);parts.append({"name":n,"role":role,"collider":col,"type":"cylinder"});return o
 if pid=="P18-04":
  box("Floor_Foot",[0,.03,0],[.56,.06,.56],"DARK",True)
  tube("Pressure_Shell",[0,.48,0],.225,.84,"STEEL",True)
  tube("Lower_Retention_Band",[0,.13,0],.246,.05,"DARK")
  tube("Upper_Retention_Band",[0,.85,0],.246,.07,"DARK")
  tube("Neck",[0,.943,0],.165,.11,"GASKET")
  tube("Safety_Cap",[0,1.015,0],.20,.07,"CAUTION")
  box("Top_Grip",[0,1.065,0],[.31,.03,.075],"DARK")
  box("Front_Warning",[0,.51,.231],[.18,.17,.007],"CAUTION")
  box("Transport_Socket",[0,.06,.22],[.26,.05,.10],"DARK")
 elif pid=="P18-05":
  box("Case_Bottom",[0,.10,0],[.68,.20,.40],"STEEL",True)
  box("Rubber_Foot_L",[-.24,.014,-.15],[.13,.028,.1],"GASKET")
  box("Rubber_Foot_R",[.24,.014,-.15],[.13,.028,.1],"GASKET")
  lid=box("Case_Lid",[0,.239,0],[.68,.078,.40],"DARK",True)
  edge=box("Lid_Accent",[0,.282,0],[.60,.008,.34],"CAUTION")
  h=hinge("Lid_HingePivot",[0,.20,-.20],root,parts);attach_preserve(lid,h);attach_preserve(edge,h)
  box("Front_Latch_L",[-.23,.19,.208],[.065,.10,.025],"CAUTION")
  box("Front_Latch_R",[.23,.19,.208],[.065,.10,.025],"CAUTION")
  box("Carry_Handle_Rail",[0,.3225,.24],[.25,.035,.038],"GASKET")
  box("Carry_Handle_Stem_L",[-.15,.285,.205],[.035,.07,.032],"DARK")
  box("Carry_Handle_Stem_R",[.15,.285,.205],[.035,.07,.032],"DARK")
 elif pid=="P18-06":
  box("Reinforced_Base",[0,.05,0],[.66,.10,.58],"DARK",True)
  box("Sample_Vault",[0,.395,0],[.52,.59,.44],"STEEL",True)
  for x in (-.29,.29):
   for z in (-.25,.25):
    box("Cage_Post_%s_%s"%(x,z),[x,.395,z],[.055,.59,.055],"DARK")
  box("Safety_Lid",[0,.74,0],[.66,.08,.58],"DARK",True)
  box("Hazard_Emblem",[0,.46,.226],[.24,.19,.008],"CAUTION")
  box("Latch_Left",[-.23,.72,.296],[.08,.09,.012],"CAUTION")
  box("Latch_Right",[.23,.72,.296],[.08,.09,.012],"CAUTION")
  box("Carry_Rail",[0,.775,0],[.22,.01,.095],"GASKET")
 elif pid=="P18-07":
  box("Bin_Chassis",[0,.115,0],[.54,.23,.31],"STEEL",True)
  box("Base_Stiffener",[0,.035,0],[.56,.07,.34],"DARK")
  lid=box("Bin_Lid",[0,.265,0],[.56,.07,.34],"DARK",True)
  trim=box("Lid_Label",[0,.305,.08],[.24,.008,.10],"CAUTION")
  h=hinge("Toolbox_LidHinge",[0,.23,-.17],root,parts);attach_preserve(lid,h);attach_preserve(trim,h)
  box("Handle_Post_L",[-.13,.325,0],[.038,.09,.04],"GASKET")
  box("Handle_Post_R",[.13,.325,0],[.038,.09,.04],"GASKET")
  box("Handle_Grip",[0,.367,0],[.30,.026,.04],"GASKET")
  box("Front_Lock",[0,.225,.176],[.08,.075,.012],"CAUTION")
  for x in [-.23,.23]:box("Grip_Rail_"+str(x),[x,.12,.164],[.027,.15,.01],"DARK")
 else:raise ValueError(pid)
def metrics(root):
 meshes=[o for o in root.children_recursive if o.type=="MESH"]
 coords=[]
 for o in meshes:
  for v in o.data.vertices:
   # World coords Blender -> Unity: X, Z, -Y.
   p=o.matrix_world@v.co
   coords.append((p.x,p.z,-p.y))
 mins=[min(p[i] for p in coords) for i in range(3)]
 maxs=[max(p[i] for p in coords) for i in range(3)]
 return {"bounds_min_unity_xyz":mins,"bounds_max_unity_xyz":maxs,
 "bounds_WDH":[maxs[0]-mins[0],maxs[2]-mins[2],maxs[1]-mins[1]],
 "mesh_parts":len(meshes),"triangles":sum(sum(max(0,len(poly.vertices)-2) for poly in o.data.polygons) for o in meshes),
 "parts_missing_uv":[o.name for o in meshes if not o.data.uv_layers],
 "parts_missing_polygons":[o.name for o in meshes if not o.data.polygons]}
def render_preview(pid,root,view):
 # Real Blender Workbench screenshots generated from the actual scene.
 bpy.context.scene.render.engine="BLENDER_WORKBENCH"
 bpy.context.scene.display.shading.light="STUDIO"
 bpy.context.scene.display.shading.color_type="MATERIAL"
 bpy.context.scene.render.resolution_x=640
 bpy.context.scene.render.resolution_y=640
 bpy.context.scene.render.resolution_percentage=100
 if view=="front":loc=(2.5,-4.5,2.25)
 elif view=="side":loc=(4.5,1.8,2.05)
 else:loc=(3.2,-3.6,2.6)
 camera_data=bpy.data.cameras.new("Camera_"+view);camera=bpy.data.objects.new("Camera_"+view,camera_data)
 bpy.context.collection.objects.link(camera);camera.location=loc
 direction=Vector((0,0,.51))-camera.location
 camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 camera_data.type="ORTHO";camera_data.ortho_scale=3.05 if pid!="P18-04" else 2.5
 bpy.context.scene.camera=camera
 bpy.context.scene.render.image_settings.file_format='PNG'
 bpy.context.scene.render.filepath=str(ROOT/"Previews"/(pid+"_"+view+".png"))
 bpy.ops.render.render(write_still=True);bpy.data.objects.remove(camera,do_unlink=True)
def export(pid):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 global MATERIALS
 MATERIALS={n:mat(n) for n in PAL}
 root=bpy.data.objects.new(pid+"_Root",None);bpy.context.collection.objects.link(root)
 root.empty_display_type='CUBE';root.empty_display_size=.1
 parts=[];build(pid,root,parts)
 bpy.context.view_layer.update()
 info=metrics(root)
 expected=SPEC[pid]["dimensions_WDH"]
 if any(abs(a-b)>.011 for a,b in zip(info["bounds_WDH"],expected)):raise RuntimeError(pid+" bad dimensions "+repr(info["bounds_WDH"])+" expected "+repr(expected))
 if any(abs(a)>1e-5 for a in (info["bounds_min_unity_xyz"][1],)):raise RuntimeError(pid+" not floor anchored: "+str(info))
 if info["parts_missing_uv"] or info["parts_missing_polygons"]:raise RuntimeError(pid+" invalid UV/geometry: "+repr(info))
 info.update({"id":pid,"version":"0.2.0","nominal_WDH":expected,"pivot_unity_xyz":[0,0,0],
 "scale_unity":[1,1,1],"material_slots":list(PAL),"parts":parts,"mounting":"floor standing / pickup-ready","unity_import":"NOT RUN"})
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"Sources"/(pid+".blend")))
 for view in ("front","side","iso"):render_preview(pid,root,view)
 bpy.ops.object.select_all(action="DESELECT")
 for o in [root]+list(root.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=root
 bpy.ops.export_scene.fbx(filepath=str(ROOT/"Models"/(pid+".fbx")),use_selection=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,apply_unit_scale=True,object_types={'MESH','EMPTY'})
 # Explicit independent format importer validation in Blender, not Unity.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/"Models"/(pid+".fbx")))
 imported=[o for o in bpy.context.scene.objects if o.type=="MESH"]
 if not imported:raise RuntimeError(pid+" import produced no meshes")
 for o in imported:
  if not o.data.uv_layers:raise RuntimeError(pid+" re-imported FBX lacks UV0 in "+o.name)
  if not o.data.polygons:raise RuntimeError(pid+" re-imported FBX mesh empty "+o.name)
 info["blender_fbx_roundtrip"]="PASS"
 info["imported_mesh_parts"]=len(imported)
 return info
out={}
for pid in SPEC:
 print("BUILD",pid,flush=True)
 out[pid]=export(pid)
(ROOT/"QA"/"BlenderBuildReport.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print("C01-18_WAVE02_BLENDER_ROUNDTRIP_PASS",list(out),flush=True)
