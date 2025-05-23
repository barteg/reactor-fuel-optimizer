# simulator.py

from core_sim.core_grid import CoreGrid
from core_sim.penalties import PenaltyCalculator
from optimization.fitness import compute_fitness
from core_sim.recorder import Recorder
from core_sim.fuel_assembly import FuelAssembly
from tqdm import tqdm

class Simulator:
    def __init__(self, grid: CoreGrid, max_timesteps: int = 730, recorder=None):
        self.grid = grid
        self.T = max_timesteps
        self.current_step = 0
        self.recorder = recorder or Recorder((grid.width, grid.height), self.T)
        self.penalty_calculator = PenaltyCalculator()

    def step(self):
        total_energy = 0  # Initialize total energy variable

        for y in range(self.grid.height):  # Changed to .height
            for x in range(self.grid.width):  # Changed to .width
                fa = self.grid.get_fa(x, y)
                if fa is None or not isinstance(fa, FuelAssembly):  # Check for None or invalid type
                    continue  # Skip if fa is not a valid FuelAssembly

                # Update energy output
                fa.energy_output = fa.enrichment * fa.life * 0.8

                # Update temperature
                neighbors = self.grid.get_neighbors(x, y)
                valid_neighbors = [n for n in neighbors if
                                   isinstance(n, FuelAssembly)]  # Only valid FuelAssembly neighbors
                avg_temp = sum(n.temperature for n in valid_neighbors) / len(
                    valid_neighbors) if valid_neighbors else 300.0
                fa.temperature = 300 + fa.energy_output * 3.5 + avg_temp * 0.05
                fa.temperature = min(fa.temperature, 1200)  # Safety cap

                # Decay life
                fa.life *= 0.999

                # Accumulate energy
                fa.total_energy += fa.energy_output
                total_energy += fa.energy_output  # Add to total energy

        self.current_step += 1
        penalties = self.penalty_calculator.evaluate(self.grid)
        fitness = compute_fitness(self.grid, penalties)

        # Pass grid, current_step, penalties, fitness, and total_energy to recorder
        self.recorder.record(self.grid, self.current_step, penalties, fitness, total_energy)

    def run(self):
        for _ in range(self.T):
            self.step()
        self.recorder.export()

    def run(self):
        for _ in tqdm(range(self.T), desc="Running simulation", unit="step"):
            self.step()
        self.recorder.export()