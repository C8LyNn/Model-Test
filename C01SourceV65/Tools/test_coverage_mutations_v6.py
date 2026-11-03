import unittest
import scene_data_v6
import audit_floor_v6
import audit_ceiling_v6
from validate_ship_v5 import solids


class CoverageMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=scene_data_v6.build()

    def without(self, ident):
        result=dict(self.data)
        result["placements"]=[p for p in self.data["placements"] if p["id"]!=ident]
        self.assertEqual(len(result["placements"]),len(self.data["placements"])-1,ident)
        return result

    def test_missing_floor_tile_is_detected(self):
        report=audit_floor_v6.audit(self.without("F_1_5_14"))
        self.assertEqual(report["status"],"FAIL")
        self.assertGreater(report["missing_area"],1)

    def test_missing_ceiling_tile_is_detected(self):
        report=audit_ceiling_v6.audit(self.without("C2_5_14"))
        self.assertEqual(report["status"],"FAIL")
        self.assertGreater(report["missing_area"],1)

    def test_missing_external_wall_is_detected(self):
        def closed_at_sample(data):
            return any(s["lo"]<1.5<s["hi"] and s["x0"]<4.5<s["x1"] and s["z0"]<-3<s["z1"]
                       for s in solids(data) if s["category"] in ("Walls","Nodes","GateFrames","GateLeaves"))
        self.assertTrue(closed_at_sample(self.data))
        self.assertFalse(closed_at_sample(self.without("W_H_3_-3_-0.4")))

if __name__=="__main__":
    unittest.main()
