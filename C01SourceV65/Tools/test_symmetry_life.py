import unittest
import grid_layout
import scene_data_v6

class SymmetricShipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=grid_layout.build();cls.data=scene_data_v6.build()

    def test_body_has_one_tile_centre_and_equal_sides(self):
        self.assertEqual(self.plan['body_bounds'],[0,42,-1,30])
        for z in self.plan['zones']:
            if z['kind']=='corridor' and z['id'].endswith('_MAIN'):
                self.assertEqual((z['z0'],z['z1']),(14,15))

    def test_primary_rooms_have_reflected_partners(self):
        zones=[z for z in self.plan['zones'] if not z.get('parent')]
        keys={(z['deck'],z['kind'],z['x0'],z['x1'],z['z0'],z['z1']) for z in zones}
        for z in zones:
            key=(z['deck'],z['kind'],z['x0'],z['x1'],29-z['z1'],29-z['z0'])
            self.assertIn(key,keys,z['id'])

    def test_bathrooms_are_mirrored(self):
        baths=[z for z in self.plan['zones'] if z['kind']=='bathroom']
        keys={(z['deck'],z['x0'],z['x1'],z['z0'],z['z1']) for z in baths}
        for z in baths:
            self.assertIn((z['deck'],z['x0'],z['x1'],29-z['z1'],29-z['z0']),keys,z['id'])

    def test_every_gate_has_a_reflected_counterpart(self):
        gates=self.data['gates']
        keys={(g['deck'],g['x'],g['z'],g['yaw'],g['width']) for g in gates}
        for g in gates:
            z=87-g['z'] if g['yaw']==0 else 87-g['z']-g['width']
            self.assertIn((g['deck'],g['x'],round(z,7),g['yaw'],g['width']),keys,g['id'])

    def test_wall_node_and_floor_placements_reflect_across_axis(self):
        for category in ('Walls','Nodes','Floors'):
            items=[p for p in self.data['placements'] if p['category']==category]
            keys={(p['x'],p['y'],p['z'],p['yaw'],p['deck'],p['model'] if category!='Floors' else '') for p in items}
            for p in items:
                z=87-p['z'] if category=='Nodes' or (category=='Walls' and p['yaw']==0) else 84-p['z']
                key=(p['x'],p['y'],round(z,7),p['yaw'],p['deck'],p['model'] if category!='Floors' else '')
                self.assertIn(key,keys,p['id'])

    def test_engine_positions_are_mirrored(self):
        engines=[p for p in self.data['placements'] if p['model']=='P_Engine']
        keys={(p['x'],p['y'],p['z']) for p in engines}
        for p in engines:self.assertIn((p['x'],p['y'],round(87-p['z'],7)),keys,p['id'])

    def test_lift_shafts_have_mirrored_partners(self):
        lifts=self.plan['lifts'];keys={(l['kind'],l['x0'],l['x1'],l['z0'],l['z1']) for l in lifts}
        for l in lifts:
            self.assertIn((l['kind'],l['x0'],l['x1'],29-l['z1'],29-l['z0']),keys,l['id'])
        self.assertEqual(sum(l['kind']=='cargo' for l in lifts),2)

    def test_essential_crew_services_are_in_the_plan(self):
        roles={z.get('role') for z in self.plan['zones']}
        self.assertTrue({'GALLEY','MESS','CREW_LOUNGE','LAUNDRY','FOOD_STORAGE','WATER_CONTROL','WORKSHOP','MEDICAL_SUPPLIES'}<=roles)
        self.assertIn('L0_FOOD_RESERVE',{z['id'] for z in self.plan['zones']})

    def test_living_services_have_usable_equipment(self):
        specs={z['id']:z for z in self.plan['zones']}
        for role,model,minimum in (('MESS','P_MessTable',4),('MESS','P_LoungeBench',4),('GALLEY','P_GalleyCounter',2),('LAUNDRY','P_LaundryUnit',4)):
            room=next(z for z in specs.values() if z.get('role')==role)
            count=sum(p['zone']==room['id'] and p['model']==model for p in self.data['placements'])
            self.assertGreaterEqual(count,minimum,role)

    def test_existing_decks_and_cabins(self):
        self.assertEqual(self.plan['elevations'],[-6.4,0,3.4])
        cabins=[z for z in self.plan['zones'] if z['kind']=='cabin']
        self.assertEqual(len(cabins),24)
        self.assertTrue(all((z['x1']-z['x0'],z['z1']-z['z0'])==(3,3) for z in cabins))

if __name__=='__main__':unittest.main()
