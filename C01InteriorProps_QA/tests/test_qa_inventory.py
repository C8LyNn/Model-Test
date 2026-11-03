import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import qa_inventory as q
class TestInventory(unittest.TestCase):
    def test_16_assets_all_blocked_if_empty(self):
        with tempfile.TemporaryDirectory() as path:
            a=q.audit(Path(path));self.assertEqual(len(a),16)
            self.assertTrue(all(x['overall']=='BLOCKED' for x in a))
    def test_bare_manifest_cannot_pass(self):
        with tempfile.TemporaryDirectory() as path:
            r=Path(path);(r/'P15-01.asset.json').write_text(json.dumps({'asset_id':'P15-01','owner':'C01-15','version':'1','files':{}}))
            a=q.audit(r)[0];self.assertEqual(a['overall'],'BLOCKED')
            self.assertEqual(a['tests']['unity_import'],'NOT RUN')
    def test_mismatched_owner_fails(self):
        with tempfile.TemporaryDirectory() as path:
            r=Path(path);(r/'P15-01.asset.json').write_text(json.dumps({'asset_id':'P15-01','owner':'C01-99','version':'1','files':{}}))
            self.assertEqual(q.audit(r)[0]['overall'],'FAIL')
    def test_reject_path_escape(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):q.safe_path(Path(path),'../bad.fbx')
    def test_reject_fake_fbx(self):
        with tempfile.TemporaryDirectory() as path:
            r=Path(path);(r/'P15-01.fbx').write_bytes(b'not a real fbx')
            (r/'P15-01.asset.json').write_text(json.dumps({'asset_id':'P15-01','owner':'C01-15','version':'1','files':{'fbx':'P15-01.fbx'}}))
            self.assertEqual(q.audit(r)[0]['tests']['fbx_signature'],'FAIL')
if __name__=='__main__':unittest.main()
