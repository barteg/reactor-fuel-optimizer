from .base_assembly import FuelAssembly
from .fuel import Fuel

class ControlRod(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=500)
        self.type = "control_rod"
        self.insertion_level = 0.5  # Range: 0 (out) to 1 (fully in)
        self.thermal_power = 1.0    # Acts as a "cooling influence" constant

    def update(self, neighbors, flux=0.0):
        self.temperature = 450

        weighted_temps = [n.temperature * w for n, w in neighbors if isinstance(n, Fuel)]
        total_weight = sum(w for n, w in neighbors if isinstance(n, Fuel))

        if total_weight == 0:
            return

        avg_temp = sum(weighted_temps) / total_weight

        if avg_temp > 1600:
            self.insertion_level = min(1.0, self.insertion_level + 0.05)
        elif avg_temp < 1000:
            self.insertion_level = max(0.0, self.insertion_level - 0.05)

    def influence_on(self, target):
        # Control rod reduces flux proportional to insertion level
        flux_multiplier = 1.0 - self.insertion_level * 0.7
        return {"flux_multiplier": flux_multiplier}