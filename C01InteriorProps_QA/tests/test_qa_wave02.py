import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qa_wave02 import expected_ids, inventory

class TestWave02(unittest.TestCase):
    def test_all_36(self):
        self.assertEqual(len(expected_ids()), 36)
        self.assertEqual(len(set(x[0] for x in expected_ids())), 36)
    def test_wave_counts(self):
        self.assertEqual(sum(x[2] == "W01" for x in expected_ids()), 16)
        self.assertEqual(sum(x[2] == "W02" for x in expected_ids()), 20)
    def test_empty_blocked(self):
        self.assertTrue(all(x["status"] == "BLOCKED" for x in inventory({})))
    def test_lfs_is_not_blend(self):
        x = inventory({"branches":{"C01-15":[{"path":"Assets/X/P15-01.blend","size":131}]}})[0]
        self.assertEqual(x["blend"], "LFS_POINTER_ONLY")
    def test_actual_binary_still_not_approved(self):
        files = [{"path":f"Assets/X/P15-01.{ext}","size":90000} for ext in ("blend","fbx","prefab")]
        x = inventory({"branches":{"C01-15":files}})[0]
        self.assertEqual(x["status"], "BLOCKED")
        self.assertEqual(x["fbx"], "PRESENT_UNVALIDATED")
    def test_wave02_not_confused_with_wave01(self):
        rows = inventory({"branches":{"C01-15":[{"path":"P15-04.fbx","size":9000}]}})
        self.assertEqual(rows[0]["fbx"], "MISSING")
        self.assertEqual(rows[3]["fbx"], "PRESENT_UNVALIDATED")
    def test_previews_lfs(self):
        x = inventory({"branches":{"C01-19":[{"path":"P19-08_top.png","size":131}]}})[-1]
        self.assertEqual(x["preview"], "LFS_POINTER_ONLY")

if __name__ == "__main__":
    unittest.main()
