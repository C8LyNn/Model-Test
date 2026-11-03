import bpy,json
from pathlib import Path
from mathutils import Matrix
root=Path(__file__).resolve().parent
out=root/'PolishSource';out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Unity positions/sizes are converted from (X,Y,Z) to Blender (X,-Z,Y).
parts=[('base',(0,.18,0),(.35,.36,3),'metal'),('display',(0,1.62,0),(.18,2.52,2.78),'screen'),('left',(0,1.62,-1.445),(.3,2.52,.11),'dark'),('right',(0,1.62,1.445),(.3,2.52,.11),'dark'),('top',(0,2.93,0),(.3,.1,3),'metal')]
cols={'metal':(.32,.4,.47,1),'screen':(.2,.7,.9,1),'dark':(.07,.12,.17,1)}
mats={}
for name,color in cols.items():
 m=bpy.data.materials.new(name);m.diffuse_color=color;mats[name]=m
objs=[]
for name,pos,size,role in parts:
 x,y,z=pos;sx,sy,sz=size
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-z,y));o=bpy.context.object;o.name=name;o.dimensions=(sx,sz,sy)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[role]);objs.append(o)
assert abs(max(o.location.z+o.dimensions.z/2 for o in objs)-2.98)<1e-5
bpy.ops.wm.save_as_mainfile(filepath=str(out/'C01_v64_Bridge_Viewscreen.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.fbx(filepath=str(out/'C01_v64_Bridge_Viewscreen.fbx'),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(out/'C01_v64_Bridge_Viewscreen.fbx'));new=set(bpy.data.objects)-before
meshes=[o for o in new if o.type=='MESH']
assert len(meshes)==len(parts)
report={'status':'PASS','parts':len(parts),'height_m':2.98,'fbx_reimport_meshes':len(meshes),'blender':bpy.app.version_string}
(out/'bridge_screen_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
