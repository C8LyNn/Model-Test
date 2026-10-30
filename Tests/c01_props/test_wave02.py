"""C01-01 Wave02 contract tests: synthetic fixtures only, no Blender/Unity claims."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODULE=ROOT/"Tools/c01_props/validate_wave02.py"
spec=importlib.util.spec_from_file_location("validate_wave02",MODULE)
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
W2=json.loads((ROOT/"Docs/C01InteriorProps/prop_contract_wave02.json").read_text())
W1=json.loads((ROOT/"Docs/C01InteriorProps/prop_contract.json").read_text())

def sample(asset="P15-04"):
    ref=next(x for x in W2["assets"] if x["id"]==asset)
    return {
        "asset_id":asset,"contract_id":W2["contract_id"],"owner_thread":ref["owner"],
        "pivot_profile":ref["pivot_profile"],"mount_surface":ref["mount_surfaces"][0],
        "root_scale_xyz":[1,1,1],"root_rotation_euler_xyz":[0,0,0],
        "pivot_local_xyz_m":[0,0,0],"measured_wdh_m":ref["nominal_wdh_m"],
        "mesh_bounds_xyz_m":ref["reference_bounds_xyz_m"],"materials":ref["materials"],
        "children":ref["required_children"],"sockets":["SOCKET_MOUNT"]+ref["required_sockets"],
        "ports":ref.get("ports",[]),"triangle_count":120,
        "colliders":[{"type":"BoxCollider","child":"Body"}],
        "moving_parts":[{"name":"Pivot","pivot_local_xyz_m":[0,0,0]}],
        "swept_volume_evidence":"synthetic-only-test-fixture",
        "qa":{k:"NOT_RUN" for k in W2["qa_fields"]},"files":{}
    }

class ContractTests(unittest.TestCase):
    def check(self,m, root=None):
        return v.check_manifest(m,W2,root or ROOT)
    def test_contract_20_and_reserved_16(self):
        self.assertEqual(v.check_contract(W2,W1),[])
    def test_20_synthetic_manifest_shapes_are_valid_but_blocked(self):
        for a in W2["assets"]:
            with self.subTest(asset=a["id"]):
                r=self.check(sample(a["id"]))
                self.assertEqual(r["static"],"PASS",r)
                self.assertEqual(r["delivery"],"BLOCKED")
                self.assertEqual(r["approval"],"NOT_APPROVED")
    def test_wave01_not_replaced(self):
        bad=copy.deepcopy(W2);bad["extends_contract_id"]="C01-MAS-0.1"
        self.assertIn("INCOMPATIBLE_WAVE01_CONTRACT",v.check_contract(bad,W1))
    def test_duplicate_wave02_slot_rejected(self):
        bad=copy.deepcopy(W2);bad["assets"][0]["id"]=bad["assets"][1]["id"]
        self.assertIn("WAVE02_IDS_NOT_EXACTLY_20",v.check_contract(bad,W1))
    def test_elbow_wrong_port_is_rejected(self):
        bad=copy.deepcopy(W2);next(x for x in bad["assets"] if x["id"]=="P15-05")["ports"][0]["local_xyz_m"][0]=-.49
        self.assertIn("TRAY_CORNER_A_POSITION_MISMATCH",v.check_contract(bad,W1))
    def test_elbow_wrong_normal_is_rejected(self):
        bad=copy.deepcopy(W2);next(x for x in bad["assets"] if x["id"]=="P15-05")["ports"][0]["outward_normal"]=[1,0,0]
        self.assertIn("TRAY_CORNER_A_AXIS_MISMATCH",v.check_contract(bad,W1))
    def test_unsupported_material_rejected(self):
        bad=sample("P16-04");bad["materials"]=["M_NONEXISTENT"]
        self.assertIn("INVALID_MATERIALS",self.check(bad)["errors"])
    def test_missing_service_socket_rejected(self):
        bad=sample("P15-07");bad["sockets"]=["SOCKET_MOUNT"]
        self.assertIn("REQUIRED_SOCKETS_MISSING",self.check(bad)["errors"])
    def test_missing_moving_child_rejected(self):
        bad=sample("P17-06");bad["children"]=["Body"]
        self.assertIn("REQUIRED_CHILDREN_MISSING",self.check(bad)["errors"])
    def test_scale_prohibited(self):
        bad=sample("P18-06");bad["root_scale_xyz"]=[1,1,3]
        self.assertIn("NON_UNIT_SCALE",self.check(bad)["errors"])
    def test_dimension_override_requires_approval(self):
        bad=sample("P19-08");bad["measured_wdh_m"]=[1.5,.55,1.3]
        bad["mesh_bounds_xyz_m"]=v.bbox("floor",bad["measured_wdh_m"])
        self.assertIn("UNAPPROVED_DIMENSION_VARIANCE",self.check(bad)["errors"])
    def test_unverified_quality_labels_do_not_bypass_absent_files(self):
        bad=sample("P16-04");bad["qa"]={k:"PASS" for k in W2["qa_fields"]}
        self.assertEqual(self.check(bad)["approval"],"NOT_APPROVED")
        self.assertEqual(self.check(bad)["delivery"],"BLOCKED")
    def test_path_escape_rejected(self):
        bad=sample("P16-04")
        bad["files"]["fbx"]={"path":"../../etc/passwd","sha256":"0"*64}
        self.assertIn("PATH_TRAVERSAL_FBX",self.check(bad)["errors"])
    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"real.fbx").write_bytes(b"fake test bytes")
            bad=sample("P16-04")
            bad["files"]["fbx"]={"path":"real.fbx","sha256":"a"*64}
            self.assertIn("HASH_MISMATCH_FBX",self.check(bad,root)["errors"])
    def test_unhydrated_lfs_pointer_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            content=b"version https://git-lfs.github.com/spec/v1\noid sha256:123\nsize 123\n"
            (root/"model.blend").write_bytes(content)
            bad=sample("P16-04")
            bad["files"]["blend"]={"path":"model.blend","sha256":hashlib.sha256(content).hexdigest()}
            self.assertIn("UNHYDRATED_LFS_BLEND",self.check(bad,root)["warnings"])
            self.assertEqual(self.check(bad,root)["delivery"],"BLOCKED")
    def test_unknown_asset_rejected(self):
        bad=sample();bad["asset_id"]="P15-99"
        self.assertIn("UNKNOWN_ASSET",self.check(bad)["errors"])

    def test_fake_fbx_with_valid_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            content=b"not a real FBX just text"
            (root/"bad.fbx").write_bytes(content)
            bad=sample("P16-04")
            bad["files"]["fbx"]={"path":"bad.fbx","sha256":hashlib.sha256(content).hexdigest()}
            self.assertIn("INVALID_FBX_SIGNATURE",self.check(bad,root)["errors"])

    def test_claimed_independent_review_never_automatically_approved(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            m=sample("P16-04")
            payloads={
                "blend": b"BLENDER"+b"0"*60,
                "fbx": b"Kaydara FBX Binary  "+b"0"*60,
                "unity_prefab": b"%YAML 1.1"+b"0"*60,
                "preview_front": bytes((137,80,78,71,13,10,26,10))+b"0"*60,
                "preview_side": bytes((137,80,78,71,13,10,26,10))+b"1"*60,
                "preview_top": bytes((137,80,78,71,13,10,26,10))+b"2"*60,
            }
            for k,body in payloads.items():
                file=root/(k+".bin")
                file.write_bytes(body)
                m["files"][k]={"path":file.name,"sha256":hashlib.sha256(body).hexdigest()}
            m["qa"]={k:"PASS" for k in W2["qa_fields"]}
            m["independent_review"]={"owner":"C01-02","report_url":"https://example.invalid/claimed","source_commit_sha":"f"*40}
            r=self.check(m,root)
            self.assertEqual(r["static"],"PASS",r)
            self.assertEqual(r["delivery"],"READY_FOR_INDEPENDENT_QA")
            self.assertEqual(r["approval"],"QA_REFERENCE_PRESENT_UNVERIFIED")

if __name__=="__main__":
    unittest.main()
