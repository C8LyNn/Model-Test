"""Export ONE existing C01 prop collection from Blender to .blend and .fbx.
Run inside Blender, not standard CPython:
blender --background authored.blend --python Tools/c01_props/blender_export_prop.py -- --asset-id P18-01 --output-dir ./C01PropExports
Requires collection C01_PROP_P18_01; never fabricates meshes.
FBX→Unity orientation must still be verified by real import.
"""
import argparse
from pathlib import Path
import sys
import bpy

def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument('--asset-id',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    opt=p.parse_args(args)
    if len(opt.asset_id)!=6 or opt.asset_id[0]!='P' or opt.asset_id[3]!='-' or not opt.asset_id[1:3].isdigit() or not opt.asset_id[4:6].isdigit():
        raise ValueError('Expected asset ID P15-01 through P19-04')
    name='C01_PROP_'+opt.asset_id.replace('-','_')
    coll=bpy.data.collections.get(name)
    if coll is None:raise RuntimeError('Missing authored collection '+name)
    objects=list(coll.all_objects)
    meshes=[o for o in objects if o.type=='MESH' and len(o.data.polygons)>0]
    if not meshes:raise RuntimeError('No actual mesh geometry in '+name)
    if bpy.context.scene.unit_settings.system!='METRIC':raise RuntimeError('Blender units must be Metric')
    if abs(bpy.context.scene.unit_settings.scale_length-1)>1e-6:raise RuntimeError('Blender unit scale must be 1')
    opt.output_dir.mkdir(parents=True,exist_ok=True)
    safe=opt.asset_id.replace('-','_')
    blend=opt.output_dir/f'{safe}.blend'
    fbx=opt.output_dir/f'{safe}.fbx'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        if obj.type in {'MESH','EMPTY'}:obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False)
    print('C01_SOURCE_EXPORT_COMPLETED',opt.asset_id,blend,fbx)
if __name__=='__main__':main()
