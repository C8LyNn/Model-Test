import unittest
import grid_layout
import scene_data_v6

class RequirementsV68(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.plan=grid_layout.build();cls.data=scene_data_v6.build()
    def test_level_one_sectors_are_two_full_tiles_and_upper_volume_is_open(self):
        sectors=[z for z in self.data['zones'] if z['deck']==1 and z['kind']=='sector']
        self.assertEqual(len(sectors),6)
        for z in sectors:self.assertEqual(z['height'],6,z['id'])
        upper=[z for z in self.plan['zones'] if z['deck']==2 and z['id'].split('_')[-1] in ('GYM','LAB','MED','CARGO','CONTROL','TECH')]
        self.assertEqual(len(upper),6)
        self.assertTrue(all(z['kind']=='void' for z in upper))
    def test_deck_zero_has_direct_and_side_connections(self):
        links={frozenset((l['a'],l['b'])) for l in self.data['links'] if l['kind']=='gate'}
        for side in ('N','S'):
            for i in range(3):self.assertTrue(frozenset(('L0_MAIN',f'L0_{side}_ACCESS_{i}')) in links,f'L0_MAIN {side} {i}')
            for i in range(2):self.assertTrue(frozenset((f'L0_{side}_ACCESS_{i}',f'L0_{side}_ACCESS_{i+1}')) in links,f'L0 side {side} {i}')
    def test_deck_zero_support_rooms_keep_alternative_path_if_one_spine_gate_is_lost(self):
        from collections import defaultdict, deque
        edges=[(l['a'],l['b']) for l in self.data['links'] if l['a'].startswith('L0_') and l['b'].startswith('L0_')]
        for side in ('N','S'):
            for i in range(3):
                target=f'L0_{side}_ACCESS_{i}'; removed=frozenset(('L0_MAIN',target)); graph=defaultdict(set)
                for a,b in edges:
                    if frozenset((a,b))==removed: continue
                    graph[a].add(b);graph[b].add(a)
                seen={'L0_MAIN'};queue=deque(seen)
                while queue:
                    for nxt in graph[queue.popleft()]-seen: seen.add(nxt);queue.append(nxt)
                self.assertTrue(target in seen,target+' has no alternative route')
    def test_bridge_and_stern_have_explicit_command_and_engine_stations(self):
        placements=self.data['placements'];ids={p['id'] for p in placements}
        for ident in ('BRIDGE_HELM_STATION','BRIDGE_NAV_STATION','STERN_PROPULSION_STATION','STERN_LOGISTICS_STATION'):
            self.assertTrue(ident in ids,ident)
    def test_each_tall_sector_has_reachable_stairs_ladder_and_ducts(self):
        for zone in (z for z in self.data['zones'] if z['deck']==1 and z['kind']=='sector'):
            props=[p for p in self.data['placements'] if p['zone']==zone['id']]
            stairs=sorted((p for p in props if p['model']=='P_Stair_3m'),key=lambda p:p['y'])
            ladder=[p for p in props if p['model']=='P_Ladder_3m']
            vents=[p for p in props if p['model']=='P_Vent_3m']
            mezz=[p for p in props if p['model']=='P_Mezzanine_3m']
            self.assertEqual((len(stairs),len(ladder),len(vents),len(mezz)),(2,1,2,1),zone['id'])
            self.assertAlmostEqual(stairs[-1]['x']+3,mezz[0]['x'],msg=zone['id'])
            self.assertAlmostEqual(stairs[-1]['y']+1.5,mezz[0]['y'],msg=zone['id'])
    def test_bridge_central_command_area_has_no_upper_floor_above_it(self):
        ids={p['id'] for p in self.data['placements'] if p['category']=='Floors'}
        self.assertFalse('F_2_-10_14' in ids,'Upper slab blocks the central bridge atrium')
        self.assertTrue('F_2_-10_18' in ids,'Upper side chase gallery is missing')
    def test_aft_displays_face_the_work_area(self):
        displays=[p for p in self.data['placements'] if p['zone']=='L1_STERN' and p['model']=='P_V68_StatusDisplay']
        stations=[p for p in self.data['placements'] if p['zone']=='L1_STERN' and p['category']=='CoreStations']
        self.assertGreaterEqual(len(displays),4)
        self.assertTrue(all(p['yaw']==180 for p in displays))
        self.assertGreaterEqual(len(stations),8)
    def test_wall_spans_respect_full_storey_boundaries(self):
        floors=[d['y'] for d in self.data['decks']];bounds=[floors[0]+3,floors[1],floors[1]+3,floors[2]]
        for p in self.data['placements']:
            if p['category']!='Walls':continue
            h=int(p['model'].split('_')[1][1:])/1000
            for boundary in bounds:
                if abs(boundary-floors[2])<1e-5 and abs(p['y']-3)<1e-5 and abs(h-3)<1e-5: continue # open two-storey sector
                self.assertFalse(p['y']+1e-5<boundary<p['y']+h-1e-5,(p['id'],boundary))

if __name__=='__main__':unittest.main()
