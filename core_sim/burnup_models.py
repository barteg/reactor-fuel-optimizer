# core_sim/burnup_models.py

from abc import ABC, abstractmethod
import math
from core_sim.constants import *
from core_sim.fuel_burnup import compute_life as physical_burn, SECONDS_PER_STEP

class BurnupModel(ABC):
    @abstractmethod
    def compute_life_loss(self, fuel, flux: float, dt: float) -> float:
        """Returns how much to reduce life by."""
        pass


class HeuristicBurnupModel(BurnupModel):
    def compute_life_loss(self, fuel, flux: float, dt: float) -> float:
        overheat_factor = 1.0 + max(0, (fuel.temperature - 600))
        burn_rate = BURN_RATE_BASE * overheat_factor
        return fuel.life * burn_rate * (fuel.energy_output / ENERGY_CONSTANT)


class PhysicsBurnupModel(BurnupModel):
    def compute_life_loss(self, fuel, flux: float, dt: float) -> float:
        return physical_burn(flux, dt)
