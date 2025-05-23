import unittest
from core_sim.core_grid import CoreGrid
from optimization.fitness import fitness, calculate_temperatures
from optimization.hotspots import hotspots
from optimization.penalties import penalties
from optimization.symmetry import symmetry
from optimization.energy import energy

class TestFitnessComponents(unittest.TestCase):
    def setUp(self):
        self.core = CoreGrid(width=20, height=20)
        self.grid = self.core.grid
        self.width = self.core.width
        self.height = self.core.height

    def test_hotspots_nonnegative(self):
        FA_lifes = [self.grid[x][y].life for x in range(self.width) for y in range(self.height)]
        penalty = hotspots(FA_lifes)
        self.assertGreaterEqual(penalty, 0)

    def test_overheat_penalty(self):
        FA_lifes = [self.grid[x][y].life for x in range(self.width) for y in range(self.height)]
        FA_temperatures = calculate_temperatures(self.core)  # zakładam, że przyjmuje core_grid
        penalty = penalties(FA_temperatures, FA_lifes)
        self.assertGreaterEqual(penalty, 0)

    def test_symmetry_score_bounds(self):
        FA_lifes = [self.grid[x][y].life for x in range(self.width) for y in range(self.height)]
        FA_energies = [energy(self.grid[x][y].life, self.grid[x][y].enrichment) for x in range(self.width) for y in range(self.height)]
        N = self.width * self.height
        score = symmetry(FA_lifes, FA_energies, N)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_fitness_return(self):
        fit = fitness(self.core)  # jeśli fitness przyjmuje core_grid!
        self.assertIsInstance(fit, float)

if __name__ == '__main__':
    unittest.main()
