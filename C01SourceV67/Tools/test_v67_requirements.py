import unittest
import grid_layout
import scene_data_v6

class NewShipRequirements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=grid_layout.build()
        cls.data=scene_data_v6.build()
    def test_sectors_are_six_tiles_across(self):
        sectors=[z for z in self.plan['zones'] if z['deck']==1 and z['kind']=='sector']
        self.assertEqual(len(sectors),6)
        for z in sectors: self.assertEqual(z['z1']-z['z0'],6,z['id'])
        self.assertEqual(self.plan['body_bounds'],[0,42,5,24])
    def test_normal_rooms_are_one_tile_tall(self):
        for z in self.data['zones']:
            if z['kind'] in ('core','void','exterior'): continue
            self.assertEqual(z['height'],3,z['id'])
        self.assertEqual(self.plan['elevations'],[-3.4,0,3.4])
    def test_core_atria_are_four_tiles_tall(self):
        for name in ('L0_BRIDGE','L0_STERN'):
            core=next(z for z in self.data['zones'] if z['id']==name)
            self.assertEqual(core['height'],12,name)
        for side in ('BRIDGE','STERN'):
            floors=[p for p in self.data['placements'] if p['category']=='Floors' and p['deck']==2 and p['zone']=='L2_'+side]
            full=(16 if side=='BRIDGE' else 8)*19
            self.assertGreater(len(floors),0,side+' must have accessible landings')
            self.assertLess(len(floors),full//2,side+' must be open to the atrium')
    def test_level_two_has_varied_chase_obstacles_and_open_path(self):
        obstacles=[p for p in self.data['placements'] if p['category']=='ChaseObstacles' and p['deck']==2]
        self.assertGreaterEqual(len(obstacles),8)
        self.assertGreaterEqual(len({p['model'] for p in obstacles}),2)
        self.assertFalse(any(g['deck']==2 and g.get('airlock') in ('L2_D1','L2_D2') for g in self.data['gates']))

if __name__=='__main__':unittest.main()
