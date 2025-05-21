import unittest
from core_sim.core_grid import CoreGrid
from core_sim.quality import calculate_fa_quality

class TestCoreGrid(unittest.TestCase):

    def setUp(self):
        self.core = CoreGrid()

    def test_grid_size(self):
        self.assertEqual(self.core.grid.shape, (20, 20))

    def test_symmetry(self):
        static_types = ['control', 'detector', 'dummy', 'empty']
        for x in range(10):
            for y in range(10):
                fa = self.core.grid[x, y]
                fa_sym = self.core.grid[19 - x, y]
                if fa.fa_type in static_types and fa_sym.fa_type in static_types:
                    self.assertEqual(fa.fa_type, fa_sym.fa_type)

    def test_quality_calculation(self):
        fa = self.core.grid[7, 7]
        quality = calculate_fa_quality(fa, self.core)
        self.assertIsNotNone(quality)
        self.assertTrue(quality >= 0.0)

if __name__ == '__main__':
    unittest.main()
