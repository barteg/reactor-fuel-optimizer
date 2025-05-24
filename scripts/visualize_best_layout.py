import json
import os
import matplotlib.pyplot as plt
import numpy as np

layout_path = "../visualization/data/best_layout.json"

assert os.path.exists(layout_path), f"Nie znaleziono pliku layoutu: {layout_path}"

with open(layout_path, "r") as f:
    grid = json.load(f)

rows = len(grid)
cols = len(grid[0])

# Przykład: pokaż mapę "life"
life_map = np.array([[cell["life"] if isinstance(cell, dict) and "life" in cell else 0.0 for cell in row] for row in grid])

print("Diagnostyka (wizualizacja): min life =", np.min(life_map), "max life =", np.max(life_map))

plt.figure(figsize=(6, 6))
plt.imshow(life_map, cmap="viridis", interpolation="none")
plt.colorbar(label="Fuel Life")
plt.title("Best Layout – Fuel Life Map")
plt.xlabel("Col")
plt.ylabel("Row")
plt.tight_layout()
plt.savefig("../visualization/data/best_layout_life.png")
plt.show()
print("Wizualizacja zapisana jako: visualization/data/best_layout_life.png")
