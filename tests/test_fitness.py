import unittest
from core_sim.core_grid import CoreGrid
from optimization.fitness import (
    fitness, f_hotspots, f_overheat_penalty, f_energy, f_lifetime, f_symmetry
)

class TestFitnessComponents(unittest.TestCase):

    def setUp(self):
        self.core = CoreGrid(size=20)

    def test_energy_positive(self):
        en = f_energy(self.core)
        self.assertGreater(en, 0)

    def test_lifetime_range(self):
        life = f_lifetime(self.core)
        self.assertGreaterEqual(life, 0.2)
        self.assertLessEqual(life, 0.8)

    def test_hotspots_nonnegative(self):
        hot = f_hotspots(self.core)
        self.assertGreaterEqual(hot, 0)

    def test_overheat_penalty_nonnegative(self):
        ovp = f_overheat_penalty(self.core)
        self.assertGreaterEqual(ovp, 0)

    def test_symmetry_score_bounds(self):
        sym = f_symmetry(self.core)
        self.assertGreaterEqual(sym, 0)
        self.assertLessEqual(sym, 1)

    def test_fitness_return(self):
        fit = fitness(self.core)
        self.assertIsInstance(fit, float)

if __name__ == '__main__':
    unittest.main()