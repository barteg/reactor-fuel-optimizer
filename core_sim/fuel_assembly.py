# core_sim/fuel_assembly.py

class FuelAssembly:
    def __init__(self, enrichment=0.0, is_movable=False):
        self.type = "base"
        self.enrichment = enrichment
        self.energy_output = 0.0
        self.temperature = 300.0  # Initial temperature
        self.life = 1.0           # Initial burnup/life state
        self.is_movable = is_movable
        self.total_energy = 0.0

    def update(self, neighbors):
        """Override in subclass: update state over one timestep"""
        pass

    def __repr__(self):
        return f"{self.type[:1].upper()}({self.enrichment:.1f})"

    @property
    def fa_type(self):
        return self.type

# === Subclasses ===

class Fuel(FuelAssembly):
    def __init__(self, enrichment, is_movable=True):
        super().__init__(enrichment, is_movable)
        self.type = "fuel"

    def update(self, neighbors):
        self.energy_output = self.enrichment * self.life * 0.8
        temp_from_output = self.energy_output * 3.5
        avg_neighbor_temp = sum(n.temperature for n in neighbors if n) / len(neighbors)
        neighbor_bonus = avg_neighbor_temp * 0.05 if neighbors else 0.0
        self.temperature = 300 + temp_from_output + neighbor_bonus
        self.life *= 0.995  # Simple burnup model
        self.total_energy += self.energy_output

    @property
    def fa_type(self):
        return "movable"

class ControlRod(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "control_rod"

    def update(self, neighbors):
        self.energy_output = 0.0
        self.temperature = 300.0

    @property
    def fa_type(self):
        return "control_rod"

class Moderator(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "moderator"
        self.temperature = 300.0

    def update(self, neighbors):
        self.temperature = 300.0

    @property
    def fa_type(self):
        return "moderator"

class Blank(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "blank"

    def update(self, neighbors):
        self.temperature = 300.0

    @property
    def fa_type(self):
        return "blank"
