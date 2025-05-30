import numpy as np
import os
from tqdm import tqdm
from urllib3.util.wait import select_wait_for_socket
import math
from core_sim.core_grid import CoreGrid
from core_sim.penalties import PenaltyCalculator
from core_sim.fuel_assembly import FuelAssembly
from optimization.fitness import compute_fitness


class Simulator:
    def __init__(self, grid: CoreGrid, max_timesteps, output_path="output/simulation_log.npz", config=None):
        self.grid = grid
        self.T = max_timesteps
        self.current_step = 0
        self.penalty_calculator = PenaltyCalculator()
        self.output_path = output_path
        self.config = config or {}
        self.flux_log = []

        self.temperature_log = []
        self.energy_output_log = []
        self.life_log = []
        self.total_energy_log = []

        self.grid_history = []
        self.meta_history = []

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                fa = self.grid.get_fa(x, y)
                if fa and fa.type == "fuel":
                    fa.energy_output = 10.0  # Kickstart


    def compute_flux_map(self, sigma=2.0, radius=5):
        height, width = self.grid.height, self.grid.width
        flux_map = np.zeros((height, width))

        for y in range(height):
            for x in range(width):
                emitter = self.grid.get_fa(x, y)
                if emitter is None:
                    continue

                # Material multiplier
                if emitter.type == "fuel":
                    multiplier = 1.0
                elif emitter.type == "moderator":
                    multiplier = 1.1
                elif emitter.type == "control_rod":
                    multiplier = 0.0
                else:
                    multiplier = 0.0

                # Contribute to neighbors within radius
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = x + dx, y + dy
                        if not self.grid.in_bounds(nx, ny):
                            continue

                        r2 = dx * dx + dy * dy
                        weight = math.exp(-r2 / (2 * sigma * sigma))
                        flux_map[ny][nx] += emitter.energy_output * multiplier * weight

        return flux_map
        flux_log.append(np.array(flux_map))

    def step(self):
        flux_map = self.compute_flux_map()
        total_energy = 0.0

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                fa = self.grid.get_fa(x, y)
                if fa is None or not isinstance(fa, FuelAssembly):
                    continue
                neighbors = self.grid.get_neighbors(x, y)
                fa.update(neighbors=neighbors, flux=flux_map[y][x])
                total_energy += fa.energy_output

        # logs (unchanged)
        temp_grid = np.array([[fa.temperature if fa else 0.0 for fa in row] for row in self.grid.grid])
        energy_grid = np.array([[fa.energy_output if fa else 0.0 for fa in row] for row in self.grid.grid])
        life_grid = np.array([[fa.life if fa else 0.0 for fa in row] for row in self.grid.grid])
        total_energy_grid = np.full_like(temp_grid, total_energy)

        self.temperature_log.append(temp_grid)
        self.energy_output_log.append(energy_grid)
        self.life_log.append(life_grid)
        self.total_energy_log.append(total_energy_grid)

        snapshot = [
            [self.grid.get_fa(x, y).as_dict() if self.grid.get_fa(x, y) else None for x in range(self.grid.width)]
            for y in range(self.grid.height)
        ]
        self.grid_history.append(snapshot)

        penalties = self.penalty_calculator.evaluate(self.grid)

        # Append preliminary meta entry without fitness
        self.meta_history.append({
            "step": self.current_step,
            "penalties": penalties,
            "fitness": None,
            "total_energy": total_energy
        })

        # Compute fitness now that meta_history is not empty
        fitness = compute_fitness(self.meta_history, self.grid_history, config={
            "weights": {
                "total_energy": 3.0,
                "life_uniformity": 1.5,
                "thermal_stability": 1.0,
                "penalties": 5.0
            },
            "reference_max_energy": 2500.0,
            "return_breakdown": True
        })

        # Update the last meta entry with the correct fitness
        self.meta_history[-1]["fitness"] = fitness

        self.current_step += 1

    def run(self):
        for _ in tqdm(range(self.T), desc="Running simulation", unit="step"):
            self.step()

        final_fitness = self.meta_history[-1]["fitness"]
        print(f"\n[✔] Final fitness score after {self.T} steps: {final_fitness:.4f}")

        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        np.savez_compressed(
            self.output_path,
            temperature=np.array(self.temperature_log),
            energy_output=np.array(self.energy_output_log),
            life=np.array(self.life_log),
            total_energy=np.array(self.total_energy_log),
            flux=np.array(self.flux_log)
        )
        print(f"\n[✔] Simulation saved to {self.output_path}")
