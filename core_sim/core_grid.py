import json
import random
from core_sim.fuel_assembly import FuelAssembly, Fuel, ControlRod, Moderator, Blank

class CoreGrid:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.grid = [[Blank() for _ in range(width)] for _ in range(height)]
        self.fixed_positions = set()  # stores (x, y) of special components

    def insert_fa(self, x, y, fa: FuelAssembly):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = fa
            return True
        return False

    def get_fa(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def get_neighbors(self, x, y):
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = [self.get_fa(x + dx, y + dy) for dx, dy in offsets]
        return [n for n in neighbors if n]

    def load_special_layout(self, filepath):
        with open(filepath, 'r') as f:
            layout = json.load(f)

        for item in layout:
            x, y = item['x'], item['y']
            kind = item['type'].lower()
            if kind == 'moderator':
                self.insert_fa(x, y, Moderator())
            elif kind == 'control':
                self.insert_fa(x, y, ControlRod())
            elif kind == 'blank':
                self.insert_fa(x, y, Blank())
            else:
                raise ValueError(f"Unknown assembly type in layout: {kind}")
            self.fixed_positions.add((x, y))

    def initialize_from_layout(self, layout_path):
        self.load_special_layout(layout_path)

        # Fill in remaining positions with Fuel assemblies
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.fixed_positions:
                    enrichment = random.uniform(2.0, 4.5)
                    self.insert_fa(x, y, Fuel(enrichment))

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.grid[y][x]
