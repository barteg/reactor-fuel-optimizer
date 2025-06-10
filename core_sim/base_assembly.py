
class FuelAssembly:
    def __init__(self, enrichment=0.0, life=1.0, is_movable=False, temperature=400):
        self.type = "base"
        self.enrichment = enrichment
        self.energy_output = 0.0
        self.temperature = temperature
        self.life = life
        self.total_energy = 0.0
        self.is_movable = is_movable

    def update(self, neighbors, flux=0.0):
        total_flux_multiplier = 1.0

        for neighbor, weight in neighbors:
            influence = neighbor.influence_on(self)
            flux_mult = influence.get("flux_multiplier", 1.0)
            total_flux_multiplier += (flux_mult - 1.0) * weight

        effective_flux = flux * total_flux_multiplier

    def influence_on(self, other):
        # Use type string instead of importing classes to avoid circular imports
        if self.type == "control_rod":
            return {"flux_multiplier": 0.6}
        elif self.type == "moderator":
            return {"flux_multiplier": 1.1}
        elif self.type == "fuel":
            temp_penalty = max(0.8, 1.0 - 0.0005 * (self.temperature - 300))
            burn_penalty = 0.8 + 0.4 * self.life
            return {"flux_multiplier": burn_penalty * temp_penalty}
        else:
            return {"flux_multiplier": 1.0}

    def neutron_yield(self):
        return {
            "fuel": self.enrichment * 1.5,
            "moderator": 0.1,
            "control_rod": 0.0,
        }.get(self.type, 0.0)

    def absorption_factor(self):
        return {
            "fuel": 0.7,
            "moderator": 0.3,
            "control_rod": 1.0,
        }.get(self.type, 0.0)

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
