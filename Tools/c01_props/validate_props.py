#!/usr/bin/env python3
"""C01-01 prop-manifest static QA. Standard library only; NEVER claims Blender/Unity PASS."""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_CONTRACT = HERE.parents[2] / 'Docs/C01InteriorProps/prop_contract.json'
STATUSES = {'PASS', 'FAIL', 'NOT_RUN', 'BLOCKED'}
REQUIRED_EVIDENCE = ('blend', 'fbx', 'prefab')

def bounds_for(profile, wdh):
    w,d,h = wdh
    if profile == 'floor': return [[-w/2,0,-d/2],[w/2,h,d/2]]
    if profile == 'wall': return [[-w/2,-h/2,-d],[w/2,h/2,0]]
    if profile == 'ceiling': return [[-w/2,-h,-d/2],[w/2,0,d/2]]
    if profile == 'rail': return [[0,-h/2,-d/2],[w,h/2,d/2]]
    raise ValueError(f'Unknown profile: {profile}')

def finite3(vec):
    return isinstance(vec,list) and len(vec)==3 and all(type(v) in (int,float) and math.isfinite(v) for v in vec)

def close3(a,b,tol):
    return finite3(a) and finite3(b) and all(abs(float(x)-float(y))<=tol for x,y in zip(a,b))

def review(manifest,contract,root):
    errors=[]; warnings=[]
    def fail(code): errors.append(code)
    ids={a['id']:a for a in contract['assets']}
    asset_id=manifest.get('asset_id')
    ref=ids.get(asset_id)
    if ref is None:
        fail('UNKNOWN_ASSET_ID')
        return dict(asset_id=asset_id,static='FAIL',delivery='BLOCKED',errors=errors,warnings=warnings)
    if manifest.get('contract_id')!=contract['contract_id']:fail('WRONG_CONTRACT')
    if manifest.get('owner_thread')!=ref['owner']:fail('WRONG_OWNER')
    if manifest.get('version') is None:fail('VERSION_MISSING')
    if not manifest.get('mesh_name','').startswith(asset_id.replace('-','_')):fail('MESH_NAME_NONSTANDARD')
    dims=manifest.get('measured_wdh_m')
    if not finite3(dims) or any(v<=0 for v in (dims if finite3(dims) else [])):fail('DIMENSIONS_INVALID')
    else:
        delta=max(abs(v-u) for v,u in zip(dims,ref['nominal_wdh_m']))
        if delta>contract['limits']['max_approved_variance_from_nominal_m']:
            exception=manifest.get('dimension_exception') or {}
            if not exception.get('reason') or not exception.get('c01_01_approval_ref'):fail('DIMENSION_OVERRIDE_UNAPPROVED')
    profile=manifest.get('pivot_profile')
    if profile not in contract['pivot_profiles']:fail('PIVOT_PROFILE_INVALID')
    if profile!=ref['default_mount'] and profile not in ref['allowed_mount_surfaces']:fail('PIVOT_PROFILE_UNEXPECTED')
    if manifest.get('mount_surface') not in ref['allowed_mount_surfaces']:fail('MOUNT_SURFACE_INVALID')
    if finite3(dims) and all(x>0 for x in dims) and profile in contract['pivot_profiles']:
        ideal=bounds_for(profile,dims)
        actual=manifest.get('local_bounds_xyz_m')
        if not (isinstance(actual,list) and len(actual)==2 and close3(actual[0],ideal[0],contract['limits']['dimension_tolerance_m']) and close3(actual[1],ideal[1],contract['limits']['dimension_tolerance_m'])):fail('BOUNDS_DO_NOT_MATCH_PIVOT_CONVENTION')
    if not close3(manifest.get('root_scale_xyz'),[1,1,1],contract['limits']['scale_tolerance']):fail('NON_UNIT_SCALE')
    if not close3(manifest.get('root_local_rotation_euler_xyz'),[0,0,0],.01):fail('NON_IDENTITY_ROOT_ROTATION')
    if not close3(manifest.get('pivot_local_xyz_m'),[0,0,0],contract['limits']['local_pivot_tolerance_m']):fail('PIVOT_OFFSET')
    if not manifest.get('mount_socket_name'):fail('MOUNT_SOCKET_MISSING')
    if not finite3(manifest.get('mount_normal_local_xyz')) and profile!='rail':fail('MOUNT_NORMAL_INVALID')
    elif profile in ('wall','ceiling','floor') and not close3(manifest.get('mount_normal_local_xyz'),contract['pivot_profiles'][profile]['socket_normal'],.001):fail('MOUNT_NORMAL_WRONG')
    tri=manifest.get('triangle_count')
    if type(tri)!=int or tri<=0:fail('TRIANGLE_COUNT_MISSING')
    mats=manifest.get('materials')
    if not isinstance(mats,list) or not 1<=len(mats)<=min(4,ref['max_materials']) or len(set(mats))!=len(mats):fail('MATERIAL_SLOTS_INVALID')
    colliders=manifest.get('colliders')
    if not isinstance(colliders,list) or not colliders:fail('COLLIDERS_MISSING')
    elif any(c.get('type') not in ('BoxCollider','CapsuleCollider','SphereCollider','MeshCollider') or not c.get('child') for c in colliders if isinstance(c,dict)):fail('COLLIDER_INVALID')
    parts=manifest.get('moving_parts')
    if not isinstance(parts,list):fail('MOVING_PARTS_MISSING')
    if ref['required_part_rule'] in ('cover','hinge_lever','wheels') and (not isinstance(parts,list) or not parts or not all('pivot_local_xyz_m' in p and finite3(p['pivot_local_xyz_m']) for p in parts if isinstance(p,dict))):fail('REQUIRED_MOVING_CHILD_MISSING')
    if ref['required_part_rule'] in ('mattress_child','screen_child','emissive_child') and not manifest.get('submesh_children'):fail('REQUIRED_SEPARATE_SUBMESH_MISSING')
    if ref['required_part_rule']=='material_variants_3' and set(manifest.get('material_variants',[]))!={'green','amber','red'}:fail('STATUS_VARIANTS_MISSING')
    qa=manifest.get('qa',{})
    if not isinstance(qa,dict) or any(qa.get(k) not in STATUSES for k in ('blender','fbx_roundtrip','unity_import','clearance','independent')):fail('QA_FIELDS_INVALID')
    files=manifest.get('files',{})
    file_ready=True
    if not isinstance(files,dict):files={};fail('FILES_INVALID');file_ready=False
    for k in REQUIRED_EVIDENCE+('preview_front','preview_side','preview_top'):
        item=files.get(k)
        if not isinstance(item,dict) or not isinstance(item.get('path'),str) or not item.get('path') or not item.get('sha256'):
            file_ready=False;warnings.append('MISSING_EVIDENCE_'+k.upper());continue
        candidate=(root/item['path']).resolve()
        if not candidate.is_relative_to(root.resolve()):fail('PATH_OUTSIDE_ROOT');file_ready=False;continue
        if not candidate.is_file():warnings.append('FILE_NOT_PRESENT_'+k.upper());file_ready=False;continue
        digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest.lower()!=item['sha256'].lower():fail('HASH_MISMATCH_'+k.upper());file_ready=False
    if not isinstance(qa,dict) or any(qa.get(k)!='PASS' for k in ('blender','fbx_roundtrip','unity_import','clearance','independent')):file_ready=False
    return dict(asset_id=asset_id,static='PASS' if not errors else 'FAIL',delivery='READY_FOR_REVIEW' if not errors and file_ready else 'BLOCKED',errors=errors,warnings=warnings)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('manifest',type=Path)
    p.add_argument('--contract',type=Path,default=DEFAULT_CONTRACT)
    p.add_argument('--root',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    contract=json.loads(args.contract.read_text(encoding='utf-8'))
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    result=review(manifest,contract,args.root or args.manifest.parent)
    output=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output+'\n',encoding='utf-8')
    print(output)
    raise SystemExit(0 if result['static']=='PASS' else 1)
if __name__=='__main__':main()
