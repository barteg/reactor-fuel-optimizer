class FuelAssembly:
    def __init__(self, enrichment=0.0, is_movable=False):
        self.type = "base"
        self.enrichment = enrichment
        self.energy_output = 0.0
        self.temperature = 300.0  # Ensure temperature is initialized
        self.life = 1.0
        self.is_movable = is_movable
        self.total_energy = 0.0

    def update(self, neighbors):
        """Override in subclass: update state over one timestep"""
        pass

    def __repr__(self):
        return f"{self.type[:1].upper()}({self.enrichment:.1f})"

    @property
    def fa_type(self):
        return self.type  # Common property to access the type of FuelAssembly


# === Subclasses ===

class Fuel(FuelAssembly):
    def __init__(self, enrichment, is_movable=True):
        super().__init__(enrichment, is_movable)
        self.type = "fuel"

    def update(self, neighbors):
        self.energy_output = self.enrichment * self.life * 0.8
        temp_from_output = self.energy_output * 3.5
        avg_neighbor_temp = sum(n.temperature for n in neighbors if n) / len(neighbors)
        neighbor_bonus = avg_neighbor_temp * 0.05
        self.temperature = 300 + temp_from_output + neighbor_bonus
        self.life *= 0.999
        self.total_energy += self.energy_output

    @property
    def fa_type(self):
        return "fuel"  # Override fa_type for Fuel assemblies


class ControlRod(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "control_rod"

    def update(self, neighbors):
        self.energy_output = 0.0
        self.temperature = 300.0

    @property
    def fa_type(self):
        return "control_rod"  # Override fa_type for ControlRod assemblies


class Moderator(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "moderator"  # Ensure the type is set properly
        self.temperature = 300.0

    def update(self, neighbors):
        self.temperature = 300.0  # Set a default temperature for moderators

    @property
    def fa_type(self):
        return "moderator"  # Return the specific type for Moderator


class Blank(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False)
        self.type = "blank"

    def update(self, neighbors):
        self.temperature = 300.0  # Constant temperature for blanks

    @property
    def fa_type(self):
        return "blank"  # Override fa_type for Blank assemblies
