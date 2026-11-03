import copy, importlib.util, tempfile, unittest
from unittest import mock
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pass03", BASE / "validate_pass03.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class LedgerTests(unittest.TestCase):
    def test_exact_36(self):
        self.assertEqual(len(p.validate()), 36)
    def test_exact_six_first(self):
        self.assertEqual({a["code"] for a in p.validate() if a["priority"] == "P0"}, p.P0)
    def test_no_fake_after_source(self):
        for a in p.validate():
            self.assertIsNone(a["repair"]["commit"])
            self.assertIsNone(a["repair"]["blend_sha256"])
            self.assertIsNone(a["repair"]["fbx_sha256"])
            self.assertEqual(a["qa"]["status"], "NOT_RUN")
            self.assertEqual(a["release_status"], "BLOCKED")
    def test_before_digests_have_real_ci_provenance(self):
        for a in p.validate():
            b = a["baseline"]
            for role in ("blend", "fbx"):
                digest = b[role + "_sha256"]
                if digest is not None:
                    self.assertRegex(digest, r"^[0-9a-f]{64}$")
                    self.assertIn("byte_evidence", b)
                    self.assertIn("action_run_id", b["byte_evidence"])
                    self.assertEqual(b[role + "_byte_status"], "BYTE_SHA256_PASS_NOT_MESH_QA")
    def test_qa_cannot_be_skipped(self):
        a = p.validate()[0]
        a["release_status"] = "APPROVED"
        with mock.patch.object(p, "records", return_value=[a] + p.validate()[1:]):
            with self.assertRaises(ValueError):
                p.validate()
    def test_no_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                p.inspect(Path(tmp), "../escape.blend", "blend")
    def test_lfs_pointer_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "bad.blend"
            file.write_bytes(b"version https://git-lfs.github.com/spec/v1\n")
            self.assertEqual(p.inspect(Path(tmp), "bad.blend", "blend")["status"], "UNRESOLVED_LFS_POINTER")
    def test_real_hash_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "real.blend"
            file.write_bytes(b"BLENDER-v-original-byte-content")
            self.assertEqual(p.inspect(Path(tmp), "real.blend", "blend")["status"], "BYTE_SHA256_PASS_NOT_MESH_QA")

if __name__ == "__main__":
    unittest.main()
