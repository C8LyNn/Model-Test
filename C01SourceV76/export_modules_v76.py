"""Export the 11 reusable wall/roof variants and verify FBX round trips."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parent.parent
ids=['G76_LaunchLeft','G76_LaunchRight','G76_LaunchLeaf']
out=ROOT/'C01SourceV76/Models';out.mkdir(parents=True,exist_ok=True)
collection=bpy.data.collections['SOURCE_MODELS_editable'];collection.hide_viewport=False;collection.hide_render=False
exports=[];checks=[]
for ident in ids:
    parent=bpy.data.objects.get(ident)
    if parent is None:raise RuntimeError('Missing source model '+ident)
    parts=sorted((p for p in parent.children if p.type=='MESH'),key=lambda p:p.name)
    if not parts:raise RuntimeError('Empty module '+ident)
    bpy.ops.object.select_all(action='DESELECT');parent.select_set(True)
    for p in parts:p.select_set(True)
    bpy.context.view_layer.objects.active=parent;originals=[]
    for p in parts:
        original=p.data;copy=original.copy();copy.transform(Matrix.Diagonal((-1,1,1,1)));copy.flip_normals();p.data=copy;originals.append((p,original,copy))
    fbx=out/(ident+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'EMPTY','MESH'},global_scale=1,
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,mesh_smooth_type='FACE',bake_anim=False)
    for p,original,copy in originals:p.data=original;bpy.data.meshes.remove(copy)
    bpy.ops.wm.obj_export(filepath=str(out/(ident+'.obj')),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True,export_triangulated_mesh=True)
    if fbx.stat().st_size<1024 or (out/(ident+'.obj')).stat().st_size<100:raise RuntimeError('Empty export '+ident)
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(fbx));created=set(bpy.data.objects)-before
    imported=[o for o in created if o.type=='MESH'];errors=[]
    if len(imported)!=len(parts):errors.append('part count')
    for i,source in enumerate(parts):
        found=[o for o in imported if o.name.startswith(f'{ident}__{i:02d}')]
        if len(found)!=1:errors.append('part identity '+str(i));continue
        actual=[found[0].matrix_world@v.co for v in found[0].data.vertices]
        expected=[Vector((-v.co.x,v.co.y,v.co.z)) for v in source.data.vertices]
        if any(min((a-e).length for e in expected)>3e-5 for a in actual) or any(min((a-e).length for a in actual)>3e-5 for e in expected):errors.append('vertices '+str(i))
    for o in created:bpy.data.objects.remove(o,do_unlink=True)
    checks.append(dict(model=ident,status='PASS' if not errors else 'FAIL',errors=errors))
    exports.append(dict(model=ident,parts=len(parts),fbxBytes=fbx.stat().st_size))
    if errors:raise RuntimeError('FBX round trip '+ident+': '+str(errors))
report={'status':'PASS','blender':bpy.app.version_string,'models':len(ids),'exports':exports,'roundtrips':checks}
(ROOT/'C01ShipV76_QA/blender_exports.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('C01 V7.0 FBX/OBJ EXPORT PASS',len(ids))
