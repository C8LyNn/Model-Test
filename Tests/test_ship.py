import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'Tools'))

class ReferencePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=(ROOT if (ROOT/'Assets').is_dir() else ROOT/'UnityProject')/'Assets/C01ShipV3/Data/ship.json';cls.ship=json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
    def test_scene_manifest_exists(self):
        self.assertIsNotNone(self.ship,'The requested ship has not been generated')
    def test_reference_topology(self):
        if self.ship is None:self.skipTest('manifest missing')
        from validate_ship import validate
        self.assertEqual(validate(self.ship)['errors'],[])
        cabins=[z for z in self.ship['zones'] if z['kind']=='cabin'];self.assertEqual(len(cabins),12)
        self.assertEqual(sum(p['module']=='P_Engine' for p in self.ship['placements']),5)
        for i in range(1,13):
            entries=[d for d in self.ship['doors'] if f'C{i:02d}' in d['zones']]
            self.assertEqual(len(entries),1);other=next(z for z in entries[0]['zones'] if z!=f'C{i:02d}')
            self.assertTrue(other.startswith('XN' if i<=6 else 'XS'))
    def test_reference_damage_is_rejected(self):
        if self.ship is None:self.skipTest('manifest missing')
        from validate_ship import validate
        mutations={
            'missing_cabin_entry':lambda s:s['doors'].__setitem__(slice(None),[d for d in s['doors'] if d['id']!='CABIN_01']),
            'extra_cabin_main_door':lambda s:s['doors'].append(dict(s['doors'][0],id='BAD',zones=['C01','MAIN_W'])),
            'missing_engine':lambda s:s['placements'].__setitem__(slice(None),[p for p in s['placements'] if p['id']!='ENGINE_05']),
            'missing_extended_branch_floor':lambda s:s['placements'].__setitem__(slice(None),[p for p in s['placements'] if p['id']!='F_6_24']),
            'missing_extended_branch_ceiling':lambda s:s['placements'].__setitem__(slice(None),[p for p in s['placements'] if p['id']!='C_6_24']),
            'missing_floor':lambda s:s['placements'].__setitem__(slice(None),[p for p in s['placements'] if p['id']!='F_0_0']),
            'missing_wall':lambda s:s['placements'].__setitem__(slice(None),[p for p in s['placements'] if p['id']!='W_H_0_0']),
            'duplicate_post':lambda s:s['placements'].append(copy.deepcopy(next(p for p in s['placements'] if p['category']=='Nodes'))),
            'misplaced_airlock':lambda s:next(z for z in s['zones'] if z['id']=='D1').__setitem__('bounds',[9,15,9,12]),
        }
        evidence={}
        for name,mutate in mutations.items():
            s=copy.deepcopy(self.ship);mutate(s);result=validate(s);evidence[name]=result['errors'][:5]
            self.assertTrue(result['errors'],name)
        ((ROOT/'C01Ship_QA' if (ROOT/'Assets').is_dir() else ROOT/'QA')/'layout_mutations.json').write_text(json.dumps(evidence,indent=2))
    def test_no_missing_bow_floor_area(self):
        if self.ship is None:self.skipTest('manifest missing')
        from ship_geometry import polygon_area
        from validate_ship import floor_polygons
        floors=floor_polygons(self.ship)
        self.assertAlmostEqual(sum(polygon_area(p) for _,p in floors),1845,places=4)
    def test_geometry_including_props_and_open_doors(self):
        if self.ship is None:self.skipTest('manifest missing')
        from validate_ship import geometry_audit
        self.assertEqual(geometry_audit(self.ship)['status'],'PASS')
    def test_complete_sweeps_and_independent_door_angles(self):
        if self.ship is None:self.skipTest('manifest missing')
        from validate_ship import sweep_audit
        self.assertEqual(sweep_audit(self.ship)['status'],'PASS')

if __name__=='__main__':unittest.main(verbosity=2)


