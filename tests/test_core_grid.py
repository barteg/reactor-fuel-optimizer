import unittest
from core_sim.core_grid import CoreGrid
from core_sim.quality import calculate_fa_quality
from core_sim.fuel_assembly import Fuel

class TestCoreGrid(unittest.TestCase):

    def setUp(self):
        # Jeśli chcesz domyślnie 20x20, nie przekazuj parametrów.
        # Jeśli możesz podać rozmiar: CoreGrid(width=20, height=20)
        self.core = CoreGrid()

    def test_grid_size(self):
        self.assertEqual(len(self.core.grid), self.core.width)  # liczba wierszy (Y)
        self.assertEqual(len(self.core.grid[0]), self.core.height)  # liczba kolumn (X)

    def test_symmetry(self):
        static_types = ['control', 'detector', 'dummy', 'empty']
        size_x = self.core.width
        size_y = self.core.height
        for x in range(size_x):
            for y in range(size_y):
                fa = self.core.grid[x][y]
                fa_sym = self.core.grid[size_x - 1 - x][y]
                if fa.fa_type in static_types and fa_sym.fa_type in static_types:
                    self.assertEqual(fa.fa_type, fa_sym.fa_type)

    def test_quality_calculation(self):
        # 1. Wstaw główny FA typu Fuel na testowaną pozycję
        fa = Fuel(enrichment=3.2)
        fa.position = (7, 7)
        self.core.grid[7][7] = fa

        # 2. Wypełnij sąsiedztwo wokół [7][7] Fuelami
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = 7 + dx, 7 + dy
                if 0 <= x < self.core.width and 0 <= y < self.core.height:
                    f = Fuel(enrichment=3.2)
                    f.position = (x, y)
                    self.core.grid[x][y] = f

        # 3. Wywołaj scoring
        quality = calculate_fa_quality(fa, self.core)
        print("Quality:", quality)  # Debug
        self.assertIsNotNone(quality)
        self.assertTrue(quality >= 0.0)

if __name__ == '__main__':
    unittest.main()
