import unittest
import os
import json
from scripts.layout_loader import load_layout
from core_sim.recorder import Recorder
from models.penalty_model import PenaltyModel
from models.energy_output_model import EnergyOutputModel

class TestFullSimulation(unittest.TestCase):
    def setUp(self):
        self.num_steps = 10
        self.output_path = "visualization/data/simulation_history.json"
        self.layout_path = "visualization/data/example_layout.json"
        # Usuń plik z poprzednich runów, jeśli istnieje
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_simulation_pipeline(self):
        # 1. Załaduj siatkę z pliku example_layout.json!
        grid = load_layout(self.layout_path)
        self.rows = len(grid)
        self.cols = len(grid[0])

        recorder = Recorder()
        penalty_model = PenaltyModel(overheat_temp=620)
        energy_output_model = EnergyOutputModel()

        for step in range(self.num_steps):
            # Przykładowe podgrzewanie FA (dla testu)
            if step < 3:
                grid[0][0].temperature = 700.0

            # Liczenie scoringu/penalty przed update!
            penalty = penalty_model.compute_penalty(grid)
            total_energy = energy_output_model.compute_output(grid)
            fitness = total_energy - penalty

            meta = {
                "step": step,
                "fitness": fitness,
                "penalty": penalty,
                "total_energy": total_energy
            }
            recorder.record(grid, meta=meta)

            # Update FA (z oryginalnej gridy!)
            for i in range(self.rows):
                for j in range(self.cols):
                    neighbors = []
                    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i+di, j+dj
                        if 0 <= ni < self.rows and 0 <= nj < self.cols:
                            neighbors.append(grid[ni][nj])
                    grid[i][j].update(neighbors)

        # Diagnostyka: pokaż min/max life po symulacji
        all_life = [cell.life for row in grid for cell in row]
        print("Diagnostyka life po symulacji: min =", min(all_life), "max =", max(all_life))

        # Zadbaj o istnienie katalogu przed zapisem!
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        recorder.save(self.output_path)

        # Sprawdź, czy plik się utworzył i ma sensowną długość
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, "r") as f:
            data = json.load(f)
        print(f"PATH: {self.output_path}, COUNT: {len(data)}")
        self.assertEqual(len(data), self.num_steps)

if __name__ == "__main__":
    unittest.main()
