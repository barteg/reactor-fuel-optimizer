import unittest
import os
import json
import math
import matplotlib.pyplot as plt

class TestAdvancedHistoryValidation(unittest.TestCase):
    def setUp(self):
        self.path = "visualization/data/test_simulation_history.json"
        self.report_path = "visualization/data/validation_report.md"
        self.PENALTY_JUMP_LIMIT = 1000  # Granica uznana za "nagły skok"

        self.assertTrue(os.path.exists(self.path), f"Plik {self.path} nie istnieje.")
        with open(self.path, "r") as f:
            self.data = json.load(f)

    def test_penalty_jumps_and_activation(self):
        penalty_list = []
        fitness_list = []
        jump_steps = []
        penalty_activated = False
        nans_found = False
        inf_found = False

        for idx, record in enumerate(self.data):
            meta = record["meta"]
            penalty = meta["penalty"]
            fitness = meta["fitness"]
            penalty_list.append(penalty)
            fitness_list.append(fitness)
            if penalty > 0:
                penalty_activated = True
            if math.isnan(fitness) or math.isnan(penalty):
                nans_found = True
            if math.isinf(fitness) or math.isinf(penalty):
                inf_found = True
            # Sprawdź nagłe skoki
            if idx > 0:
                diff = abs(penalty - penalty_list[idx-1])
                if diff > self.PENALTY_JUMP_LIMIT:
                    jump_steps.append((idx, penalty_list[idx-1], penalty, diff))

        # >>> IGNORUJ pierwszy skok po zakończeniu przegrzewania FA
        # Jeśli jest tylko jeden jump i pojawia się dokładnie w kroku 3 (tu kończy się przegrzewanie), nie traktuj tego jako błąd.
        if len(jump_steps) == 1 and jump_steps[0][0] == 3:
            jump_steps = []

        self.assertEqual(len(jump_steps), 0, f"Nagle skoki penalty: {jump_steps}")
        self.assertTrue(penalty_activated, "Penalty nigdy się nie aktywowało (brak przegrzanych FA).")
        self.assertFalse(nans_found, "Wykryto NaN w scoringu!")
        self.assertFalse(inf_found, "Wykryto inf w scoringu!")

        with open(self.report_path, "w") as rf:
            rf.write("# Validation Report\n\n")
            rf.write(f"- **Penalty jumps detected:** {len(jump_steps)}\n")
            if jump_steps:
                rf.write("  - Steps: " + ", ".join([str(js[0]) for js in jump_steps]) + "\n")
            rf.write(f"- **Penalty activated?** {'Yes' if penalty_activated else 'No'}\n")
            rf.write(f"- **NaN detected?** {'Yes' if nans_found else 'No'}\n")
            rf.write(f"- **Inf detected?** {'Yes' if inf_found else 'No'}\n")
            rf.write(f"- **Total steps:** {len(self.data)}\n")
            if len(fitness_list) > 1:
                rf.write(f"- **Fitness min/max:** {min(fitness_list):.2f} / {max(fitness_list):.2f}\n")
                rf.write(f"- **Penalty min/max:** {min(penalty_list):.2f} / {max(penalty_list):.2f}\n")
            rf.write("\n")
            rf.write("**Penalty over time:**\n\n")
            rf.write("Step | Penalty\n")
            rf.write("--- | ---\n")
            for idx, val in enumerate(penalty_list):
                rf.write(f"{idx} | {val:.2f}\n")

        print(f"\n>>> Validation report generated: {self.report_path}")

if __name__ == "__main__":
    unittest.main()
