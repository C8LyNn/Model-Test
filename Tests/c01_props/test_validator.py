import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('c01_validator',ROOT/'Tools/c01_props/validate_props.py')
v=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)
CAT=json.loads((ROOT/'Docs/C01InteriorProps/prop_contract.json').read_text())

def fixture(asset_id='P19-04'):
    a=next(x for x in CAT['assets'] if x['id']==asset_id)
    prof=a['default_mount']
    m=dict(asset_id=asset_id,contract_id=CAT['contract_id'],owner_thread=a['owner'],version='0.1.0',
      mesh_name=asset_id.replace('-','_')+'_MESH',measured_wdh_m=a['nominal_wdh_m'],
      pivot_profile=prof,mount_surface=a['allowed_mount_surfaces'][0] if prof=='rail' else prof,
      local_bounds_xyz_m=v.bounds_for(prof,a['nominal_wdh_m']),pivot_local_xyz_m=[0,0,0],
      root_scale_xyz=[1,1,1],root_local_rotation_euler_xyz=[0,0,0],
      mount_socket_name='SOCKET_MOUNT',
      mount_normal_local_xyz=[0,1,0] if prof=='rail' else CAT['pivot_profiles'][prof]['socket_normal'],
      triangle_count=120,materials=['M_C01_METAL_GRY'],
      colliders=[dict(type='BoxCollider',child='Body')],moving_parts=[],
      submesh_children=[],material_variants=[],
      qa={k:'NOT_RUN' for k in ('blender','fbx_roundtrip','unity_import','clearance','independent')},files={})
    rule=a['required_part_rule']
    if rule in ('cover','hinge_lever','wheels'):m['moving_parts']=[dict(name='MovingPart',pivot_local_xyz_m=[0,0,0])]
    if rule in ('mattress_child','screen_child','emissive_child'):m['submesh_children']=['DistinctChild']
    if rule=='material_variants_3':m['material_variants']=['green','amber','red']
    return m

class TestC01PropValidation(unittest.TestCase):
    def result(self,m):return v.review(m,CAT,Path(tempfile.gettempdir()))
    def test_catalog_has_exactly_16_unique_ids(self):
        assets=CAT['assets'];self.assertEqual(len(assets),16);self.assertEqual(len(set(a['id'] for a in assets)),16)
    def test_all_skeleton_manifest_shapes_structurally_valid_but_delivery_blocked(self):
        for a in CAT['assets']:
            with self.subTest(id=a['id']):
                result=self.result(fixture(a['id']))
                self.assertEqual(result['static'],'PASS',result)
                self.assertEqual(result['delivery'],'BLOCKED')
    def test_bad_scale_rejected(self):
        m=fixture();m['root_scale_xyz']=[3,3,3]
        self.assertIn('NON_UNIT_SCALE',self.result(m)['errors'])
    def test_wall_socket_and_bounds(self):
        m=fixture('P17-02');m['mount_normal_local_xyz']=[0,0,1]
        self.assertIn('MOUNT_NORMAL_WRONG',self.result(m)['errors'])
    def test_nominal_dimension_override_needs_approval(self):
        m=fixture();m['measured_wdh_m']=[1,.6,.95]
        m['local_bounds_xyz_m']=v.bounds_for('floor',m['measured_wdh_m'])
        self.assertIn('DIMENSION_OVERRIDE_UNAPPROVED',self.result(m)['errors'])
    def test_approved_dimension_exception(self):
        m=fixture();m['measured_wdh_m']=[1,.6,.95]
        m['local_bounds_xyz_m']=v.bounds_for('floor',m['measured_wdh_m'])
        m['dimension_exception']={'reason':'seat clearance','c01_01_approval_ref':'ISSUE-42'}
        self.assertEqual(self.result(m)['static'],'PASS')
    def test_missing_separate_part_rejected(self):
        m=fixture('P18-03');m['moving_parts']=[]
        self.assertIn('REQUIRED_MOVING_CHILD_MISSING',self.result(m)['errors'])
    def test_wrong_status_colors_rejected(self):
        m=fixture('P16-03');m['material_variants']=['red']
        self.assertIn('STATUS_VARIANTS_MISSING',self.result(m)['errors'])
    def test_invalid_mesh_name_rejected(self):
        m=fixture();m['mesh_name']='Whatever'
        self.assertIn('MESH_NAME_NONSTANDARD',self.result(m)['errors'])
    def test_material_limit_rejected(self):
        m=fixture();m['materials']=['A','B','C','D','E']
        self.assertIn('MATERIAL_SLOTS_INVALID',self.result(m)['errors'])
    def test_path_escape_rejected(self):
        m=fixture();m['files']['fbx']={'path':'../../secrets','sha256':'0'*64}
        self.assertIn('PATH_OUTSIDE_ROOT',self.result(m)['errors'])
    def test_bad_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a.blend').write_text('test');m=fixture()
            m['files']['blend']={'path':'a.blend','sha256':'0'*64}
            self.assertIn('HASH_MISMATCH_BLEND',v.review(m,CAT,p)['errors'])
    def test_no_evidence_cannot_be_declared_delivered(self):
        m=fixture();m['qa']={k:'PASS' for k in m['qa']}
        self.assertEqual(self.result(m)['delivery'],'BLOCKED')
    def test_nonexistent_owner(self):
        m=fixture();m['owner_thread']='C01-15'
        self.assertIn('WRONG_OWNER',self.result(m)['errors'])

if __name__=='__main__':unittest.main()
