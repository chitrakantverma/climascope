import unittest
from modules.grid_math import latitude_weights

class GridMathTests(unittest.TestCase):
    def test_equator_has_twice_the_weight_of_sixty_degrees(self):
        w = latitude_weights([0, 60])
        self.assertAlmostEqual(w[0] / w[1], 2)
        self.assertAlmostEqual(sum(v * a for v, a in zip([10, 30], w)) / sum(w), 50 / 3)
    def test_north_south_symmetry(self):
        w = latitude_weights([-60, 0, 60])
        self.assertAlmostEqual(w[0], w[2])
    def test_descending_grid(self):
        self.assertEqual(latitude_weights([60, 0, -60]), latitude_weights([-60, 0, 60]))
    def test_poles_do_not_add_area(self):
        self.assertEqual(latitude_weights([-90, 0, 90]), [0, 1, 0])
    def test_invalid_coordinates(self):
        for coordinates in [[], [float('nan')], [91], [0, 0], [-90, 90], [0, 15, 60]]:
            with self.subTest(coordinates=coordinates):
                with self.assertRaises(ValueError): latitude_weights(coordinates)

if __name__ == '__main__': unittest.main()
