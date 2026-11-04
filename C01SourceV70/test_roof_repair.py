import copy
import json
import unittest
from pathlib import Path
from roof_repair import build

ROOT=Path(__file__).resolve().parent.parent

class RoofRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
        cls.plan=build(copy.deepcopy(cls.data))
        cls.byid={p['id']:p for p in cls.data['placements']}

    def test_sector_roof_top_matches_corridor_without_lowering_ceiling(self):
        selected=[p for p in self.data['placements'] if p['category']=='Ceilings' and abs(p['y']-6.2)<1e-6]
        self.assertTrue(selected)
        self.assertEqual({p['id'] for p in selected},{p['id'] for p in self.plan['roofs']})
        for roof in self.plan['roofs']:
            self.assertAlmostEqual(roof['bottom'],6.0,msg=roof['id'])
            self.assertAlmostEqual(roof['top'],6.6,msg=roof['id'])

    def test_every_roof_tile_is_covered_except_for_real_obstructions(self):
        self.assertEqual(self.plan['audit']['uncoveredTiles'],0)
        self.assertAlmostEqual(self.plan['audit']['uncoveredArea'],0,places=5)
        self.assertEqual(self.plan['audit']['capPenetrations'],0)
        self.assertEqual(self.plan['audit']['raisedRoofPenetrations'],0)

    def test_roof_shapes_use_reusable_unscaled_variants(self):
        variants={}
        for roof in self.plan['roofs']:
            shape=json.dumps([roof['model'],roof['caps']],sort_keys=True)
            if roof['variant'] in variants:self.assertEqual(variants[roof['variant']],shape)
            else:variants[roof['variant']]=shape
        self.assertLess(len(variants),len(self.plan['roofs']))

if __name__=='__main__':unittest.main()
