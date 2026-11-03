"""C01-03 Wave02 metadata tests — not Blender or Unity QA."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "Wave02" / "validate_wave02.py"
spec = importlib.util.spec_from_file_location("c01_wave02_validator", VALIDATOR)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Wave02CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = v.read_json(v.WAVE01)
        cls.cat = v.read_json(v.CATALOG)

    def test_exact_twenty_new_ids(self):
        self.assertEqual(len(self.cat["assets"]), 20)
        self.assertEqual(len({a["asset_id"] for a in self.cat["assets"]}), 20)

    def test_no_wave01_overlap(self):
        old = {a["asset_id"] for a in self.old["assets"]}
        self.assertFalse(old.intersection({a["asset_id"] for a in self.cat["assets"]}))

    def test_all_owned_by_production_threads(self):
        self.assertEqual({a["owner_thread"] for a in self.cat["assets"]},
                         {f"C01-{i}" for i in range(15,20)})

    def test_no_fake_dimensions_files_hashes_or_approval(self):
        for a in self.cat["assets"]:
            self.assertIsNone(a["target_dimensions_wdh_m"])
            self.assertIsNone(a["measured_dimensions_wdh_m"])
            self.assertIsNone(a["delivered_version"])
            self.assertIsNone(a["source_sha256"])
            self.assertIsNone(a["fbx_sha256"])
            self.assertEqual(a["files"], [])
            self.assertEqual(a["status"], "PLANNED")
            self.assertEqual(a["qa"]["status"], "NOT_RUN")

    def test_dependencies_exist_and_acyclic(self):
        self.assertEqual(v.audit(self.old, self.cat), [])

    def test_duplicate_id_rejected(self):
        x = copy.deepcopy(self.cat)
        x["assets"][0]["asset_id"] = x["assets"][1]["asset_id"]
        self.assertTrue(any("canonical ID" in e for e in v.audit(self.old, x)))

    def test_cross_wave_collision_rejected(self):
        x = copy.deepcopy(self.cat)
        x["assets"][0]["asset_id"] = "C01-P15-01"
        self.assertTrue(any("collision" in e for e in v.audit(self.old, x)))

    def test_unknown_dependency_rejected(self):
        x = copy.deepcopy(self.cat)
        x["assets"][0]["dependencies"] = ["C01-DOES-NOT-EXIST"]
        self.assertTrue(any("dependencies" in e for e in v.audit(self.old, x)))

    def test_cycle_rejected(self):
        x = copy.deepcopy(self.cat)
        x["assets"][0]["dependencies"] = [x["assets"][1]["asset_id"]]
        x["assets"][1]["dependencies"] = [x["assets"][0]["asset_id"]]
        self.assertTrue(any("cyclic" in e for e in v.audit(self.old, x)))

    def test_premature_approved_rejected(self):
        x = copy.deepcopy(self.cat)
        x["assets"][0]["status"] = "APPROVED"
        self.assertTrue(any("premature" in e for e in v.audit(self.old, x)))

    def test_missing_source_file_rejected(self):
        x = copy.deepcopy(self.cat)
        a = x["assets"][0]
        a["files"] = [{"role":"fbx", "path":"Assets/C01InteriorProps/MISSING.fbx",
                       "sha256":"0"*64, "size_bytes":1}]
        a["delivered_version"] = a["proposed_version"]
        self.assertTrue(any("missing physical" in e for e in v.audit(self.old, x)))

    def test_missing_release_is_exit_2(self):
        proc = subprocess.run([sys.executable, str(VALIDATOR), "release"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("BLOCKED", proc.stdout)


if __name__ == "__main__":
    unittest.main()
