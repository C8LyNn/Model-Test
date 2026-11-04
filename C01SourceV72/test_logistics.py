import json
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


class LogisticsLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'C01SourceV72/Data/ship_v72.json').read_text(encoding='utf8'))
        cls.zones = {z['id']: z for z in cls.data['zones']}

    def test_engine_room_is_below_engine_control(self):
        a = self.zones['L0_ENGINE_ROOM']['bounds']
        b = self.zones['L1_ENGINE_CONTROL']['bounds']
        self.assertEqual(a, b)

    def test_freight_sector_touches_freight_dock(self):
        cargo = self.zones['L0_CARGO']['bounds']
        dock = self.zones['L0_FREIGHT_DOCK']['bounds']
        self.assertEqual(cargo[1], dock[0])
        self.assertLess(max(cargo[2], dock[2]), min(cargo[3], dock[3]))

    def test_food_reserve_is_closer_to_galley_than_cargo(self):
        food = self.zones['L0_FOOD_RESERVE']['waypoint'][0]
        cargo = self.zones['L0_CARGO']['waypoint'][0]
        galley = self.zones['L2_N_SUPPORT_03']['waypoint'][0]
        self.assertLess(abs(food-galley), abs(cargo-galley))

    def test_food_and_hydroponics_share_the_same_longitudinal_section(self):
        self.assertEqual(self.zones['L0_FOOD_RESERVE']['bounds'][:2],
                         self.zones['L0_HYDROPONICS']['bounds'][:2])

    def test_each_sector_contains_its_assigned_equipment(self):
        by_zone = {name: [] for name in ('L0_ENGINE_ROOM', 'L0_PURIFICATION', 'L0_HYDROPONICS', 'L0_CARGO', 'L0_FOOD_RESERVE')}
        for p in self.data['placements']:
            if p['zone'] in by_zone and p['category'] == 'Props':
                by_zone[p['zone']].append(p)
        for name, prefix, count in (('L0_ENGINE_ROOM', 'P_Reactor', 2),
                                    ('L0_PURIFICATION', 'P_Purifier', 4),
                                    ('L0_HYDROPONICS', 'P_Plant', 40),
                                    ('L0_CARGO', 'P_Crate', 4),
                                    ('L0_FOOD_RESERVE', 'P_Crate', 4)):
            items = by_zone[name]
            self.assertEqual(len(items), count, name)
            x0,x1,z0,z1 = self.zones[name]['bounds']
            self.assertTrue(all(p['model'].startswith(prefix) and x0 < p['x'] < x1
                                and z0 < p['z'] < z1 for p in items), name)

    def test_audit_detects_an_intentional_duplicate(self):
        sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools/v5_dependencies'))
        from validate_ship_v5 import collision_audit
        data = deepcopy(self.data)
        item = deepcopy(next(p for p in data['placements'] if p['id'] == 'L0_ENGINE_ROOM_CORE_REACTOR_0'))
        item['id'] = 'QA_INTENTIONAL_DUPLICATE'
        data['placements'].append(item)
        result = collision_audit(data)
        self.assertEqual(result['status'], 'FAIL')
        self.assertGreater(result['penetrations'], 0)
        self.assertTrue(any('QA_INTENTIONAL_DUPLICATE' in hit for hit in result['examples']))
        (ROOT / 'C01ShipV72_QA/collision_positive_control.json').write_text(json.dumps(result, indent=2), encoding='utf8')

    def test_architecture_and_gate_geometry_are_unchanged(self):
        old = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
        before = {p['id']: p for p in old['placements']}
        after = {p['id']: p for p in self.data['placements']}
        self.assertEqual(set(before), set(after))
        for ident, p in before.items():
            if p['id'].startswith(('L0_ENGINE_ROOM_CORE_REACTOR_', 'L0_HYDROPONICS_PLANT_',
                                   'L0_CARGO_CRATE_', 'L0_FOOD_RESERVE_CRATE_')):
                continue
            q = after[ident]
            for key in ('model', 'category', 'x', 'y', 'z', 'yaw'):
                self.assertEqual(p[key], q[key], (ident, key))
        gates = {g['id']: g for g in self.data['gates']}
        for g in old['gates']:
            for key in ('x', 'y', 'z', 'yaw', 'width', 'height', 'leaves', 'buttons'):
                self.assertEqual(g[key], gates[g['id']][key], (g['id'], key))


if __name__ == '__main__':
    unittest.main()
