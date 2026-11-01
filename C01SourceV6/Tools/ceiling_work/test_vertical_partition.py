import unittest

from vertical_partition import vertical_modules


class VerticalPartitionTests(unittest.TestCase):
    def test_full_wall_keeps_eight_square_modules_and_smooth_trim(self):
        parts = list(vertical_modules([(-12.4, 12.4)], roof_elevations=[12.4]))
        self.assertEqual(parts, [(-12.4, -9.4, 'panel'), (-9.4, -6.4, 'panel'),
            (-6.4, -3.4, 'panel'), (-3.4, -0.4, 'panel'), (-0.4, 2.6, 'panel'),
            (2.6, 5.6, 'panel'), (5.6, 8.6, 'panel'), (8.6, 11.6, 'panel'),
            (11.6, 12.4, 'trim')])

    def test_story_wall_retains_3m_panels_and_exact_roof(self):
        parts = list(vertical_modules([(0, 6.4)], roof_elevations=[6.4]))
        self.assertEqual(parts, [(0, 3, 'panel'), (3, 6, 'panel'), (6, 6.4, 'trim')])

    def test_exact_grid_has_no_trim(self):
        self.assertEqual(list(vertical_modules([(6.4, 12.4)], roof_elevations=[12.4])),
                         [(6.4, 9.4, 'panel'), (9.4, 12.4, 'panel')])

    def test_gate_ends_are_not_misclassified_as_ceiling(self):
        self.assertEqual(list(vertical_modules([(0, 3.4), (6.4, 12.4)], roof_elevations=[12.4])),
                         [(0, 3, 'panel'), (3, 3.4, 'panel'),
                          (6.4, 9.4, 'panel'), (9.4, 12.4, 'panel')])

    def test_intrinsically_short_roof_span_stays_exact(self):
        self.assertEqual(list(vertical_modules([(12, 12.4)], roof_elevations=[12.4])),
                         [(12, 12.4, 'trim')])

    def test_long_roof_remainder_is_not_a_narrow_strip(self):
        self.assertEqual(list(vertical_modules([(0, 5)], roof_elevations=[5])),
                         [(0, 3, 'panel'), (3, 5, 'panel')])


if __name__ == '__main__':
    unittest.main()
