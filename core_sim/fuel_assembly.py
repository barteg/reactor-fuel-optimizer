import numpy as np
import math

from sympy.physics.units import temperature


class FuelAssembly:
    def __init__(self, enrichment=0.0, life=1.0, is_movable=False, temperature=300):
        self.type = "base"
        self.enrichment = enrichment
        self.energy_output = 0.0
        self.temperature = temperature
        self.life = life
        self.total_energy = 0.0
        self.is_movable = is_movable

    def update(self, neighbors, flux=0.0):
        pass

    def influence_on(self, other):
        if isinstance(self, ControlRod):
            return {"flux_multiplier": 0.6}
        elif isinstance(self, Moderator):
            return {"flux_multiplier": 1.1}
        elif isinstance(self, Fuel):
            temp_penalty = max(0.8, 1.0 - 0.0005 * (self.temperature - 300))
            burn_penalty = 0.8 + 0.4 * self.life
            return {"flux_multiplier": burn_penalty * temp_penalty}
        else:
            return {"flux_multiplier": 1.0}

    def neutron_yield(self) -> float:
        if self.type == "fuel":
            return self.enrichment * 1.5
        elif self.type == "moderator":
            return 0.1
        elif self.type == "control_rod":
            return 0.0
        return 0.0

    def absorption_factor(self) -> float:
        if self.type == "fuel":
            return 0.7
        elif self.type == "moderator":
            return 0.3
        elif self.type == "control_rod":
            return 1.0
        return 0.0

    def as_dict(self):
        return {
            "type": self.type,
            "fa_type": self.type,
            "enrichment": self.enrichment,
            "temperature": self.temperature,
            "energy_output": self.energy_output,
            "life": self.life,
            "total_energy": self.total_energy
        }

    def __repr__(self):
        return f"{self.type[:1].upper()}({self.enrichment:.1f})"


class Fuel(FuelAssembly):
    def __init__(self, enrichment, life=1.0, is_movable=True):
        super().__init__(enrichment=enrichment, life=life, is_movable=is_movable, temperature=1500)
        self.type = "fuel"
        self.age = 0

    def update(self, neighbors, flux=1.0):
        self.age += 1

        # Let neighbors adjust based on this fuel's current temperature
        for neighbor in neighbors:
            if isinstance(neighbor, Moderator):
                self.temperature += neighbor.thermal_power * 5.0  # Apply influence
            elif isinstance(neighbor, ControlRod):
                self.temperature -= neighbor.thermal_power * 5.0  # Reduce temp if needed

        valid_neighbors = [n for n in neighbors if isinstance(n, FuelAssembly)]
        avg_temp = (
            sum(n.temperature for n in valid_neighbors) / len(valid_neighbors)
            if valid_neighbors else 300.0
        )

        # Calculate flux modifier from neighbors with updated states
        flux_modifier = np.prod([n.influence_on(self).get("flux_multiplier", 1.0) for n in valid_neighbors])
        soft_flux_decay = 1.0 - 0.0002 * self.age
        core_flux = flux * 100
        local_flux = core_flux * flux_modifier * soft_flux_decay
        flux_factor = min(local_flux / core_flux, 1.0)

        # Constants for temperature effect
        T_opt = 1000.0
        sigma_T = 200.0
        gamma = 1.5
        C = 12000.0
        C_th = 5000.0
        cooling_coeff = 40.0
        burn_rate_base = 0.0004

        enrichment_term = gamma * self.enrichment / (1 + gamma * self.enrichment)
        temp_diff = self.temperature - T_opt
        temp_factor = math.exp(-0.5 * (temp_diff / sigma_T) ** 2)

        self.energy_output = flux_factor * self.life * enrichment_term * temp_factor * C

        heating = self.energy_output
        cooling = cooling_coeff * (self.temperature - avg_temp)
        delta_T = (heating - cooling) / C_th
        self.temperature = max(300.0, min(self.temperature + delta_T, 1800.0))

        overheat_factor = 1.0 + max(0, (self.temperature - 600))
        burn_rate = burn_rate_base * overheat_factor
        energy_frac = self.energy_output / C
        self.life = max(0.0, self.life * (1 - burn_rate * energy_frac))
        self.total_energy += self.energy_output

class ControlRod(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=450)
        self.type = "control_rod"
        self.insertion_level = 0.5  # Range: 0 (out) to 1 (fully in)
        self.thermal_power = 1.0    # Acts as a "cooling influence" constant

    def update(self, neighbors, flux=0.0):
        self.temperature = 450

        # React to surrounding fuel temperatures
        fuel_temps = [n.temperature for n in neighbors if isinstance(n, Fuel)]
        if not fuel_temps:
            return

        avg_temp = sum(fuel_temps) / len(fuel_temps)

        if avg_temp > 1600:
            self.insertion_level = min(1.0, self.insertion_level + 0.05)
        elif avg_temp < 1000:
            self.insertion_level = max(0.0, self.insertion_level - 0.05)

    def influence_on(self, other):
        return {
            "flux_multiplier": 1.0 - self.insertion_level * 0.7,
            "temperature_effect": -self.thermal_power * self.insertion_level * 5.0
        }

    def influence_on(self, other):
        # Influence on nearby assemblies via flux multiplier
        return {
            "flux_multiplier": 1.0 - self.insertion_level * 0.7  # up to 70% reduction
        }
    def influence_on(self, target):
        # Control rod reduces flux proportional to insertion level
        flux_multiplier = 1.0 - self.insertion_level * 0.7
        return {"flux_multiplier": flux_multiplier}


class Moderator(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=320)
        self.type = "moderator"
        self.thermal_power = 1.0

    def update(self, neighbors, flux=0.0):
        # Adjust thermal influence factor based on nearby hot fuel
        nearby_fuel_temps = [n.temperature for n in neighbors if isinstance(n, Fuel)]
        avg_fuel_temp = np.mean(nearby_fuel_temps) if nearby_fuel_temps else 1000.0

        # Adjust moderator thermal influence depending on avg fuel temperature
        if avg_fuel_temp > 1500:
            self.thermal_power = max(0.1, self.thermal_power - 0.1)
        elif avg_fuel_temp < 1000:
            self.thermal_power = min(2.0, self.thermal_power + 0.1)

        # Reset temperature
        self.temperature = 320

    def influence_on(self, target):
        if isinstance(target, Fuel):
            # Moderator increases temp by its thermal power
            return {"temp_offset": self.thermal_power * 5.0}
        return {}




class Blank(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=300)
        self.type = "blank"

    def update(self, neighbors, flux=0.0):
        self.temperature = 300
