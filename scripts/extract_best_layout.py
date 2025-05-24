import json
import os

history_path = "../visualization/data/simulation_history.json"
output_path = "../visualization/data/best_layout.json"

assert os.path.exists(history_path), f"Nie znaleziono pliku historii: {history_path}"

with open(history_path, "r") as f:
    data = json.load(f)

# Znajdź rekord z najlepszym fitness
best = max(data, key=lambda rec: rec["meta"]["fitness"])
best_grid = best["grid"]

# Diagnostyka: sprawdź wartości life
all_life = [cell["life"] for row in best_grid for cell in row if isinstance(cell, dict) and "life" in cell]
print("Diagnostyka (extract): min life:", min(all_life), "max life:", max(all_life))

with open(output_path, "w") as f:
    json.dump(best_grid, f, indent=2)

print(f"Zapisano najlepszy layout do: {output_path}")
print(f"Najlepszy fitness: {best['meta']['fitness']}")
