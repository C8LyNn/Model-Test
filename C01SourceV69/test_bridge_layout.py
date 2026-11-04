import unittest
from bridge_layout import build

class BridgeLayoutTests(unittest.TestCase):
    def setUp(self):
        self.layout=build()
        self.items={p['id']:p for p in self.layout['placements']}

    def test_distinct_roles_and_reusable_models(self):
        self.assertEqual(len(self.items),len(self.layout['placements']))
        self.assertEqual(sum(p['model']=='P_V68_CommandConsole' for p in self.items.values()),6)
        self.assertEqual(sum(p['model']=='P_V68_CommandChair' for p in self.items.values()),7)
        self.assertEqual(sum(p['model']=='P_V68_StatusDisplay' for p in self.items.values()),6)
        self.assertTrue(all(p['y']==0 and p['yaw']==0 for p in self.items.values()))

    def test_stations_and_seats_mirror_about_bridge_axis(self):
        pairs=[('BRIDGE_HELM_STATION','BRIDGE_NAV_STATION',.9),
               ('BRIDGE_HELM_CHAIR','BRIDGE_NAV_CHAIR',.6),
               ('BRIDGE_SCIENCE_STATION','BRIDGE_COMMS_STATION',.9),
               ('BRIDGE_SCIENCE_CHAIR','BRIDGE_COMMS_CHAIR',.6),
               ('BRIDGE_TACTICAL_STATION','BRIDGE_ENGINEERING_STATION',.9),
               ('BRIDGE_TACTICAL_CHAIR','BRIDGE_ENGINEERING_CHAIR',.6),
               ('BRIDGE_DISPLAY_S','BRIDGE_DISPLAY_N',1.4)]
        for left,right,offset in pairs:
            a,b=self.items[left],self.items[right]
            self.assertEqual(a['x'],b['x'])
            self.assertAlmostEqual(a['z']+b['z']+2*offset,2*self.layout['symmetryZ'],msg=left)
        captain=self.items['BRIDGE_CAPTAIN_CHAIR']
        self.assertAlmostEqual(captain['z']+.6,self.layout['symmetryZ'])

if __name__ == '__main__': unittest.main()
