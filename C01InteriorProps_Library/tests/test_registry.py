"""Unit tests for catalog logic only. NOT Blender or Unity tests."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "C01InteriorProps_Library" / "tools"))
import registry


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = registry.load()

    def test_all_sixteen_present(self):
        self.assertEqual(len(self.catalog["assets"]), 16)

    def test_owners_and_ids_unique(self):
        self.assertEqual(len({a["asset_id"] for a in self.catalog["assets"]}), 16)
        self.assertEqual({a["owner_thread"] for a in self.catalog["assets"]},
                         {"C01-15", "C01-16", "C01-17", "C01-18", "C01-19"})

    def test_planned_is_not_delivered(self):
        for a in self.catalog["assets"]:
            self.assertEqual(a["status"], "PLANNED")
            self.assertIsNone(a["delivered_version"])
            self.assertEqual(a["files"], [])
            self.assertEqual(a["qa"]["status"], "NOT_RUN")

    def test_audit_has_no_metadata_errors(self):
        errors, pending = registry.audit(self.catalog)
        self.assertEqual(errors, [])
        self.assertEqual(len(pending), 16)

    def test_release_is_blocked(self):
        proc = subprocess.run([sys.executable, str(registry.Path(registry.__file__)), "release"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("BLOCKED", proc.stdout)

    def test_traversal_rejected(self):
        for path in ("../secret.blend", "/etc/passwd", "Assets\\evil.blend", "a/../x.fbx"):
            with self.assertRaises(ValueError):
                registry.safe_path(path)

    def test_duplicate_id_is_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["assets"][0]["asset_id"] = data["assets"][1]["asset_id"]
        errors, _ = registry.audit(data)
        self.assertTrue(errors)

    def test_wrong_owner_is_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["assets"][0]["owner_thread"] = "C01-19"
        errors, _ = registry.audit(data)
        self.assertTrue(any("owner mismatch" in err for err in errors))

    def test_invalid_dimensions_are_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["assets"][0]["suggested_dimensions_wdh_m"] = [1, 0, 1]
        errors, _ = registry.audit(data)
        self.assertTrue(any("dimensions" in err for err in errors))

    def test_no_premature_approved(self):
        data = copy.deepcopy(self.catalog)
        data["assets"][0]["status"] = "APPROVED"
        errors, _ = registry.audit(data)
        self.assertTrue(any("premature" in err for err in errors))
        self.assertTrue(any("QA" in err for err in errors))

    def test_missing_file_does_not_exist(self):
        data = copy.deepcopy(self.catalog)
        data["assets"][0]["files"].append({
            "role": "fbx", "path": "Assets/DefinitelyNotARealFile.fbx",
            "sha256": "0" * 64, "size_bytes": 1
        })
        data["assets"][0]["delivered_version"] = "0.1.0"
        errors, _ = registry.audit(data)
        self.assertTrue(any("does not exist" in err for err in errors))

    def test_registration_refuses_overwrite_and_uses_hash(self):
        with tempfile.TemporaryDirectory(prefix=".c01registry-test-", dir=ROOT) as tmp:
            folder = Path(tmp)
            dummy = folder / "temporary.blend"
            dummy.write_bytes(b"BLENDER-v-test-bytes")
            cat = folder / "catalog.json"
            cat.write_text(json.dumps(copy.deepcopy(self.catalog)), encoding="utf-8")
            rel = dummy.relative_to(ROOT).as_posix()
            class Args:
                asset = "C01-P15-01"
                role = "blend"
                path = rel
            with patch.object(registry, "CATALOG", cat):
                registry.register(Args)
                modified = json.loads(cat.read_text(encoding="utf-8"))
                a = modified["assets"][0]
                self.assertEqual(a["files"][0]["sha256"],
                                 hashlib.sha256(dummy.read_bytes()).hexdigest())
                self.assertEqual(a["status"], "IN PRODUCTION")
                self.assertEqual(a["delivered_version"], "0.1.0")
                with self.assertRaises(ValueError):
                    registry.register(Args)

    def test_bad_hash_detected(self):
        with tempfile.TemporaryDirectory(prefix=".c01registry-test-", dir=ROOT) as tmp:
            path = Path(tmp) / "a.fbx"
            path.write_bytes(b"Kaydara FBX Binary  \x00\x1a\x00test")
            entry = {"role": "fbx", "path": path.relative_to(ROOT).as_posix(),
                     "sha256": "0" * 64, "size_bytes": path.stat().st_size}
            errors = []
            registry.check_one_file(entry, errors)
            self.assertTrue(any("SHA-256 mismatch" in x for x in errors))

    def test_lfs_pointer_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix=".c01registry-test-", dir=ROOT) as tmp:
            path = Path(tmp) / "a.blend"
            path.write_bytes(b"version https://git-lfs.github.com/spec/v1\n")
            entry = {"role": "blend", "path": path.relative_to(ROOT).as_posix(),
                     "sha256": registry.sha256(path), "size_bytes": path.stat().st_size}
            errors = []
            registry.check_one_file(entry, errors)
            self.assertTrue(any("LFS pointer" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
