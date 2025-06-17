# core_sim/core_grid.py

import json
from core_sim.assemblies.base_assembly import FuelAssembly
from core_sim.assemblies.fuel import Fuel
from core_sim.assemblies.empty import Blank
from core_sim.assemblies.moderator import Moderator
from core_sim.assemblies.control_rod import ControlRod

class CoreGrid:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.grid = [[Blank() for _ in range(width)] for _ in range(height)]
        self.fixed_positions = set()  # Positions that are static and should not be overwritten

    # Add this to your CoreGrid class
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


    def insert_fa(self, x, y, fa: FuelAssembly) -> bool:
        """Insert a FuelAssembly at (x, y). Returns True if successful."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = fa
            return True
        return False

    def get_fa(self, x, y):
        """Retrieve the FuelAssembly at (x, y), or None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def get_neighbors(self, x, y):
        offsets_with_weights = [
            (-1, 0, 1.0),  # left
            (1, 0, 1.0),  # right
            (0, -1, 1.0),  # up
            (0, 1, 1.0),  # down
            (-1, -1, 0.4),  # top-left diagonal
            (-1, 1, 0.4),  # bottom-left diagonal
            (1, -1, 0.4),  # top-right diagonal
            (1, 1, 0.4),  # bottom-right diagonal
        ]
        neighbors = []
        for dx, dy, weight in offsets_with_weights:
            fa = self.get_fa(x + dx, y + dy)
            if fa is not None:
                neighbors.append((fa, weight))
        return neighbors

        # diagonal offsets with weight 0.4
        offsets_04 = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in offsets_04:
            neighbor = self.get_fa(x + dx, y + dy)
            if neighbor is not None:
                neighbors.append((neighbor, 0.4))

        return neighbors

    def load_special_layout(self, filepath: str):
        """
        Load static layout (moderators, control rods, blanks) from a JSON file.
        File must contain a list of dicts with keys: 'x', 'y', 'type'.
        """
        with open(filepath, 'r') as f:
            layout = json.load(f)

        for item in layout:
            x, y = item['x'], item['y']
            kind = item['type'].lower()

            if kind == 'moderator':
                fa = Moderator()
            elif kind == 'control':
                fa = ControlRod()
            elif kind == 'blank':
                fa = Blank()
            else:
                raise ValueError(f"Unknown assembly type in layout: {kind}")

            self.insert_fa(x, y, fa)
            self.fixed_positions.add((x, y))

    def set_assembly(self, x: int, y: int, fa_type: str, **kwargs):
        if fa_type == "Fuel":
            self.grid[y][x] = Fuel(**kwargs)
        elif fa_type == "ControlRod":
            self.grid[y][x] = ControlRod()
        elif fa_type == "Moderator":
            self.grid[y][x] = Moderator()
        elif fa_type == "Blank":
            self.grid[y][x] = Blank()
        else:
            raise ValueError(f"Unknown fuel assembly type '{fa_type}' at ({x}, {y})")

    def initialize_from_layout(self, layout_data: dict):
        """
        Initializes the grid based on layout dictionary.
        """
        for y, row in enumerate(layout_data["grid"]):
            for x, cell in enumerate(row):
                if isinstance(cell, str):
                    fa_type = cell
                    params = {}
                elif isinstance(cell, dict):
                    fa_type = cell["fa_type"]
                    params = {k: v for k, v in cell.items() if k != "fa_type"}
                else:
                    raise ValueError(f"Unrecognized cell format at ({x}, {y}): {cell}")

                self.set_assembly(x, y, fa_type, **params)

    def __iter__(self):
        """Allows iteration over the grid, yielding (x, y, FuelAssembly) triples."""
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.grid[y][x]
