
# core_sim/core_grid.py

import numpy as np
from core_sim.fuel_assembly import FuelAssembly

class CoreGrid:
    def __init__(self, size=20):
        self.size = size
        self.grid = np.empty((size, size), dtype=object)
        self.fa_counter = 0  # Licznik ID

        self._place_static_fuel_assemblies()
        self._place_movable_fuel_assemblies()

    def _generate_id(self, prefix):
        self.fa_counter += 1
        return f"{prefix}-{self.fa_counter:03d}"

    def _place_static_fuel_assemblies(self):
        """Umieść stałe FA (control, detector, dummy, empty) w realistycznych miejscach."""
        # Przykładowe rozmieszczenie — można rozszerzać
        control_positions = [(9,9), (10,10), (9,10), (10,9)]
        detector_positions = [(0,0), (0,19), (19,0), (19,19)]
        dummy_positions = [(0,10), (19,10), (10,0), (10,19)]
        empty_positions = [(0,5), (5,0), (19,14), (14,19)]

        for x, y in control_positions:
            self.grid[x, y] = FuelAssembly(self._generate_id("C"), "control", 0.0, 1.0, (x, y))

        for x, y in detector_positions:
            self.grid[x, y] = FuelAssembly(self._generate_id("D"), "detector", 0.0, 1.0, (x, y))

        for x, y in dummy_positions:
            self.grid[x, y] = FuelAssembly(self._generate_id("DU"), "dummy", 0.0, 1.0, (x, y))

        for x, y in empty_positions:
            self.grid[x, y] = FuelAssembly(self._generate_id("E"), "empty", 0.0, 1.0, (x, y))

    def _place_movable_fuel_assemblies(self):
        """Umieść ruchome FA losowo z lekko realistycznym rozkładem."""
        center = (self.size - 1) / 2
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x, y] is not None:
                    continue  # Miejsce już zajęte

                # Odległość od środka
                distance = np.sqrt((x - center)**2 + (y - center)**2)

                # Wybór wzbogacenia na podstawie odległości
                if distance < 4:
                    enrichment = 4.5
                elif distance < 7:
                    enrichment = 3.6
                else:
                    enrichment = 2.4

                life = np.random.uniform(0.2, 0.8)

                self.grid[x, y] = FuelAssembly(self._generate_id("M"), "movable", enrichment, life, (x, y))

    def get_all_fuel_assemblies(self):
        """Zwraca listę wszystkich FA."""
        return self.grid.flatten()

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

