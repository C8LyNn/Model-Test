import json
from pathlib import Path
import sys
import unittest

root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'C01SourceV71/Tools/v5_dependencies'))
from validate_ship_v5 import solids
from ship_geometry import overlap_poly

def launch_sweep(data,openness):
    bodies=solids(data,openness);ship=[s for s in bodies if s['owner']=='L1_CARGO_EVAC_SHUTTLE']
    rest=[s for s in bodies if s['owner']!='L1_CARGO_EVAC_SHUTTLE' and s['x1']>108.5 and s['x0']<113.5 and s['z1']>2 and s['z0']<31 and s['hi']>0 and s['lo']<2.8]
    hits=[]
    for i in range(181):
        dz=-i*.1
        for a in ship:
            for b in rest:
                if min(a['hi'],b['hi'])-max(a['lo'],b['lo'])<1e-5 or min(a['x1'],b['x1'])-max(a['x0'],b['x0'])<1e-5 or min(a['z1']+dz,b['z1'])-max(a['z0']+dz,b['z0'])<1e-5:continue
                if overlap_poly([[x,z+dz] for x,z in a['poly']],b['poly']):hits.append((i,b['owner']))
    return hits

class TwoDeckShip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((root/'C01SourceV77/Data/ship_v77.json').read_text(encoding='utf8'))
    def test_no_deck_zero_or_lower_wall_segments(self):
        self.assertEqual([d['id'] for d in self.data['decks']],[1,2])
        self.assertFalse(any(z['deck']==0 for z in self.data['zones']))
        self.assertFalse(any(g['deck']==0 for g in self.data['gates']))
        self.assertFalse(any(p['deck']==0 for p in self.data['placements']))
        self.assertFalse(any(p['deck']==-1 and p['category'] in ('Walls','Nodes') and p['y']<-.401 for p in self.data['placements']))
    def test_lifts_have_only_two_stops(self):
        for lift in self.data['lifts']:
            self.assertEqual(lift['floors'],[1,2]);self.assertFalse(lift['landings'][0]);self.assertTrue(all(lift['landings'][1:]))
        self.assertFalse(any(p.get('buttonLift') and p['buttonFloor']==0 for p in self.data['placements']))
    def test_essential_functions_survive(self):
        p=self.data['placements'];models={x['model'] for x in p if x['deck']==1}
        self.assertTrue({'P_Reactor','P_Plant','P_Purifier_ROOM3','P_Shuttle_ROOM3','P_Crate'}<=models)
        self.assertEqual(len([x for x in p if x['model']=='P_Plant' and x['zone']=='L1_LAB']),15)
        self.assertEqual(len([x for x in p if x['category']=='ShaftBases']),12)
    def test_all_links_reference_remaining_zones(self):
        ids={z['id'] for z in self.data['zones']}
        for l in self.data['links']:self.assertIn(l['a'],ids);self.assertIn(l['b'],ids)
    def test_shuttle_clear_when_open_and_blocked_when_closed(self):
        self.assertFalse(launch_sweep(self.data,1))
        self.assertTrue(any(name.startswith('L1_LAUNCH_LEAF') for _,name in launch_sweep(self.data,0)))
    def test_floor_audit_detects_missing_tile(self):
        from copy import deepcopy
        sys.path.insert(0,str(root/'C01SourceV71/Tools'))
        from audit_floor_v77 import audit
        data=deepcopy(self.data);ident='F_1_21_20';self.assertTrue(any(p['id']==ident for p in data['placements']))
        data['placements']=[p for p in data['placements'] if p['id']!=ident]
        result=audit(data);self.assertEqual(result['status'],'FAIL');self.assertGreater(result['gaps'],0)
    def test_launch_sweep_detects_added_obstacle(self):
        from copy import deepcopy
        data=deepcopy(self.data);p=deepcopy(next(x for x in data['placements'] if x['model']=='P_Crate'))
        p.update(id='QA_LAUNCH_OBSTACLE',x=110,y=0,z=14,yaw=0,gate='',travel=[0,0,0]);data['placements'].append(p)
        self.assertTrue(any(name=='QA_LAUNCH_OBSTACLE' for _,name in launch_sweep(data,1)))

if __name__=='__main__':unittest.main()
