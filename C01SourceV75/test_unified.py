import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent.parent
class UnifiedSectorData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'C01SourceV75/Data/ship_platforms.json').read_text(encoding='utf8'))
        cls.data=json.loads((ROOT/'C01SourceV75/Data/ship_v75.json').read_text(encoding='utf8'))

    def test_six_spanning_owners_by_footprint(self):
        zones=self.data['zones']
        sectors=[z for z in zones if z.get('spansDecks')]
        self.assertEqual(len(sectors),6)
        for z in sectors:
            self.assertEqual((z['deck'],z['floor'],z['height']),(1,0,6))
            self.assertEqual(len([u for u in zones if u['bounds']==z['bounds'] and u['deck']==2 and u['kind'] in ('gallery','void')]),0)

    def test_unchanged_modules_and_valid_owner_references(self):
        old={p['id']:p for p in self.old['placements']};new={p['id']:p for p in self.data['placements']}
        self.assertEqual(old.keys(),new.keys())
        for ident,p in old.items():
            for key in ('model','x','y','z','yaw','deck'):
                self.assertEqual(p[key],new[ident][key],(ident,key))
        ids={z['id'] for z in self.data['zones']}
        for g in self.data['gates']:
            for z in g['zones']:self.assertIn(z,ids,(g['id'],z))
        for link in self.data['links']:
            self.assertIn(link['a'],ids);self.assertIn(link['b'],ids)

    def test_upper_gallery_objects_share_lower_owner(self):
        for name in ('GYM','ENGINE_CONTROL','MED'):
            parts=[p for p in self.data['placements'] if p['id'].startswith('L2_ROUTE_'+name+'_')]
            self.assertGreater(len(parts),40)
            self.assertTrue(all(p['zone']=='L1_'+name for p in parts))

    def test_every_sector_has_two_upper_entrances_and_a_platform(self):
        plan=json.loads((ROOT/'Assets/C01ShipV75/Data/platforms.json').read_text(encoding='utf8'))
        self.assertEqual(len(plan['gates']),6)
        gates=self.data['gates'];parts=self.data['placements']
        for owner in ('L1_GYM','L1_TECH','L1_LAB','L1_ENGINE_CONTROL','L1_MED','L1_CARGO'):
            upper=[g for g in gates if g['deck']==2 and owner in g['zones']]
            lower=[g for g in gates if g['deck']==1 and owner in g['zones']]
            floors=[p for p in parts if p['deck']==2 and p['zone']==owner and p['category']=='Floors']
            self.assertEqual(len(upper),2,owner);self.assertGreaterEqual(len(lower),1,owner);self.assertEqual(len(floors),8,owner)

if __name__=='__main__':unittest.main()
