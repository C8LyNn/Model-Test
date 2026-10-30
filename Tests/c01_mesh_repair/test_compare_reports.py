import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
S=importlib.util.spec_from_file_location("c01_compare",ROOT/"Tools/c01_mesh_repair/compare_topology_reports.py")
mod=importlib.util.module_from_spec(S)
S.loader.exec_module(mod)


def sample(stage):
    obj={
        "object":"Body","parent":None,
        "local_aabb_xyz":[[0,0,0],[1,1,1]],"world_object_dimensions_xyz":[1,1,1],
        "material_slots":["Steel"],"uv_maps":[{"name":"UVMap"}],
        "transform":{"local_scale":[1,1,1],"local_rotation_euler":[0,0,0],
                     "matrix_world":[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]},
        "mesh_issues":{k:0 for k in mod.HARD+mod.CANDIDATES+("boundary_edges",)}
    }
    return {"schema":"C01-MESH-TOPOLOGY-1.0","asset_id":"P17-04","stage":stage,
            "source_sha256":"a"*64 if stage=="BEFORE" else "b"*64,
            "object_data":[obj],"exceptions_declared":[]}


class TestCompare(unittest.TestCase):
    def test_good_shape_still_requires_independent_review(self):
        r=mod.compare(sample("BEFORE"),sample("AFTER"),True)
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
        self.assertEqual(r["geometry_final_qa"],"NOT_APPROVED")
    def test_identical_hash_with_repair_claim_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["source_sha256"]=a["source_sha256"]
        self.assertIn("REPAIR_CLAIM_WITH_IDENTICAL_SOURCE_BYTES",mod.compare(a,b,True)["errors"])
    def test_hierarchy_changed_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["object"]="Renamed"
        self.assertIn("OBJECT_HIERARCHY_CHANGED",mod.compare(a,b)["errors"])
    def test_dimension_change_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["local_aabb_xyz"][1][0]=1.1
        self.assertIn("Body:LOCAL_AABB_XYZ_CHANGED",mod.compare(a,b)["errors"])
    def test_mesh_degenerate_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["mesh_issues"]["degenerate_faces"]=1
        self.assertIn("Body:PERSISTENT_DEGENERATE_FACES",mod.compare(a,b)["errors"])
    def test_open_surface_requires_review_not_fail(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["mesh_issues"]["boundary_edges"]=4
        r=mod.compare(a,b)
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
        self.assertTrue(any("OPEN_BOUNDARY" in x for x in r["review_items"]))
    def test_declared_exception_requires_review(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["mesh_issues"]["loose_edges"]=1
        b["exceptions_declared"]=[{"object":"Body","metric":"loose_edges",
            "classification":"INTENTIONAL_UNVERIFIED","reason":"fixture-only"}]
        r=mod.compare(a,b)
        self.assertEqual(r["status"],"REVIEW_REQUIRED")
        self.assertTrue(any("EXCEPTION_NOT_INDEPENDENTLY_APPROVED" in x for x in r["review_items"]))
    def test_uv_changed_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["uv_maps"]=[{"name":"NewUV"}]
        self.assertIn("Body:UV_MAP_NAMES_CHANGED",mod.compare(a,b)["errors"])
    def test_material_changed_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["object_data"][0]["material_slots"]=["Different"]
        self.assertIn("Body:MATERIAL_SLOTS_CHANGED",mod.compare(a,b)["errors"])
    def test_false_missing_hash_fails(self):
        a,b=sample("BEFORE"),sample("AFTER")
        b["source_sha256"]=None
        self.assertIn("SOURCE_HASH_MISSING",mod.compare(a,b)["errors"])


if __name__=="__main__":
    unittest.main()
