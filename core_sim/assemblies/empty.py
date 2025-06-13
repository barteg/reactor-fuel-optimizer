from .base_assembly import FuelAssembly

class Blank(FuelAssembly):
    def __init__(self):
        super().__init__(enrichment=0.0, is_movable=False, temperature=300)
        self.type = "blank"

    def update(self, neighbors, flux=0.0):
        self.temperature = 300
