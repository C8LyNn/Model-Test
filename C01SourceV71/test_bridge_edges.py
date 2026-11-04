"""Contract for bridge lift positions in 3 m cells."""
import json
from pathlib import Path
from copy import deepcopy
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


class BridgeEdges(unittest.TestCase):
    def test_lifts_are_symmetric_at_sides(self):
        data = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
        lifts = {item['id']: item for item in data['lifts']}
        a, b = lifts['BRIDGE_PASSENGER'], lifts['BRIDGE_PASSENGER_N']
        self.assertEqual(a['x'], b['x'])
        self.assertAlmostEqual(a['z'] + b['z'], 87.0)
        self.assertLessEqual(a['z'], 22.5)
        self.assertGreaterEqual(b['z'], 64.5)
        for lift in (a, b):
            self.assertEqual(len(lift['landings']), 3)
            self.assertEqual(len(lift['waypoints']), 3)

    def test_command_and_outer_stations_form_a_symmetric_layout(self):
        data = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
        items = {item['id']: item for item in data['placements']}
        command = items['BRIDGE_COMMAND_TABLE']
        self.assertAlmostEqual(command['z'] + .9, 43.5)
        for left, right, half_width in (('BRIDGE_PORT_OPS', 'BRIDGE_STARBOARD_OPS', .9),
                                       ('BRIDGE_PORT_OPS_CHAIR', 'BRIDGE_STARBOARD_OPS_CHAIR', .6)):
            self.assertEqual(items[left]['x'], items[right]['x'])
            self.assertAlmostEqual(items[left]['z'] + items[right]['z'] + 2 * half_width, 87)

    def test_all_lift_landing_gates_follow_the_new_positions(self):
        data = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
        gates = {item['id']: item for item in data['gates']}
        for lift in data['lifts']:
            if not lift['id'].startswith('BRIDGE_PASSENGER'):
                continue
            for floor, gate_id in enumerate(lift['landings']):
                gate = gates[gate_id]
                self.assertAlmostEqual(gate['z'] + 1.5, lift['z'])
                self.assertAlmostEqual(gate['x'], lift['x'] - 1.5)
                self.assertEqual(gate['floor'], floor)

    def test_geometry_audit_detects_an_injected_overlap(self):
        sys.path.insert(0, str(ROOT / 'C01SourceV71/Tools/v5_dependencies'))
        from validate_ship_v5 import collision_audit
        data = json.loads((ROOT / 'C01SourceV71/Data/ship_v71.json').read_text(encoding='utf8'))
        wall = next(p for p in data['placements'] if p['model'] == 'W3_H3000_V70_OneSeam')
        duplicate = deepcopy(wall)
        duplicate['id'] = 'QA_INTENTIONAL_OVERLAP'
        data['placements'].append(duplicate)
        result = collision_audit(data)
        self.assertEqual(result['status'], 'FAIL')
        self.assertGreater(result['penetrations'], 0)
        self.assertTrue(any('QA_INTENTIONAL_OVERLAP' in hit for hit in result['examples']))
        (ROOT / 'C01ShipV71_QA/collision_positive_control.json').write_text(json.dumps(result, indent=2), encoding='utf8')


if __name__ == '__main__':
    unittest.main()
