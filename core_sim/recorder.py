import os
import json
from datetime import datetime
from core_sim.fuel_assembly import FuelAssembly

class Recorder:
    def __init__(self, grid_shape, total_steps, export_path=None):
        self.grid_shape = grid_shape
        self.total_steps = total_steps
        self.records = []
        self.export_path = export_path or self._default_export_path()

    def _default_export_path(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"output/simulation_{now}.json"

    def record(self, grid, step, penalties, fitness, total_energy):
        grid_data = []
        for row in grid:
            grid_row = []
            for fa in row:
                if isinstance(fa, FuelAssembly):
                    grid_row.append({
                        "type": fa.fa_type,
                        "enrichment": fa.enrichment,
                        "life": fa.life,
                        "temperature": fa.temperature,
                        "energy_output": fa.energy_output,
                        "total_energy": fa.total_energy,
                        "is_movable": fa.is_movable
                    })
                else:
                    grid_row.append({
                        "type": "invalid",
                        "enrichment": None,
                        "life": None,
                        "temperature": None,
                        "energy_output": None,
                        "total_energy": None,
                        "is_movable": None
                    })
            grid_data.append(grid_row)

        self.records.append({
            "step": step,
            "grid": grid_data,
            "fitness": fitness,
            "penalties": penalties,
            "total_energy": total_energy
        })

    def export(self):
        def make_json_safe(obj):
            """Recursively sanitize objects for JSON export."""
            if isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            elif isinstance(obj, dict):
                return {k: make_json_safe(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_safe(v) for v in obj]
            elif hasattr(obj, '__dict__'):
                return make_json_safe(vars(obj))
            elif isinstance(obj, tuple):
                return tuple(make_json_safe(v) for v in obj)
            else:
                return str(obj)  # Fallback for unknown types

        output = make_json_safe({
            "grid_shape": self.grid_shape,
            "total_steps": self.total_steps,
            "steps": self.records
        })

        export_dir = os.path.dirname(self.export_path)
        if export_dir:
            os.makedirs(export_dir, exist_ok=True)

        with open(self.export_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Simulation data exported to: {self.export_path}")
