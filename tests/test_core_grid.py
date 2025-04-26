import unittest
from core_sim.core_grid import CoreGrid
from core_sim.quality import calculate_fa_quality

class TestCoreGrid(unittest.TestCase):

    def setUp(self):
        self.core = CoreGrid()

    def test_grid_size(self):
        self.assertEqual(self.core.grid.shape, (20, 20))

    def test_symmetry(self):
        for x in range(10):
            for y in range(10):
                fa = self.core.get_fa(x, y)
                fa_sym = self.core.get_fa(19 - x, y)
                self.assertEqual(fa.fa_type, fa_sym.fa_type)

    def test_quality_calculation(self):
        fa = self.core.get_fa(7, 7)
        quality = calculate_fa_quality(fa, self.core)
        self.assertIsNotNone(quality)
        self.assertTrue(quality >= 0.0)

if __name__ == '__main__':
    unittest.main()
