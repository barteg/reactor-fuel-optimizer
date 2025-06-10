import math
import numpy as np
from .base_assembly import FuelAssembly
from .constants import *

class Fuel(FuelAssembly):


    def __init__(self, enrichment, life=1.0, is_movable=True):
        super().__init__(enrichment=enrichment, life=life, is_movable=is_movable, temperature=800)
        self.type = "fuel"
        self.age = 0

    def update(self, neighbors, flux=1.0):
        from .moderator import Moderator
        from .control_rod import ControlRod

        self.age += 1
        temp_change = 0.0
        for neighbor, weight in neighbors:
            if isinstance(neighbor, Moderator):
                temp_change += neighbor.thermal_power * 5.0 * weight
            elif isinstance(neighbor, ControlRod):
                temp_change -= neighbor.thermal_power * 5.0 * weight

        self.temperature += temp_change

        valid_neighbors = [n for n, w in neighbors if isinstance(n, FuelAssembly)]
        avg_temp = sum(n.temperature for n in valid_neighbors) / len(valid_neighbors) if valid_neighbors else 300.0

        flux_modifier = 1.0
        for n, w in neighbors:
            flux_modifier *= n.influence_on(self).get("flux_multiplier", 1.0) ** w

        soft_flux_decay = 1.0 - 0.0002 * self.age
        core_flux = flux * 100
        local_flux = core_flux * flux_modifier * soft_flux_decay
        flux_factor = min(local_flux / core_flux, 1.0)

        enrichment_term = GAMMA * self.enrichment / (1 + GAMMA * self.enrichment)
        temp_factor = math.exp(-0.5 * ((self.temperature - T_OPT) / SIGMA_T) ** 2)

        self.energy_output = flux_factor * self.life * enrichment_term * temp_factor * ENERGY_CONSTANT

        heating = self.energy_output
        cooling = COOLING_COEFF * (self.temperature - avg_temp)
        delta_T = (heating - cooling) / THERMAL_CAPACITY
        self.temperature = max(T_MIN, min(self.temperature + delta_T, T_MAX))

        overheat_factor = 1.0 + max(0, (self.temperature - 600))
        burn_rate = BURN_RATE_BASE * overheat_factor
        self.life = max(0.0, self.life * (1 - burn_rate * (self.energy_output / ENERGY_CONSTANT)))
        self.total_energy += self.energy_output