import numpy as np

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
        super().__init__(enrichment=enrichment, life=life, is_movable=is_movable, temperature=600)
        self.type = "fuel"

    def influence_on(self, other):
        temp_penalty = max(0.8, 1.0 - 0.0005 * (self.temperature - 300))
        burn_penalty = 0.8 + 0.4 * self.life
        return {"flux_multiplier": burn_penalty * temp_penalty, "cooling_effect": -0.5}


    def update(self, neighbors, flux=1.0):
        valid_neighbors = [n for n in neighbors if isinstance(n, FuelAssembly)]
        avg_temp = sum(n.temperature for n in valid_neighbors) / len(valid_neighbors) if valid_neighbors else 300.0

        flux_modifier = 1.0
        cooling_effect_sum = 0.0

        for neighbor in valid_neighbors:
            influence = neighbor.influence_on(self)
            flux_modifier *= influence.get("flux_multiplier", 1.0)
            cooling_effect_sum += influence.get("cooling_effect", 0.0)

        T_opt = 900.0  # Optimal temp for power output (Kelvin)
        alpha = 0.005  # Temperature penalty coefficient (higher to penalize more)
        gamma = 3.0  # Enrichment effectiveness factor
        C = 10000.0  # Energy output scale factor (Watt scale)
        C_th = 10000.0  # Thermal capacity (J/K), per assembly effective
        cooling_coefficient = 50.0  # Heat loss coefficient (W/K)

        local_flux = flux * flux_modifier * 100
        flux_factor = min(local_flux / 100.0, 1.0)

        # Energy output calculation
        enrichment_term = 1 - np.exp(-gamma * self.enrichment)
        temp_ratio = (self.temperature / T_opt) - 1
        temperature_penalty = max(0.0, 1 - alpha * temp_ratio ** 2)
        life_term = self.life
        self.energy_output = flux_factor * life_term * enrichment_term * temperature_penalty * C  # Watts

        # Temperature update
        heating = self.energy_output  # Watts = J/s
        cooling = cooling_coefficient * (self.temperature - avg_temp) + cooling_effect_sum  # Watts
        net_power = heating - cooling  # Watts (J/s)

        # Convert power to temperature change per timestep (1 second)
        delta_T = net_power / C_th  # K per second

        # Update temperature with physical limits
        self.temperature = max(300.0, min(self.temperature + delta_T, 1500.0))

        # Life degradation
        burn_rate = 0.0005 * (1 + flux_factor) * (1 + (self.temperature - 300) / 1000)
        self.life = max(0.0, self.life * (1 - burn_rate))

        self.total_energy += self.energy_output  # Accumulate total energy produced


class ControlRod(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=450)
        self.type = "control_rod"

    def influence_on(self, other):
        return {"flux_multiplier": 0.6, "cooling_effect": -10.0}

    def update(self, neighbors, flux=0.0):
        self.energy_output = 0.0
        self.temperature = 450


class Moderator(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=320)
        self.type = "moderator"

    def influence_on(self, other):
        return {"flux_multiplier": 1.1, "cooling_effect": 2.0}

    def update(self, neighbors, flux=0.0):
        self.temperature = 320


class Blank(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=300)
        self.type = "blank"

    def influence_on(self, other):
        return {"flux_multiplier": 1.0, "cooling_effect": 0.0}

    def update(self, neighbors, flux=0.0):
        self.temperature = 300
