import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / 'Tools/c01_props/mesh_stream_audit.py'
SPEC = importlib.util.spec_from_file_location('c01_stream_audit', SRC)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)

OBJ_VALID = '''v 0 0 0\nv 1 0 0\nv 0 1 0\nvt 0 0\nvt 1 0\nvt 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\n'''


def gltf(attrs=None, counts=None):
    attrs = attrs or {'POSITION':0, 'NORMAL':1, 'TEXCOORD_0':2}
    types = ['VEC3','VEC3','VEC2']
    counts = counts or [3,3,3]
    return {'asset': {'version':'2.0'},'meshes':[{'primitives':[{'attributes':attrs, 'mode':4}]}],
            'accessors':[{'count':c,'type':t} for c,t in zip(counts,types)]}


class MeshStreamAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, body):
        p = self.root/name
        p.write_text(body)
        return p

    def test_obj_complete(self):
        self.assertEqual(audit.inspect(self.write('good.obj', OBJ_VALID))['static'], 'PASS')

    def test_obj_missing_uv(self):
        bad=OBJ_VALID.replace('f 1/1/1 2/2/1 3/3/1','f 1//1 2//1 3//1')
        self.assertIn('LINE_8:MISSING_TEXCOORD_0',audit.inspect(self.write('no_uv.obj',bad))['errors'])

    def test_obj_missing_normal(self):
        bad=OBJ_VALID.replace('f 1/1/1 2/2/1 3/3/1','f 1/1 2/2 3/3')
        self.assertIn('LINE_8:MISSING_NORMAL',audit.inspect(self.write('no_n.obj',bad))['errors'])

    def test_obj_negative_indices(self):
        bad=OBJ_VALID.replace('f 1/1/1 2/2/1 3/3/1','f -3/-3/-1 -2/-2/-1 -1/-1/-1')
        self.assertEqual(audit.inspect(self.write('neg.obj',bad))['static'],'PASS')

    def test_obj_zero_area(self):
        bad=OBJ_VALID.replace('v 0 1 0','v 2 0 0')
        self.assertIn('LINE_8:DEGENERATE_TRIANGLE',audit.inspect(self.write('flat.obj',bad))['errors'])

    def test_obj_out_of_range(self):
        bad=OBJ_VALID.replace('f 1/1/1','f 900/1/1')
        self.assertIn('LINE_8:INVALID_INDEX_0',audit.inspect(self.write('out.obj',bad))['errors'])

    def test_gltf_complete(self):
        self.assertEqual(audit.inspect(self.write('good.gltf',json.dumps(gltf())))['static'],'PASS')

    def test_gltf_missing_uv(self):
        doc=gltf({'POSITION':0,'NORMAL':1})
        self.assertIn('MESH_0_PRIMITIVE_0:MISSING_TEXCOORD_0',audit.inspect(self.write('no_uv.gltf',json.dumps(doc)))['errors'])

    def test_gltf_mismatched_stream(self):
        doc=gltf(counts=[3,4,3])
        self.assertIn('MESH_0_PRIMITIVE_0:STREAM_COUNT_MISMATCH',audit.inspect(self.write('mismatch.gltf',json.dumps(doc)))['errors'])

    def test_missing_file(self):
        self.assertIn('FILE_MISSING',audit.inspect(self.root/'missing.obj')['errors'])

    def test_unsupported_fbx(self):
        self.assertIn('UNSUPPORTED_FORMAT',audit.inspect(self.write('x.fbx','fake'))['errors'])

    def test_invalid_json(self):
        self.assertEqual(audit.inspect(self.write('bad.gltf','{'))['static'],'FAIL')

if __name__=='__main__':
    unittest.main()
