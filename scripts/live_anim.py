import matplotlib.pyplot as plt
import numpy as np
import time
from scripts.layout_loader import load_layout
from core_sim.recorder import Recorder
from models.penalty_model import PenaltyModel
from models.energy_output_model import EnergyOutputModel

# Załaduj layout startowy
layout_path = "../visualization/data/best_layout.json"
grid = load_layout(layout_path)
rows, cols = len(grid), len(grid[0])
print("Typy FA i ich life na starcie:")
for i, row in enumerate(grid):
    for j, cell in enumerate(row):
        print(f"({i},{j}) typ: {cell.type}, life: {getattr(cell,'life',None)}")

penalty_model = PenaltyModel(overheat_temp=620)
energy_output_model = EnergyOutputModel()
recorder = Recorder()

plt.ion()
fig, ax = plt.subplots(figsize=(6, 6))
im = None

step = 0

try:
    while True:
        # PODGRZEWANIE dla testu
        if step < 5:
            grid[0][0].temperature = 700.0

        # Zbieraj dane do historii (opcjonalnie)
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

        # Przygotuj dane do wyświetlenia (tu: life)
        life_map = np.array([[cell.life for cell in row] for row in grid])

        if im is None:
            im = ax.imshow(life_map, cmap="viridis", vmin=0, vmax=1)
            plt.colorbar(im, ax=ax)
            ax.set_title(f"Step {step} | Fitness={fitness:.2f} | Penalty={penalty:.2f}")
        else:
            im.set_data(life_map)
            ax.set_title(f"Step {step} | Fitness={fitness:.2f} | Penalty={penalty:.2f}")

        plt.pause(0.1)  # Czas (s) między klatkami

        # Update grid (pętla po neighbors)
        for i in range(rows):
            for j in range(cols):
                if grid[i][j].type == "fuel":
                    neighbors = []
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols:
                            neighbors.append(grid[ni][nj])
                    grid[i][j].update(neighbors)

        if step % 10 == 0:
            min_life = min(cell.life for row in grid for cell in row if hasattr(cell, "life"))
            max_life = max(cell.life for row in grid for cell in row if hasattr(cell, "life"))
            print(f"Krok {step}: min life = {min_life:.4f}, max life = {max_life:.4f}")

        step += 1
except KeyboardInterrupt:
    print("Animacja zatrzymana ręcznie (Ctrl+C).")
    # Po zakończeniu możesz zapisać historię!
    recorder.save("../visualization/data/live_anim_history.json")
    print("Historia zapisana do visualization/data/live_anim_history.json")
    plt.ioff()
    plt.show()
