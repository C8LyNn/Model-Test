import unittest
import grid_layout
import scene_data_v6

class ShipHeightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=scene_data_v6.build()
        cls.plan=grid_layout.build()

    def test_corridors_are_one_tile(self):
        corridors=[z for z in self.data['zones'] if z['kind']=='corridor']
        self.assertEqual(len(corridors),27)
        for z in corridors:
            b=z['bounds']
            self.assertAlmostEqual(min(b[1]-b[0],b[3]-b[2]),3,msg=z['id'])

    def test_room_clear_heights(self):
        for z in self.data['zones']:
            if z['kind'] in ('void','exterior'): continue
            expected=6 if z['deck']==0 or z['kind']=='sector' else 3
            self.assertAlmostEqual(z['height'],expected,msg=z['id'])

    def test_deck_clearances_and_lift_stops(self):
        floors=[d['y'] for d in self.data['decks']]
        self.assertEqual(floors,[-6.4,0,3.4])
        for lift in self.data['lifts']:
            self.assertEqual(lift['elevations'],floors,lift['id'])

    def test_gates_fit_deck_height(self):
        for g in self.data['gates']:
            self.assertLessEqual(g['height'],6 if g['deck']==0 else 3,g['id'])

    def test_sector_access_reaches_duct_and_uses_short_ladder(self):
        for zone in (z for z in self.data['zones'] if z['kind']=='sector'):
            fixtures=[p for p in self.data['placements'] if p['zone']==zone['id']]
            stairs=sorted((p for p in fixtures if p['model']=='P_Stair_3m'),key=lambda p:p['y'])
            platform=next(p for p in fixtures if p['model']=='P_Mezzanine_3m')
            ladder=[p for p in fixtures if p['model']=='P_Ladder_3m']
            vents=sorted((p for p in fixtures if p['model']=='P_Vent_3m'),key=lambda p:p['x'])
            self.assertEqual(len(stairs),2,zone['id']);self.assertEqual(len(ladder),1,zone['id']);self.assertEqual(len(vents),2,zone['id'])
            self.assertAlmostEqual(stairs[-1]['x']+3,platform['x'],msg=zone['id'])
            self.assertAlmostEqual(stairs[-1]['y']+1.5,platform['y'],msg=zone['id'])
            self.assertAlmostEqual(platform['x']+3,vents[0]['x'],msg=zone['id'])
            self.assertAlmostEqual(platform['y'],vents[0]['y'],msg=zone['id'])

    def test_bridge_and_stern_have_complete_upper_deck_surfaces(self):
        by_id={p['id']:p for p in self.data['placements']}
        for ident in ('F_2_-10_15','F_2_45_12'):
            self.assertIn(ident,by_id)
            self.assertAlmostEqual(by_id[ident]['y'],3.4,msg=ident)

if __name__=='__main__': unittest.main()
