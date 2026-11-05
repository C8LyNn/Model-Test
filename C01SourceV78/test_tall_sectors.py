import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / 'C01SourceV77/Data/ship_v77.json'
NEW = ROOT / 'C01SourceV78/Data/ship_v78.json'


class TallSectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(OLD.read_text(encoding='utf8'))
        cls.new = json.loads(NEW.read_text(encoding='utf8'))

    def test_all_six_shared_sectors_are_three_modules_high(self):
        sectors = [z for z in self.new['zones'] if z['kind'] == 'sector']
        self.assertEqual(len(sectors), 6)
        self.assertTrue(all(z['height'] == 9 and z['spansDecks'] for z in sectors))

    def test_roof_is_raised_exactly_one_module(self):
        old = {p['id']: p for p in self.old['placements'] if p['category'] == 'Ceilings' and p.get('zone', '').startswith('L1_') and p['y'] == 6.2}
        new = {p['id']: p for p in self.new['placements']}
        self.assertGreater(len(old), 400)
        for key, p in old.items():
            self.assertEqual(new[key]['y'], 9.2, key)
            self.assertEqual((new[key]['x'], new[key]['z']), (p['x'], p['z']))

    def test_perimeter_is_filled_once_with_square_modules(self):
        modules = [p for p in self.new['placements'] if p['id'].startswith('V78_W_')]
        nodes = [p for p in self.new['placements'] if p['id'].startswith('V78_N_')]
        edges = set()
        for z in [z for z in self.new['zones'] if z['kind'] == 'sector']:
            x0,x1,z0,z1 = map(int,z['bounds'])
            edges.update(('H',x,zv) for x in range(x0,x1,3) for zv in (z0,z1))
            edges.update(('V',xv,zz) for xv in (x0,x1) for zz in range(z0,z1,3))
        self.assertEqual(len(modules), len(edges))
        self.assertEqual({(p['axis'],p['x'],p['z']) for p in modules}, edges)
        self.assertTrue(all(p['y'] == 6.4 and p['model'] == 'W78_H2600' for p in modules))
        self.assertEqual(len(nodes),len({(p['x'],p['z']) for p in nodes}))
        self.assertTrue(all((p['y'],p['model']) in ((6,'N_H3000'),(6.4,'N_H2600')) for p in nodes))

    def test_walkways_and_gates_preserved(self):
        old = {p['id']: p for p in self.old['placements'] if p['id'].startswith('L2_ROUTE_') and '_HEAD_' not in p['id']}
        new = {p['id']: p for p in self.new['placements']}
        self.assertGreater(len(old), 20)
        self.assertTrue(all(new[k] == p for k,p in old.items()))
        self.assertEqual(self.old['gates'], self.new['gates'])

    def test_audit_detects_a_missing_raised_ceiling_tile(self):
        import copy, sys
        sys.path[:0]=[str(ROOT/'C01SourceV71/Tools'),str(ROOT/'C01SourceV71/Tools/v5_dependencies'),str(ROOT/'C01SourceV77')]
        source=(ROOT/'C01SourceV77/audit_ceiling_v77.py').read_text(encoding='utf8')
        source=source.replace('planes[6.0 if deck==1 and kind=="sector"','planes[9.0 if deck==1 and kind=="sector"')
        scope={'__name__':'ceiling_test'};exec(compile(source,'ceiling_test','exec'),scope)
        data=copy.deepcopy(self.new);data['placements']=[p for p in data['placements'] if p['id']!='C1_1_19']
        result=scope['audit'](data);self.assertEqual(result['status'],'FAIL');self.assertGreater(result['gaps'],0)


if __name__ == '__main__': unittest.main()
