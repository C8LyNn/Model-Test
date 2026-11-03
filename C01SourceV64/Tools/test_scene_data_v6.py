import unittest
import scene_data_v6


class SceneDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = scene_data_v6.build()

    def test_full_grid_footprint_and_levels(self):
        self.assertEqual(self.data["body"], [0, 126, 0, 90])
        self.assertEqual(self.data["shipBounds"], [-48, 174, -6, 96])
        self.assertEqual([d["y"] for d in self.data["decks"]], [-6.4, 0, 3.4])

    def test_all_objects_are_independent_instances(self):
        placements = self.data["placements"]
        self.assertGreater(len(placements), 1000)
        self.assertEqual(len(placements), len({p["id"] for p in placements}))
        self.assertGreater(len([p for p in placements if p["model"] == "W3_H3000"]), 100)

    def test_room_doors_and_cabins(self):
        data = self.data
        cabins = [z for z in data["zones"] if z["kind"] == "cabin"]
        self.assertEqual(len(cabins), 24)
        for c in cabins:
            self.assertEqual((c["bounds"][1]-c["bounds"][0], c["bounds"][3]-c["bounds"][2]), (9, 9))
            self.assertTrue(any(c["id"] in g["zones"] for g in data["gates"]), c["id"])
            fixtures=[p for p in data["placements"] if p["zone"]==c["id"]]
            self.assertEqual(sum(p["model"]=="P_Bed" for p in fixtures),4,c["id"])
            self.assertGreaterEqual(sum(p["model"]=="P_Locker" for p in fixtures),4,c["id"])

    def test_four_lifts(self):
        lifts = self.data["lifts"]
        self.assertEqual(len(lifts), 4)
        self.assertEqual(len([l for l in lifts if l["id"].startswith("STERN_CARGO")]), 2)
        self.assertTrue(all(len(l["landings"]) == 3 for l in lifts))

    def test_training_and_medical_equipment(self):
        gym=[p["model"] for p in self.data["placements"] if p["zone"]=="L1_GYM"]
        med=[p["model"] for p in self.data["placements"] if p["zone"]=="L1_MED"]
        self.assertNotIn("P_Bed",gym)
        self.assertNotIn("P_MedBed",gym)
        self.assertIn("P_Treadmill",gym)
        self.assertIn("P_ExamScanner",med)
        self.assertEqual(med.count("P_MedBed"),2)

    def test_no_wall_across_middle_of_a_sector(self):
        sector = next(z for z in self.data["zones"] if z["id"] == "L1_GYM")
        x0,x1,z0,z1 = sector["bounds"]
        walls = [p for p in self.data["placements"] if p["category"] == "Walls" and
                 p["y"] <= 1 < p["y"] + 3 and
                 x0+.2 < p["x"] < x1-3.2 and z0+.2 < p["z"] < z1-3.2]
        self.assertEqual(walls, [])


if __name__ == "__main__":
    unittest.main()
