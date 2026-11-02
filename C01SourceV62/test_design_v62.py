import json
import math
import unittest
from pathlib import Path

import design_v62


class DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = design_v62.build()

    def test_wall_band_alignment_for_different_start_elevations(self):
        # Adjacent original panels start at -0.4 and 0 m; their only visible
        # seam between 1 and 5 m must cross both walls at the same y=3 m.
        left = design_v62.stripe_centers(-.4, 6)
        right = design_v62.stripe_centers(0, 6)
        self.assertEqual([x for x in left if 1 < x < 5], [3.0])
        self.assertEqual([x for x in right if 1 < x < 5], [3.0])

    def test_wall_mesh_has_no_paint_bands_off_global_three_metre_grid(self):
        for item in self.data['walls']:
            for center in item['stripeCenters']:
                self.assertAlmostEqual(center / 3, round(center / 3), places=6)
                self.assertGreaterEqual(center + .06, item['y'] - 1e-6)
                self.assertLessEqual(center - .06, item['y'] + item['height'] + 1e-6)

    def test_every_lift_has_cabin_roof_sides_and_unobstructed_entry(self):
        self.assertEqual(len(self.data['lifts']), 4)
        base = json.loads((Path(__file__).resolve().parent.parent / 'Assets/C01ShipV6/Data/ship_v6.json').read_text(encoding='utf-8'))
        original = {l['id']: l for l in base['lifts']}
        gates = {g['id']: g for g in base['gates']}
        removed = set(self.data['removedLandingButtons'])
        self.assertEqual(len(removed), 12)
        for lift in self.data['lifts']:
            for landing in original[lift['id']]['landings']:
                self.assertIn(gates[landing]['buttons'][1], removed)
                self.assertNotIn(gates[landing]['buttons'][0], removed)
            bounds = original[lift['id']]['bounds']
            self.assertGreaterEqual((bounds[1] - bounds[0])/2 - lift['halfX'], .03999)
            self.assertGreaterEqual((bounds[3] - bounds[2])/2 - lift['halfZ'], .03999)
            self.assertGreaterEqual(lift['doorWidth'], 2.1, lift['id'])
            self.assertGreater(lift['roofHeight'], 2.4, lift['id'])
            self.assertLess(lift['buttonZ'], lift['halfZ'] - .08, lift['id'])
            panels = lift['panels']
            for role in ('side_s', 'side_n', 'back', 'roof'):
                self.assertTrue(any(p['role'] == role for p in panels), (lift['id'], role))
            for p in panels:
                self.assertTrue(all(v > 0 for v in p['size']), p)
                self.assertLessEqual(max(p['size'][0], p['size'][2]), 3.0, p)
                x, y, z = p['center']; sx, sy, sz = p['size']
                self.assertLessEqual(abs(x) + sx / 2, lift['halfX'] + .00001, p)
                self.assertLessEqual(abs(z) + sz / 2, lift['halfZ'] + .00001, p)
                if p['role'] == 'front':
                    overlap = min(z + sz/2, lift['doorMax']) - max(z - sz/2, lift['doorMin'])
                    self.assertLessEqual(overlap, 1e-6, p)
            for i, a in enumerate(panels):
                for b in panels[i+1:]:
                    overlap = [min(a['center'][k]+a['size'][k]/2, b['center'][k]+b['size'][k]/2) -
                               max(a['center'][k]-a['size'][k]/2, b['center'][k]-b['size'][k]/2) for k in range(3)]
                    self.assertFalse(all(d > .00001 for d in overlap), (a['id'], b['id'], overlap))

    def test_bridge_has_command_chair_consoles_and_forward_screen(self):
        props = self.data['bridge']
        self.assertEqual(sum(p['kind'] == 'captain' for p in props), 1)
        self.assertGreaterEqual(sum(p['kind'] == 'console' for p in props), 5)
        self.assertGreaterEqual(sum(p['kind'] == 'screen' for p in props), 3)
        chair = next(p for p in props if p['kind'] == 'captain')
        self.assertTrue(all(p['position'][0] < chair['position'][0] for p in props if p['kind'] == 'screen'))


if __name__ == '__main__':
    unittest.main()
