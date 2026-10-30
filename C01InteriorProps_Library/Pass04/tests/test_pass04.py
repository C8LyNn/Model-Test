"""C01-03 PASS04 catalog integrity tests. No Blender, Unity, or mesh QA simulation."""
import copy, hashlib, importlib.util, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pass04",HERE/"capture_pass04.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class TestPass04(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=p.load()
    def test_all_thirtysix_present(self):
        self.assertEqual(len(p.validate(self.data)),36)
    def test_all_original_before_digests_immutable(self):
        for a in p.validate(self.data):
            for role in ("blend","fbx"):
                h=a["before"][role+"_sha256"]
                self.assertTrue(h is None or p.H64.fullmatch(h))
    def test_prior_independent_failures_remain_blocked(self):
        failures={a["code"] for a in p.validate(self.data) if a["independent_qa"]["status"].startswith("FAIL")}
        self.assertEqual(failures,p.P0)
    def test_not_approved_by_static_receipt(self):
        for a in p.validate(self.data):
            self.assertEqual(a["release_status"],"BLOCKED")
            self.assertIsNone(a["independent_qa"]["signed_after_fbx_sha256"])
    def test_release_without_qa_rejected(self):
        altered=copy.deepcopy(self.data)
        altered["assets"][0]["release_status"]="APPROVED"
        with self.assertRaises(ValueError):p.validate(altered)
    def test_fake_byte_hash_rejected(self):
        altered=copy.deepcopy(self.data)
        altered["assets"][0]["after_candidate"]["fbx_sha256"]="0"*64
        with self.assertRaises(ValueError):p.validate(altered)
    def test_p19_qa_fail_cannot_be_reset_without_signed_evidence(self):
        altered=copy.deepcopy(self.data)
        fail=next(a for a in altered["assets"] if a["code"]=="P19-05")
        fail["independent_qa"]["status"]="PASS"
        with self.assertRaises(ValueError):p.validate(altered)
    def test_lfs_pointers_do_not_count_as_files(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"asset.blend"
            path.write_bytes(b"version https://git-lfs.github.com/spec/v1\n")
            self.assertEqual(p.inspect(Path(d),"asset.blend","blend")["status"],"UNHYDRATED_LFS")
    def test_real_blender_header_and_sha(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"asset.blend"
            content=b"BLENDER-v-original-real-bytes"
            path.write_bytes(content)
            rec=p.inspect(Path(d),"asset.blend","blend")
            self.assertEqual(rec["sha256"],hashlib.sha256(content).hexdigest())
            self.assertEqual(rec["status"],"BYTE_SHA256_VERIFIED_NOT_TOPOLOGY_QA")
    def test_ascii_fbx_not_binary(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"asset.fbx"
            path.write_bytes(b"; FBX 7.4.0 project file\n")
            self.assertEqual(p.inspect(Path(d),"asset.fbx","fbx")["status"],"NOT_BINARY_FBX")
    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):p.inspect(Path(d),"../secrets.blend","blend")
    def test_future_producer_commit_not_same_as_baseline_for_fixed_assets(self):
        a=next(x for x in p.validate(self.data) if x["code"]=="P19-07")
        self.assertNotEqual(a["before"]["producer_commit"],a["after_candidate"]["producer_commit"])

if __name__=="__main__":unittest.main()
