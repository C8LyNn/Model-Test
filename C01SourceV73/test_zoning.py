import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ZoningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT/'C01SourceV73/Data/ship_v73.json').read_text(encoding='utf8'))
        cls.zones = {z['id']: z for z in cls.data['zones']}

    def test_cargo_rooms_are_vertically_aligned(self):
        self.assertEqual(self.zones['L0_CARGO']['bounds'], self.zones['L1_CARGO']['bounds'])
        self.assertEqual(self.zones['L0_ENGINE_ROOM']['bounds'], self.zones['L1_ENGINE_CONTROL']['bounds'])

    def test_cargo_support_is_near_cargo_and_workshop_near_technical_sector(self):
        for room, sector, label in (('L1_S_SUPPORT_11','L1_CARGO','EWIDENCJA LADUNKU'),
                                    ('L1_S_SUPPORT_12','L1_CARGO','NARZEDZIA LADUNKOWE'),
                                    ('L1_S_SUPPORT_03','L1_TECH','WARSZTAT'),
                                    ('L1_S_SUPPORT_04','L1_TECH','CZESCI ZAMIENNE')):
            support, target = self.zones[room], self.zones[sector]
            self.assertEqual(support['label'],label)
            self.assertLess(target['bounds'][0],support['waypoint'][0])
            self.assertGreater(target['bounds'][1],support['waypoint'][0])

    def test_equipment_remains_in_its_respective_sector(self):
        for zone, model, expected in (('L1_CARGO','P_Crate',4),('L1_TECH','P_Server',4)):
            bounds=self.zones[zone]['bounds']
            items=[p for p in self.data['placements'] if p['zone']==zone and p['category']=='Props']
            self.assertEqual(len(items),expected,zone)
            self.assertTrue(all(p['model']==model and bounds[0]<p['x']<bounds[1]
                                and bounds[2]<p['z']<bounds[3] for p in items),zone)

    def test_architecture_and_gate_positions_are_preserved(self):
        old=json.loads((ROOT/'C01SourceV72/Data/ship_v72.json').read_text(encoding='utf8'))
        before={p['id']:p for p in old['placements']};after={p['id']:p for p in self.data['placements']}
        self.assertEqual(set(before),set(after))
        for ident,p in before.items():
            if ident.startswith(('L1_CARGO_CRATE_','L1_TECH_TECH_SERVER_')):continue
            for key in ('model','category','x','y','z','yaw'):
                self.assertEqual(p[key],after[ident][key],(ident,key))
        gates={g['id']:g for g in self.data['gates']}
        for g in old['gates']:
            for key in ('x','y','z','yaw','width','height','leaves','buttons'):
                self.assertEqual(g[key],gates[g['id']][key],(g['id'],key))

    def test_audit_detects_an_intentional_overlap(self):
        from copy import deepcopy
        sys.path.insert(0,str(ROOT/'C01SourceV71/Tools/v5_dependencies'))
        from validate_ship_v5 import collision_audit
        data=deepcopy(self.data)
        item=deepcopy(next(p for p in data['placements'] if p['id']=='L1_CARGO_CRATE_0'))
        item['id']='QA_DUPLICATE_CRATE';data['placements'].append(item)
        result=collision_audit(data)
        self.assertEqual(result['status'],'FAIL')
        self.assertTrue(any('QA_DUPLICATE_CRATE' in hit for hit in result['examples']))
        out=ROOT/'C01ShipV73_QA/collision_positive_control.json';out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result,indent=2),encoding='utf8')


if __name__ == '__main__':
    unittest.main()
