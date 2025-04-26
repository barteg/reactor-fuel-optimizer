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
