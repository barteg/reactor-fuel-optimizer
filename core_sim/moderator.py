
import math
import numpy as np
from .base_assembly import FuelAssembly
from .fuel import Fuel

class Moderator(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=600)
        self.type = "moderator"
        self.thermal_power = 1.0

    def update(self, neighbors, flux=0.0):
        weighted_temps = [n.temperature * w for n, w in neighbors if isinstance(n, Fuel)]
        total_weight = sum(w for n, w in neighbors if isinstance(n, Fuel))
        avg_fuel_temp = sum(weighted_temps) / total_weight if total_weight > 0 else 1000.0

        if avg_fuel_temp > 1500:
            self.thermal_power = max(0.1, self.thermal_power - 0.1)
        elif avg_fuel_temp < 1000:
            self.thermal_power = min(2.0, self.thermal_power + 0.1)

        self.temperature = 320

    def influence_on(self, target):
        if isinstance(target, Fuel):
            return {"temp_offset": self.thermal_power * 5.0}
        return {}
