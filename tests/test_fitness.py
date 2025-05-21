import unittest
import numpy as np
from core_sim.core_grid import CoreGrid
from optimization.fitness import fitness, calculate_temperatures
from optimization.hotspots import hotspots
from optimization.penalties import penalties
from optimization.symmetry import symmetry
from optimization.energy import energy

class TestFitnessComponents(unittest.TestCase):
    def setUp(self):
        self.core = CoreGrid(size=20)
        self.grid = self.core.grid
        self.size = self.core.size

    def test_hotspots_nonnegative(self):
        penalty = hotspots(self.grid)
        self.assertGreaterEqual(penalty, 0)

    def test_overheat_penalty(self):
        FA_lifes = [self.grid[x, y].life for x in range(self.size) for y in range(self.size)]
        FA_temperatures = calculate_temperatures(self.grid)
        penalty = penalties(FA_temperatures, FA_lifes)
        self.assertGreaterEqual(penalty, 0)

    def test_symmetry_score_bounds(self):
        FA_lifes = [self.grid[x, y].life for x in range(self.size) for y in range(self.size)]
        FA_energies = [energy(self.grid[x, y].life, self.grid[x, y].enrichment) for x in range(self.size) for y in range(self.size)]
        N = self.size * self.size
        score = symmetry(FA_lifes, FA_energies, N)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_fitness_return(self):
        fit = fitness(self.grid)
        self.assertIsInstance(fit, float)

if __name__ == '__main__':
    unittest.main()
