import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'C01SourceV71/Tools/v5_dependencies'))
from validate_ship_v5 import solids
from ship_geometry import overlap_poly

def sweep(data,gate_open):
    bodies=solids(data,gate_open)
    ship=[s for s in bodies if s['owner']=='L0_EVAC_HANGAR_EVAC_SHUTTLE']
    other=[s for s in bodies if s['owner']!='L0_EVAC_HANGAR_EVAC_SHUTTLE' and s['x1']>108.5 and s['x0']<113.5 and s['z1']>56 and s['z0']<86 and s['hi']>-3.4 and s['lo']<-.6]
    hits=[]
    for step in range(181):
        dz=step*.1
        for a in ship:
            for b in other:
                if min(a['hi'],b['hi'])-max(a['lo'],b['lo'])<1e-5 or min(a['x1'],b['x1'])-max(a['x0'],b['x0'])<1e-5 or min(a['z1']+dz,b['z1'])-max(a['z0']+dz,b['z0'])<1e-5:continue
                poly=[[x,z+dz] for x,z in a['poly']]
                if overlap_poly(poly,b['poly']):hits.append((step,b['owner']))
    return hits

class ShipOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'C01SourceV76/Data/ship_v76.json').read_text(encoding='utf8'))
        cls.zones={z['id']:z for z in cls.data['zones']}

    def test_crew_and_life_support_zoning(self):
        expected={'L2_S_SUPPORT_03':'LACZNOSC', 'L2_S_SUPPORT_11':'SALON ZALOGI',
                  'L2_N_SUPPORT_08':'NADZOR WODY I POWIETRZA','L2_S_SUPPORT_12':'POSCIEL I ODZIEZ',
                  'L2_S_SUPPORT_07':'PRALNIA','L2_N_SUPPORT_07':'SRODKI HIGIENY'}
        for ident,label in expected.items():self.assertEqual(self.zones[ident]['label'],label)
        self.assertEqual(self.zones['L2_N_SUPPORT_08']['bounds'][0]//42,self.zones['L0_PURIFICATION']['bounds'][0]//42)
        self.assertEqual(self.zones['L2_S_SUPPORT_07']['bounds'][2],self.zones['L2_S_SUPPORT_08']['bounds'][2])
        self.assertEqual(self.zones['L1_ENGINE_CONTROL']['bounds'],self.zones['L0_ENGINE_ROOM']['bounds'])
        self.assertEqual(self.zones['L1_CARGO']['bounds'],self.zones['L0_CARGO']['bounds'])

    def test_shuttle_exit_is_clear_open_and_blocked_closed(self):
        self.assertEqual(sweep(self.data,1),[])
        self.assertTrue(any(name.startswith('L0_LAUNCH_') for _,name in sweep(self.data,0)))

    def test_sweep_detects_a_deliberate_obstruction(self):
        from copy import deepcopy
        data=deepcopy(self.data);sample=deepcopy(next(p for p in data['placements'] if p['model']=='P_Crate'))
        sample.update(id='QA_OBSTRUCTION',x=110,y=-3.4,z=71,yaw=0,gate='',travel=[0,0,0]);data['placements'].append(sample)
        self.assertTrue(any(name=='QA_OBSTRUCTION' for _,name in sweep(data,1)))

    def test_launch_apron_has_eight_modular_tiles(self):
        floors=[p for p in self.data['placements'] if p['id'].startswith('L0_LAUNCH_APRON_')]
        self.assertEqual(len(floors),8)
        self.assertEqual({(p['x'],p['z']) for p in floors},{(x,z) for x in (108,111) for z in (72,75,78,81)})

    def test_closed_gate_segments_are_continuous(self):
        parts=sorted((p for p in self.data['placements'] if p['model']=='G76_LaunchLeaf'),key=lambda p:p['x'])
        model=next(m for m in self.data['models'] if m['id']=='G76_LaunchLeaf');part=model['parts'][0]
        self.assertEqual(len(parts),12)
        for a,b in zip(parts,parts[1:]):self.assertGreaterEqual(a['x']+.47,b['x']-1e-6)
        self.assertAlmostEqual(parts[0]['y']+part['y0'],-3.4)
        self.assertAlmostEqual(parts[0]['y']+part['y1'],-.5)

if __name__=='__main__':unittest.main()
