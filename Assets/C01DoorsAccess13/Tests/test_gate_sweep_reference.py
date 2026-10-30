#!/usr/bin/env python3
"""C01-13 pure-math fixture tests, not a Unity/Blender import test.
Run: python3 -m unittest discover -s Assets/C01DoorsAccess13/Tests -p 'test_*.py' -v
"""
import unittest

def sweep_aabb(box_min, box_max, travel, openness, margin=0.02):
    """Reference for DoorAccessSweepAudit.cs: gate.travel is world-space."""
    closed = [box_min[i] - openness * travel[i] for i in range(3)]
    opened = [box_min[i] + (1.0 - openness) * travel[i] for i in range(3)]
    closed_max = [box_max[i] - openness * travel[i] for i in range(3)]
    opened_max = [box_max[i] + (1.0 - openness) * travel[i] for i in range(3)]
    # Unity Bounds.Expand(2*margin) expands each side by 'margin'
    return ([min(closed[i], opened[i]) - margin for i in range(3)],
            [max(closed_max[i], opened_max[i]) + margin for i in range(3)])

def intersects(first, second):
    return all(first[0][i] <= second[1][i] and second[0][i] <= first[1][i]
               for i in range(3))

class SlidingDoorSweepReferenceTests(unittest.TestCase):
    def setUp(self):
        self.base_min = (0.0, 0.0, 0.0)
        self.base_max = (1.0, 2.0, 0.1)
        self.travel = (1.2, 0.0, 0.0)

    def test_closed_sweep_covers_both_positions(self):
        self.assertEqual(sweep_aabb(self.base_min, self.base_max, self.travel, 0, 0),
                         ([0.0, 0.0, 0.0], [2.2, 2.0, 0.1]))

    def test_open_sweep_same_coverage(self):
        self.assertEqual(sweep_aabb((1.2,0,0),(2.2,2,0.1), self.travel, 1, 0),
                         ([0.0, 0.0, 0.0], [2.2, 2.0, 0.1]))

    def test_midpoint_sweep_same_coverage(self):
        self.assertEqual(sweep_aabb((0.6,0,0),(1.6,2,0.1), self.travel, .5, 0),
                         ([0.0, 0.0, 0.0], [2.2, 2.0, 0.1]))

    def test_negative_direction_travel(self):
        self.assertEqual(sweep_aabb(self.base_min,self.base_max,(-1,0,0),0,0),
                         ([-1.0,0.0,0.0],[1.0,2.0,0.1]))

    def test_mount_outside_sweep(self):
        gate = sweep_aabb(self.base_min,self.base_max,self.travel,0)
        prop = ([2.5,.8,.0], [2.68,1.08,.07])
        self.assertFalse(intersects(gate,prop))

    def test_mount_intersects_middle(self):
        gate = sweep_aabb(self.base_min,self.base_max,self.travel,0)
        prop = ([1.08,.8,.0], [1.26,1.08,.07])
        self.assertTrue(intersects(gate,prop))

    def test_margin_flags_near_miss(self):
        gate = sweep_aabb(self.base_min,self.base_max,self.travel,0)
        prop = ([2.215,.8,.0], [2.30,1.08,.07])
        self.assertTrue(intersects(gate,prop))

    def test_clear_with_bigger_gap(self):
        gate = sweep_aabb(self.base_min,self.base_max,self.travel,0)
        prop = ([2.25,.8,.0], [2.38,1.08,.07])
        self.assertFalse(intersects(gate,prop))

    def test_diagonal_travel_broadphase_is_conservative(self):
        gate = sweep_aabb(self.base_min,self.base_max,(1.2,0,1.2),0,0)
        # Corner of swept AABB can be occupied even when no actual moving leaf reaches it.
        corner = ([2.0,.8,0], [2.1,1.08,.1])
        self.assertTrue(intersects(gate,corner))

if __name__ == "__main__":
    unittest.main()
