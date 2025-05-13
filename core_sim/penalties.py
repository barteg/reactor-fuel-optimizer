# penalties.py

import math
from copy import deepcopy
from core_sim.fuel_assembly import FuelAssembly

class PenaltyCalculator:
    def __init__(self):
        self.w_temp = 1.0
        self.w_hotspot = 1.0
        self.w_symmetry = 1.0

    def evaluate(self, grid):
        overheated_count = 0
        life_below_threshold = 0
        total_hotspot_penalty = 0.0
        total_temp_penalty = 0.0

        for y in range(grid.height):
            for x in range(grid.width):
                fa = grid.get_fa(x, y)
                if not isinstance(fa, FuelAssembly):
                    continue

                # Overheating
                if fa.temperature > 620:
                    overheated_count += 1
                    total_temp_penalty += math.exp((fa.temperature - 620) / 50)

                # Life decay
                if fa.life < 0.5:
                    life_below_threshold += 1

                # Hotspot detection
                neighbors = grid.get_neighbors(x, y)
                fuel_neighbors = [n for n in neighbors if isinstance(n, FuelAssembly)]
                count = sum(abs(n.life - fa.life) > 0.15 for n in fuel_neighbors)
                if count >= 2:
                    total_hotspot_penalty += 1

        # Symmetry reward
        symmetry_score = self.symmetry_score(grid)

        # Adjust weights dynamically
        total_fuel = sum(1 for y in range(grid.height) for x in range(grid.width)
                         if isinstance(grid.get_fa(x, y), FuelAssembly))
        overheated_pct = overheated_count / total_fuel if total_fuel else 0
        life_pct = 1 - (life_below_threshold / total_fuel) if total_fuel else 1

        if overheated_pct > 0.2:
            self.w_temp *= 1.1
        if life_pct < 0.5:
            self.w_hotspot *= 1.1

        return {
            "temp": total_temp_penalty,
            "hotspot": total_hotspot_penalty,
            "symmetry": symmetry_score,
            "weights": (self.w_temp, self.w_hotspot, self.w_symmetry)
        }

    def symmetry_score(self, grid):
        score = 0
        mid = grid.width // 2  # horizontal symmetry
        for y in range(grid.height):
            for x in range(mid):
                fa1 = grid.get_fa(x, y)
                fa2 = grid.get_fa(grid.width - x - 1, y)
                if not isinstance(fa1, FuelAssembly) or not isinstance(fa2, FuelAssembly):
                    continue
                if fa1.fa_type != fa2.fa_type:
                    score -= 1
                else:
                    score += 1 - abs(fa1.enrichment - fa2.enrichment)
        return score
