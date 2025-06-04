import numpy as np
import os
from tqdm import tqdm
from core_sim.flux_models import diffusion_approx_flux
import json
from core_sim.core_grid import CoreGrid
from core_sim.penalties import PenaltyCalculator
from core_sim.fuel_assembly import FuelAssembly
from optimization.fitness import compute_fitness
from core_sim.recorder import Recorder

class Simulator:
    def __init__(self, grid: CoreGrid, max_timesteps, output_path="output/simulation_log.npz", config=None):
        self.grid = grid
        self.T = max_timesteps
        self.current_step = 0
        self.penalty_calculator = PenaltyCalculator()
        self.output_path = output_path
        self.config = config or {}

        self.recorder = Recorder((self.grid.height, self.grid.width), self.T)

        types_grid = [[fa.type if fa else "none" for fa in row] for row in self.grid.grid]
        self.recorder.set_types(types_grid)

        self.temperature_log = []
        self.energy_output_log = []
        self.life_log = []
        self.total_energy_log = []

        self.grid_history = []
        self.meta_history = []

        self.flux_log = []  # Keep to save flux history

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                fa = self.grid.get_fa(x, y)
                if fa and fa.type == "fuel":
                    fa.energy_output = 10.0  # Kickstart

    def step(self):
        flux_map = diffusion_approx_flux(self.grid)
        self.flux_log.append(flux_map)

        total_energy = 0.0

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                fa = self.grid.get_fa(x, y)
                if fa is None or not isinstance(fa, FuelAssembly):
                    continue
                neighbors = self.grid.get_neighbors(x, y)
                fa.update(neighbors=neighbors, flux=flux_map[y][x])
                total_energy += fa.energy_output

        temp_grid = np.array([[fa.temperature if fa else 0.0 for fa in row] for row in self.grid.grid])
        energy_grid = np.array([[fa.energy_output if fa else 0.0 for fa in row] for row in self.grid.grid])
        life_grid = np.array([[fa.life if fa else 0.0 for fa in row] for row in self.grid.grid])
        total_energy_grid = np.full_like(temp_grid, total_energy)

        life_grid = np.array([[fa.life if fa else 0.0 for fa in row] for row in self.grid.grid])

        self.recorder.record(
            temperature=temp_grid,
            energy_output=energy_grid,
            life=life_grid,
            total_energy=total_energy,
            flux=flux_map,
        )

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

        meta_entry = {
            "step": self.current_step,
            "penalties": penalties,
            "fitness": None,
            "total_energy": total_energy
        }
        self.meta_history.append(meta_entry)

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

        self.meta_history[-1]["fitness"] = fitness

        # *** Recorder integration ***
        self.recorder.record(
            temperature=temp_grid,
            energy_output=energy_grid,
            life=life_grid,
            total_energy=total_energy,
            flux=flux_map,
        )

        self.current_step += 1

    def run(self):
        for _ in tqdm(range(self.T), desc="Running simulation", unit="step"):
            self.step()

        final_fitness = self.meta_history[-1]["fitness"]
        print(f"\n[✔] Final fitness score after {self.T} steps: {final_fitness:.4f}")

        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # Prepare data dictionary, convert arrays to lists
        data_to_save = {
            "temperature": [arr.tolist() for arr in self.temperature_log],
            "energy_output": [arr.tolist() for arr in self.energy_output_log],
            "life": [arr.tolist() for arr in self.life_log],
            "total_energy": [arr.tolist() for arr in self.total_energy_log],
            "flux": [arr.tolist() for arr in self.flux_log],
        }

        json_path = self.output_path.replace(".npz", ".json")
        with open(json_path, "w") as f:
            json.dump(data_to_save, f, indent=2)

        # Save detailed snapshots from recorder (assumed to already save JSON)
        recorder_path = self.output_path.replace(".npz", "_snapshots.json")
        self.recorder.save(self.output_path)

        print(f"\n[✔] Simulation saved to {json_path}")
        print(f"[✔] Detailed snapshots saved to {recorder_path}")
