# core_sim/recorder.py

import json

class Recorder:
    def __init__(self, grid_shape, max_timesteps):
        self.grid_shape = grid_shape
        self.max_timesteps = max_timesteps

        self.temperature_log = []
        self.energy_output_log = []
        self.life_log = []
        self.total_energy_log = []
        self.types = None  # Will be set once
        self.flux_log = []  # 🔧 Add this line
        self.meta_log = []

    def record(self, temperature, energy_output, life, total_energy, flux, meta=None):
        self.temperature_log.append(temperature.tolist())
        self.energy_output_log.append(energy_output.tolist())
        self.life_log.append(life.tolist())
        self.total_energy_log.append(total_energy)
        self.flux_log.append(flux.tolist())
        if meta is not None:
            self.meta_log.append(meta)

    def set_types(self, types_grid):
        """Call this once before running the simulation to store the static type grid."""
        self.types = types_grid

    def save(self, output_path):
        data = {
            "temperature": self.temperature_log,
            "energy_output": self.energy_output_log,
            "life": self.life_log,
            "total_energy": self.total_energy_log,
            "flux": self.flux_log,
            "meta": self.meta_log,
            "types": self.types,  # Add this line
        }
        with open(output_path.replace(".npz", ".json"), "w") as f:
            json.dump(data, f)

