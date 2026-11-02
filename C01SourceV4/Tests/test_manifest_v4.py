import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))
from validate_ship_v4 import PROJECT
PATH=PROJECT/'Assets/C01ShipV4/Data/ship_v4.json'

class MultideckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else None
    def test_manifest_exists(self):self.assertIsNotNone(self.data,'Three-deck ship has not been generated')
    def ship(self):
        if self.data is None:self.skipTest('manifest not generated yet')
        return self.data
    def test_confirmed_square_dimensions_and_heights(self):
        d=self.ship();self.assertEqual(d['body'],[0,63,0,45]);self.assertEqual(d['unit'],3)
        cabins=[z for z in d['zones'] if z['kind']=='cabin'];self.assertEqual(len(cabins),24)
        for z in cabins:
            b=z['bounds'];self.assertEqual([b[1]-b[0],b[3]-b[2],z['height']],[9,9,6])
        baths=[z for z in d['zones'] if z['kind']=='bathroom'];self.assertEqual(len(baths),24)
        for z in baths:
            b=z['bounds'];self.assertEqual(sorted([b[1]-b[0],b[3]-b[2]]),[3,6])
        for z in d['zones']:
            if z['kind']=='sector':self.assertEqual(z['height'],12)
            if z['kind']=='corridor':self.assertEqual(min(z['bounds'][1]-z['bounds'][0],z['bounds'][3]-z['bounds'][2]),3);self.assertEqual(z['height'],6)
    def test_every_cabin_has_four_beds_and_eight_lockers(self):
        d=self.ship()
        for zone in [z for z in d['zones'] if z['kind']=='cabin']:
            local=[p for p in d['placements'] if p['zone']==zone['id']]
            self.assertEqual(sum(p['model']=='P_Bed' for p in local),4,zone['id'])
            self.assertEqual(sum(p['model']=='P_Locker' for p in local),8,zone['id'])
    def test_gym_medical_control_and_lower_spaces(self):
        d=self.ship();zids={z['id'] for z in d['zones']}
        self.assertTrue({'L0_ENGINE_ROOM','L0_PURIFICATION','L0_HYDROPONICS','L0_CARGO','L0_EVAC_HANGAR','L1_ENGINE_CONTROL'}<=zids)
        gym=[p for p in d['placements'] if p['zone']=='L1_GYM'];self.assertFalse(any('Bed' in p['model'] for p in gym));self.assertGreaterEqual(len(gym),6)
        med=[p for p in d['placements'] if p['zone']=='L1_MED'];self.assertEqual(sum(p['model']=='P_MedBed' for p in med),2)
        self.assertGreaterEqual(sum(p['model']=='P_Plant' for p in d['placements']),24)
        self.assertEqual(sum(p['model']=='P_Shuttle' for p in d['placements']),1)
        self.assertFalse(any(p['model']=='P_Reactor' and p['zone']=='L1_ENGINE_CONTROL' for p in d['placements']))
    def test_vertical_cores_and_repeated_corridors(self):
        d=self.ship();self.assertEqual([x['y'] for x in d['decks']],[-12.4,0,6.4]);self.assertEqual(len(d['lifts']),2)
        for l in d['lifts']:self.assertEqual(l['floors'],[0,1,2]);self.assertEqual(len(l['landings']),3)
        zones={z['id']:z for z in d['zones']}
        for side in ['N','S']:
            for i in range(1,4):self.assertEqual(zones[f'L1_X{side}{i}']['bounds'],zones[f'L2_X{side}{i}']['bounds'])
        for n in [0,1,2]:self.assertEqual(zones[f'L{n}_STERN']['bounds'][1]-zones[f'L{n}_STERN']['bounds'][0],12)
    def test_formal_nominal_sockets_survive_quarter_turns(self):
        d=self.ship();from ship_geometry import transform_poly
        for m in d['models']:
            self.assertTrue(m['sockets'])
            if m['family'] in ['wall','gate_frame']:
                socket=next(s for s in m['sockets'] if s['name']=='Socket_End');width=m['nominal'][0]
                self.assertEqual(socket['position'],[width,0,0])
                for yaw,expected in [(0,[width,0]),(90,[0,-width]),(180,[-width,0]),(270,[0,width])]:
                    p=transform_poly([[socket['position'][0],socket['position'][2]]],[0,0,0],yaw)[0]
                    self.assertLess(sum(abs(a-b) for a,b in zip(p,expected)),1e-5)
    def test_full_layout_geometry_and_damage_detection(self):
        d=self.ship();from validate_ship_v4 import validate
        self.assertEqual(validate(d)['errors'],[])
        changed=copy.deepcopy(d);changed['placements']=[p for p in changed['placements'] if p['id']!='F_L2_6_24']
        self.assertTrue(validate(changed)['errors'],'Missing upper-deck floor must be detected')
        changed=copy.deepcopy(d);changed['placements']=[p for p in changed['placements'] if p['id']!='C_L2_6_24']
        self.assertTrue(validate(changed)['errors'],'Missing upper-deck ceiling must be detected')
        changed=copy.deepcopy(d);changed['gates'][0]['buttons']=[]
        self.assertTrue(validate(changed)['errors'],'A gate without its button must fail')
    def test_empty_shortened_slabs_and_deleted_coverage_are_rejected(self):
        d=self.ship();from validate_ship_v4 import validate
        for damage in ['empty_model','short_model','no_coverage']:
            with self.subTest(damage=damage):
                changed=copy.deepcopy(d);placement=next(p for p in changed['placements'] if p['id']=='F_L2_6_24');model=next(m for m in changed['models'] if m['id']==placement['model'])
                if damage=='empty_model':model['parts']=[]
                elif damage=='short_model':
                    for part in model['parts']:part['outline']=[v*.5 if i%2==0 else v for i,v in enumerate(part['outline'])]
                else:changed['coverage']=[]
                self.assertTrue(validate(changed)['errors'],damage+' must fail independent surface checks')

if __name__=='__main__':unittest.main(verbosity=2)

