# core_sim/fuel_assembly.py

from .base_assembly import FuelAssembly
from core_sim.constants import *
from core_sim.burnup_models import HeuristicBurnupModel  # Default
import math

from ..fuel_burnup import SECONDS_PER_STEP


class Fuel(FuelAssembly):

    def __init__(self, enrichment, life=1.0, is_movable=True, burnup_model=None):
        super().__init__(enrichment=enrichment, life=life, is_movable=is_movable, temperature=800)
        self.type = "fuel"
        self.age = 0
        self.burnup_model = burnup_model or HeuristicBurnupModel()

    def update(self, neighbors, flux=1.0):
        from .moderator import Moderator
        from .control_rod import ControlRod
        from core_sim.fuel_burnup import SECONDS_PER_STEP

        self.age += 1

        # 1. Neighbor thermal influence
        temp_change = 0.0
        for neighbor, weight in neighbors:
            if isinstance(neighbor, Moderator):
                temp_change += neighbor.thermal_power * weight
            elif isinstance(neighbor, ControlRod):
                temp_change -= neighbor.thermal_power * weight

        self.temperature += temp_change

        # 2. Average neighbor temperature (for cooling)
        valid_neighbors = [n for n, _ in neighbors if isinstance(n, FuelAssembly)]
        avg_temp = sum(n.temperature for n in valid_neighbors) / len(valid_neighbors) if valid_neighbors else 300.0

        # 3. Flux modifier from neighbors
        flux_modifier = 1.0
        for n, w in neighbors:
            flux_modifier *= n.influence_on(self).get("flux_multiplier", 1.0) ** w

        # 4. Flux dynamics: sigmoid age factor + life feedback
        # Age sigmoid: ramps up from 0.1 to ~1 over ~100 steps
        k = 0.05  # steepness of ramp
        t0 = 50  # center of ramp (in steps)
        age_factor = 1 / (1 + math.exp(-k * (self.age - t0)))

        # Life feedback: low life = lower energy output
        life_efficiency = 1.0 - math.exp(-3.0 * self.life)

        core_flux = flux * 100  # global flux scaled
        local_flux = core_flux * flux_modifier * age_factor * life_efficiency
        flux_factor = min(local_flux / core_flux, 1.0)

        # 5. Temperature effect: Gaussian around T_OPT
        temp_factor = math.exp(-0.5 * ((self.temperature - T_OPT) / SIGMA_T) ** 2)

        # 6. Energy production
        self.energy_output = flux_factor * self.life * temp_factor * ENERGY_CONSTANT

        # 7. Update temperature from heating/cooling
        heating = self.energy_output
        cooling = COOLING_COEFF * (self.temperature - avg_temp)
        delta_T = (heating - cooling) / THERMAL_CAPACITY
        self.temperature = max(T_MIN, min(self.temperature + delta_T, T_MAX))

        # 8. Life loss using burnup model with correct dt
        life_loss = self.burnup_model.compute_life_loss(self, flux=flux, dt=SECONDS_PER_STEP)
        self.life = max(0.0, self.life - life_loss)

        # 9. Accumulate total energy
        self.total_energy += self.energy_output

