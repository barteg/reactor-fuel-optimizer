# optimization_ga/chromosome.py
from copy import deepcopy


class ReactorChromosome:
    """Reprezentacja chromosomu dla algorytmu genetycznego"""

    def __init__(self, base_layout, movable_positions):
        self.base_layout = deepcopy(base_layout)
        self.movable_positions = movable_positions
        self.genes = []  # 1 = Fuel, 0 = Blank

    def to_layout(self):
        """Konwertuj chromosom na layout JSON"""
        layout = deepcopy(self.base_layout)
        grid = layout['grid']

        for i, (x, y) in enumerate(self.movable_positions):
            if self.genes[i] == 1:  # Fuel
                grid[y][x] = {
                    "fa_type": "Fuel",
                    "enrichment": 0.05,
                    "life": 1.0
                }
            else:  # Blank
                grid[y][x] = {
                    "fa_type": "Blank"
                }

        return layout

    def get_fuel_count(self):
        """Zwróć liczbę elementów paliwa"""
        return sum(self.genes)

    def get_fuel_ratio(self):
        """Zwróć stosunek paliwa do wszystkich pozycji"""
        if len(self.genes) == 0:
            return 0
        return self.get_fuel_count() / len(self.genes)