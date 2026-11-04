import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent.parent
ROUTES=[('GYM',9,33,54,57),('ENGINE_CONTROL',51,75,30,33),('MED',93,117,54,57)]


class SectorRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'C01SourceV74/Data/ship_v74.json').read_text(encoding='utf8'))
        cls.byid={p['id']:p for p in cls.data['placements']}

    def test_catwalks_cross_three_sectors_on_the_upper_deck(self):
        for name,x0,x1,z0,z1 in ROUTES:
            zone=next(z for z in self.data['zones'] if z['id']=='L2_'+name)
            self.assertEqual(zone['kind'],'gallery')
            tiles=[p for p in self.data['placements'] if p['id'].startswith('L2_ROUTE_'+name+'_FLOOR_')]
            self.assertEqual(len(tiles),8,name)
            self.assertEqual({p['x'] for p in tiles},set(range(x0,x1,3)))
            self.assertTrue(all(p['z']==z0 and p['y']==3.4 for p in tiles))

    def test_each_sector_has_two_operable_gates_and_guardrails(self):
        gates={g['id']:g for g in self.data['gates']}
        for name,x0,x1,z0,z1 in ROUTES:
            for label,x in (('IN',x0),('OUT',x1-3)):
                gate=gates['L2_ROUTE_'+name+'_'+label]
                self.assertEqual(gate['x'],x)
                self.assertEqual(gate['height'],2.6)
                self.assertEqual(len(gate['leaves']),8)
                self.assertEqual(len(gate['buttons']),2)
            rails=[p for p in self.data['placements'] if p['id'].startswith('L2_ROUTE_'+name+'_RAIL_')]
            self.assertEqual(len(rails),10,name)

    def test_central_barriers_require_sector_detours(self):
        for x in (18,60,102):
            barrier=self.byid['L2_ROUTE_BULKHEAD_'+str(x)]
            self.assertEqual((barrier['x'],barrier['y'],barrier['z'],barrier['yaw']),(x,3.4,42,-90))
        for name,_,_,_,_ in ROUTES:
            obstacles=[p for p in self.data['placements'] if p['id'].startswith('L2_ROUTE_'+name+'_OBSTACLE_')]
            self.assertEqual(len(obstacles),3,name)

    def test_original_engine_and_cargo_alignment_remains(self):
        zones={z['id']:z for z in self.data['zones']}
        self.assertEqual(zones['L0_ENGINE_ROOM']['bounds'],zones['L1_ENGINE_CONTROL']['bounds'])
        self.assertEqual(zones['L0_CARGO']['bounds'],zones['L1_CARGO']['bounds'])

    def test_catwalk_coverage_detects_a_missing_tile(self):
        from copy import deepcopy
        if __package__:
            from .audit_catwalks import audit
        else:
            from audit_catwalks import audit
        self.assertEqual(audit(self.data)['status'],'PASS')
        damaged=deepcopy(self.data)
        damaged['placements']=[p for p in damaged['placements'] if p['id']!='L2_ROUTE_GYM_FLOOR_4']
        result=audit(damaged)
        self.assertEqual(result['status'],'FAIL')
        self.assertTrue(any(g['sector']=='GYM' and g['x']==21 for g in result['examples']))

    def test_geometry_audit_detects_a_duplicate_railing(self):
        from copy import deepcopy
        import sys
        sys.path.insert(0,str(ROOT/'C01SourceV71/Tools/v5_dependencies'))
        from validate_ship_v5 import collision_audit
        damaged=deepcopy(self.data)
        rail=deepcopy(self.byid['L2_ROUTE_GYM_RAIL_4']);rail['id']='QA_DUPLICATE_RAIL';damaged['placements'].append(rail)
        result=collision_audit(damaged,1)
        self.assertEqual(result['status'],'FAIL')
        self.assertTrue(any('QA_DUPLICATE_RAIL' in hit for hit in result['examples']))


if __name__=='__main__':unittest.main()
