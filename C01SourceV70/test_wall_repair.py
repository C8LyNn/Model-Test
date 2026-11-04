import collections
import copy
import json
import unittest
from pathlib import Path
from wall_repair import build

ROOT=Path(__file__).resolve().parent.parent

def height(model):
    return int(model.split('_')[1][1:])/1000

def spans(items):
    groups=collections.defaultdict(list)
    for p in items:
        key=(p['category'],p['x'],p['z'],p['yaw'])
        groups[key].append((round(p['y'],6),round(p['y']+height(p['model']),6)))
    result={}
    for key,intervals in groups.items():
        merged=[]
        for lo,hi in sorted(intervals):
            if merged and lo<=merged[-1][1]+1e-6:merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
            else:merged.append((lo,hi))
        result[key]=merged
    return result

class WallRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'Assets/C01ShipV68/Data/ship_v68.json').read_text(encoding='utf8'))
        cls.repair=build(cls.data)
        cls.before=[copy.deepcopy(p) for p in cls.data['placements'] if p['category'] in ('Walls','Nodes')]
        cls.after=copy.deepcopy(cls.before);byid={p['id']:p for p in cls.after}
        for m in cls.repair['moves']:
            p=byid[m['id']]
            if abs(p['y']-m['fromY'])>1e-6:raise AssertionError(m['id'])
            p['y']=m['toY']

    def test_no_solid_wall_or_node_volume_is_lost_or_added(self):
        self.assertTrue(self.repair['moves'])
        self.assertEqual(spans(self.before),spans(self.after))

    def test_short_upper_segments_now_occupy_the_floor_slab(self):
        moved={m['id'] for m in self.repair['moves']}
        shorts=[p for p in self.before if p['id'] in moved and p['model'] in ('W3_H400','N_H400')]
        self.assertTrue(shorts)
        byid={p['id']:p for p in self.after}
        for p in shorts:self.assertAlmostEqual(byid[p['id']]['y'],3.0,msg=p['id'])
        full=[p for p in self.before if p['id'] in moved and p['model'] in ('W3_H3000','N_H3000')]
        self.assertEqual(len(shorts),len(full))
        for p in full:self.assertAlmostEqual(byid[p['id']]['y'],3.4,msg=p['id'])

    def test_every_slab_join_has_one_consistent_seam(self):
        walls=[p for p in self.after if p['category']=='Walls'];idx=collections.defaultdict(list)
        for p in walls:idx[(p['x'],p['z'],p['yaw'])].append(p)
        expected=set();fascia_tops=set()
        for p in walls:
            if p['model']!='W3_H3000':continue
            group=idx[(p['x'],p['z'],p['yaw'])]
            fascia=[q for q in group if q['model'].startswith('W3_H400') and abs(q['y']-(p['y']+3))<1e-6]
            if fascia:
                expected.add(p['id'])
                if not any(q['model']=='W3_H3000' and abs(q['y']-fascia[0]['y']-.4)<1e-6 for q in group):
                    fascia_tops.add(fascia[0]['id'])
        self.assertTrue(expected)
        self.assertEqual(expected,set(self.repair['singleSeamWalls']))
        self.assertEqual(fascia_tops,set(self.repair['topBandFascias']))

if __name__=='__main__':unittest.main()
