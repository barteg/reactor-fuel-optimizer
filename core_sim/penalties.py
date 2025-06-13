from core_sim.assemblies.empty import FuelAssembly
from optimization.hotspots import compute_hotspots
from optimization.temperature import temperature_penalty
from optimization.symmetry import symmetry_score

class PenaltyCalculator:
    # === Constants ===
    TEMP_LIMIT = 1000.0  # Adjust as needed
    OVERHEAT_THRESHOLD = 620
    TEMP_EXP_SCALE = 50
    LIFE_THRESHOLD = 0.5
    HOTSPOT_LIFE_DIFF = 0.15
    HOTSPOT_NEIGHBOR_COUNT = 2

    def __init__(self):
        self.reset_weights()

    def reset_weights(self):
        self.w_temp = 1.0
        self.w_hotspot = 1.0
        self.w_symmetry = 1.0

    def evaluate(self, grid):
        temp_penalty = self._penalty_temperature(grid)
        hotspot_penalty = self._penalty_hotspots(grid)
        symmetry_score = self._penalty_symmetry(grid)

        # Total weighted penalty score
        total_penalty = (
            self.w_temp * temp_penalty +
            self.w_hotspot * hotspot_penalty -
            self.w_symmetry * symmetry_score
        )

        return {
            "temp": temp_penalty,
            "hotspot": hotspot_penalty,
            "symmetry": symmetry_score,
            "weights": (self.w_temp, self.w_hotspot, self.w_symmetry),
            "total": total_penalty
        }

    def _penalty_temperature(self, grid):
        temperatures = []
        total_fuel = 0

        for y in range(grid.height):
            for x in range(grid.width):
                fa = grid.get_fa(x, y)
                if isinstance(fa, FuelAssembly):
                    temperatures.append(fa.temperature)
                    total_fuel += 1

        total_penalty, overheated_count = temperature_penalty(
            temperatures,
            limit=self.TEMP_LIMIT,
            scale=self.TEMP_EXP_SCALE
        )

        # Dynamic penalty weight adjustment
        overheated_pct = overheated_count / total_fuel if total_fuel else 0
        if overheated_pct > 0.2:
            self.w_temp *= 1.1

        return total_penalty

    def _penalty_hotspots(self, grid):
        life_values = []
        low_life_count = 0
        total_fuel = 0

        for y in range(grid.height):
            for x in range(grid.width):
                fa = grid.get_fa(x, y)
                if isinstance(fa, FuelAssembly):
                    total_fuel += 1
                    life_values.append(fa.life)
                    if fa.life < self.LIFE_THRESHOLD:
                        low_life_count += 1

        # Reset or cap weight increase
        if total_fuel and (low_life_count / total_fuel) > 0.5:
            self.w_hotspot = min(self.w_hotspot * 1.1, 5.0)  # cap max weight to 5
        else:
            self.w_hotspot = 1.0  # reset to default if condition not met

        return compute_hotspots(grid, self.HOTSPOT_LIFE_DIFF)

    def _penalty_symmetry(self, grid):
        return symmetry_score(grid)

    def _compare_symmetry(self, fa1, fa2):
        if not isinstance(fa1, FuelAssembly) or not isinstance(fa2, FuelAssembly):
            return 0
        if fa1.fa_type != fa2.fa_type:
            return -1
        return 1 - abs(fa1.enrichment - fa2.enrichment)
