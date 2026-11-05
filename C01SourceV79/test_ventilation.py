import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

class VentilationLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'C01SourceV79/Data/ship_v79.json').read_text(encoding='utf8'))
        cls.plan=json.loads((ROOT/'Assets/C01ShipV79/Data/ventilation.json').read_text(encoding='utf8'))

    def test_upper_cabins_become_service_rooms_without_raising_ceilings(self):
        rooms=[z for z in self.data['zones'] if z['deck']==2 and z['kind']=='ventilation_service']
        self.assertEqual(len(rooms),12)
        self.assertTrue(all(z['height']==3 for z in rooms))
        self.assertFalse(any(z['deck']==2 and z['kind'] in ('cabin','bathroom') for z in self.data['zones']))

    def test_lower_cabins_remain(self):
        self.assertEqual(sum(z['deck']==1 and z['kind']=='cabin' for z in self.data['zones']),12)
        self.assertEqual(sum(z['deck']==1 and z['kind']=='bathroom' for z in self.data['zones']),12)

    def test_each_converted_room_contains_two_joined_duct_modules(self):
        ducts=[p for p in self.data['placements'] if p['id'].startswith('V79_VENT_')]
        self.assertEqual(len(ducts),24)
        for z in (z for z in self.data['zones'] if z['kind']=='ventilation_service'):
            pair=sorted((p for p in ducts if p['zone']==z['id']),key=lambda p:p['x'])
            self.assertEqual(len(pair),2,z['id'])
            self.assertEqual(pair[1]['x']-pair[0]['x'],3,z['id'])
            self.assertEqual(pair[0]['z'],pair[1]['z'])
        self.assertFalse(any(p['zone'] in {z['id'] for z in self.data['zones'] if z['kind']=='ventilation_service'} and p['model'] in ('P_Bed','P_Locker','P_Toilet','P_Shower','P_Sink') for p in self.data['placements']))

    def test_zone_links_resolve(self):
        ids={z['id'] for z in self.data['zones']}
        for link in self.data['links']:
            self.assertIn(link['a'],ids);self.assertIn(link['b'],ids)

    def test_shipwide_network_is_physically_connected(self):
        # This must not pass on room adjacency or decorative grilles alone.
        from network_audit import audit
        result=audit(self.data)
        self.assertEqual(result['status'],'PASS',
                         f"Niepołączone elementy: {result['physical_components']} sieci, {result['connected_outlets']}/{result['interior_zones']} wylotów")

if __name__=='__main__':unittest.main()
