import copy, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Tools'))
from build_ship import build
from validate_ship import floor_polygons
from ship_geometry import polygon_area

class ExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship = build()
        cls.zones = {z['id']: z for z in cls.ship['zones']}

    def test_six_side_corridors_are_nine_metres_long_and_three_wide(self):
        for side in ['N', 'S']:
            for index in range(1, 4):
                b = self.zones[f'X{side}{index}']['bounds']
                self.assertEqual((b[1]-b[0], b[3]-b[2]), (3, 9))

    def test_main_corridor_and_stern_keep_the_same_three_metre_width(self):
        for zid in ['MAIN_W', 'MAIN_M', 'MAIN_E', 'D1', 'D2']:
            b = self.zones[zid]['bounds']
            self.assertEqual(b[3]-b[2], 3)
        b = self.zones['STERN']['bounds']
        self.assertEqual(b[1]-b[0], 3)

    def test_body_and_cabins_expand_with_unscaled_three_metre_modules(self):
        self.assertEqual(self.ship['body'], [0, 45, 0, 33])
        for zone in self.ship['zones']:
            if zone['kind'] == 'cabin':
                b = zone['bounds']
                self.assertEqual((b[1]-b[0], b[3]-b[2]), (6, 9))
        self.assertEqual(len(self.ship['doors']), 36)
        self.assertEqual(sum(p['module']=='P_Engine' for p in self.ship['placements']), 5)

    def test_expanded_deck_has_full_1845_square_metre_coverage(self):
        self.assertAlmostEqual(sum(polygon_area(poly) for _, poly in floor_polygons(self.ship)), 1845, places=4)

    def test_configured_lengths_keep_door_sockets_on_the_three_metre_grid(self):
        for length in [3, 6, 9, 12]:
            for door in build(length)['doors']:
                self.assertEqual(door['x'] % 3, 0)
                self.assertEqual(door['z'] % 3, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
