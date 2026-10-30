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


def visual_exceeds_collider(visual, physical, tolerance=0.03):
    """Python math mirror of C01-13 Unity Editor ExtendsOutside, not Unity execution."""
    return any(visual[0][i] < physical[0][i] - tolerance or
               visual[1][i] > physical[1][i] + tolerance for i in range(3))


def aabb_separation(a, b):
    """Mirror conservative world-space Unity renderer Bounds gap, metres."""
    return sum(max(0.0, a[0][i]-b[1][i], b[0][i]-a[1][i])**2
               for i in range(3))**.5


class AccessReaderAttachmentReferenceTests(unittest.TestCase):
    # Source-grounded P17-02 world bounds, not a Blender or Unity execution.
    # Historical PASS12 housing at cf405ed6: .5mm source gap, now fixed in PASS13.
    housing = ((-.0795, .0175, .0225), (.0795, .2625, .0575))
    housing_pass13 = ((-.0795, .0175, .0225), (.0795, .2625, .0585))
    keybed = ((-.064, .0475, .058), (.064, .2025, .064))
    backing = ((-.09, 0, 0), (.09, .28, .016))
    screw = ((-.0875, .0055, .0155), (-.0785, .0145, .0185))

    def test_source_keybed_housing_positive_half_mm_gap(self):
        self.assertAlmostEqual(aabb_separation(self.keybed, self.housing), .0005, places=8)

    def test_pass13_revised_housing_closes_keybed_gap(self):
        self.assertEqual(aabb_separation(self.keybed, self.housing_pass13), 0.0)

    def test_pass13_front_plane_half_mm_seating(self):
        self.assertAlmostEqual(self.housing_pass13[1][2] - self.keybed[0][2], .0005, places=8)

    def test_screw_overlaps_backing_after_full_scale(self):
        self.assertEqual(aabb_separation(self.screw, self.backing), 0.0)

    def test_gap_detected_above_two_hundred_fifty_micrometres(self):
        self.assertGreater(aabb_separation(self.keybed, self.housing), .00025)

    def test_example_seated_keybed_removes_aabb_gap(self):
        seated = (tuple(v if i != 2 else v-.0006 for i,v in enumerate(self.keybed[0])),
                  tuple(v if i != 2 else v-.0006 for i,v in enumerate(self.keybed[1])))
        self.assertEqual(aabb_separation(seated, self.housing), 0.0)

    def test_rotated_or_overlapping_aabb_cannot_certify_contact(self):
        # AABB overlap is only a candidate; exact triangle testing remains mandatory.
        self.assertEqual(aabb_separation(self.keybed, self.keybed), 0.0)


class AccessReaderMeshEnvelopeReferenceTests(unittest.TestCase):
    # Directly measured from TRUE P17-02 producer glTF, PR #17 SHA
    # 79d8dcd3c7a4e39a7a3bcb3c88551642bf52d191, source binary buffer.
    # These fixtures do NOT substitute for Blender FBX/Unity validation.
    base_collider = ((-.09, 0, 0), (.09, .28, .07))

    def test_historical_unscaled_screw_regression_snapshot(self):
        # Old failing interpretation omitted glTF node.scale; should never be treated
        # as the CURRENT P17-02 world geometry.
        bad_render = ((-1.083, -.99, -.983), (1.083, 1.27, 1.017))
        self.assertTrue(visual_exceeds_collider(bad_render, self.base_collider))

    def test_current_transformed_screw_is_nominal(self):
        # Real glTF P17-02 at C01-17 commit cf405ed6: mesh20 local +/-1m,
        # node.scale (0.0045,0.0045,0.003), node translation (-.083,.01,.017).
        actual_screw = ((-.0875, .0055, .0155), (-.0785, .0145, .0185))
        self.assertFalse(visual_exceeds_collider(actual_screw, self.base_collider))
        self.assertAlmostEqual(actual_screw[1][0] - actual_screw[0][0], .009, places=8)
        self.assertAlmostEqual(actual_screw[1][2] - actual_screw[0][2], .003, places=8)

    def test_original_reader_nominal_mesh_is_bounded(self):
        self.assertFalse(visual_exceeds_collider(
            ((-.09, 0, 0), (.09, .28, .07)), self.base_collider))

    def test_legitimate_twenty_mm_overhang_is_not_rejected(self):
        self.assertFalse(visual_exceeds_collider(
            ((-.11, -.01, -.01), (.11, .29, .08)), self.base_collider))

    def test_forty_mm_protrusion_is_rejected(self):
        self.assertTrue(visual_exceeds_collider(
            ((-.13, 0, 0), (.09, .28, .07)), self.base_collider))


if __name__ == "__main__":
    unittest.main()
