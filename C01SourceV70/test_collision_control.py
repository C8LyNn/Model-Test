"""Prove the penetration auditor detects an injected overlapping module."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

import assembly_v70

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'C01SourceV68/Tools/v5_dependencies'))
from validate_ship_v5 import collision_audit


class CollisionPositiveControl(unittest.TestCase):
    def test_duplicate_wall_is_detected(self):
        data = assembly_v70.build()
        wall = next(p for p in data['placements'] if p['model'] == 'W3_H3000_V70_OneSeam')
        duplicate = deepcopy(wall)
        duplicate['id'] = 'QA_INTENTIONAL_OVERLAP'
        data['placements'].append(duplicate)
        result = collision_audit(data, 0)
        self.assertEqual(result['status'], 'FAIL')
        self.assertGreater(result['penetrations'], 0)
        self.assertTrue(any('QA_INTENTIONAL_OVERLAP' in hit for hit in result['examples']))
        (ROOT / 'C01ShipV70_QA/collision_positive_control.json').write_text(
            json.dumps(result, indent=2), encoding='utf8')


if __name__ == '__main__':
    unittest.main()
