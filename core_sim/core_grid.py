import random
import numpy as np
from typing import Optional
from core_sim.fuel_assembly import FuelAssembly

class CoreGrid:
    GRID_SIZE = 20

    def __init__(self):
        self.grid = np.empty((self.GRID_SIZE, self.GRID_SIZE), dtype=object)
        self._initialize_fixed_fuel_assemblies()
        self._fill_movable_fuel_assemblies()
        self._apply_symmetry()

    def _initialize_fixed_fuel_assemblies(self) -> None:
        fixed_positions = {
            "control": [(5, 5), (5, 14), (14, 5), (14, 14)],
            "detector": [(9, 9), (9, 10), (10, 9), (10, 10)],
            "dummy": [(0, 0), (0, 19), (19, 0), (19, 19)],
            "empty": [(0, 10), (10, 0), (19, 9), (9, 19)],
        }
        for fa_type, positions in fixed_positions.items():
            for x, y in positions:
                self._place_fa((x, y), fa_type, enrichment=0.0, life=1.0)

    def _fill_movable_fuel_assemblies(self) -> None:
        enrichments = [0.024, 0.036, 0.045]
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE):
                if self.grid[x, y] is None:
                    enrichment = random.choice(enrichments)
                    life = random.uniform(0.2, 0.8)
                    self._place_fa((x, y), "movable", enrichment, life)

    def _apply_symmetry(self) -> None:
        center = (self.GRID_SIZE // 2, self.GRID_SIZE // 2)
        for x in range(center[0] + 1):
            for y in range(center[1] + 1):
                original = self.grid[x, y]
                symmetric_positions = [
                    (x, y),
                    (self.GRID_SIZE - 1 - x, y),
                    (x, self.GRID_SIZE - 1 - y),
                    (self.GRID_SIZE - 1 - x, self.GRID_SIZE - 1 - y)
                ]
                for pos in symmetric_positions:
                    self.grid[pos[0], pos[1]] = FuelAssembly(
                        original.fa_type,
                        original.enrichment,
                        original.life,
                        pos
                    )

    def _place_fa(self, position: Tuple[int, int], fa_type: str, enrichment: float, life: float) -> None:
        x, y = position
        self.grid[x, y] = FuelAssembly(fa_type, enrichment, life, position)

    def get_fa(self, x: int, y: int) -> Optional[FuelAssembly]:
        if 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE:
            return self.grid[x, y]
        return None
