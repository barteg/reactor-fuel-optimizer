import json
from core_sim.fuel_assembly import Fuel, ControlRod, Moderator, Blank

def load_layout(path):
    with open(path) as f:
        layout_raw = json.load(f)
    grid = []
    for row in layout_raw:
        grid_row = []
        for cell in row:
            t = cell.get("type")
            if t is None:
                t = "fuel"
            if t == "fuel":
                fa = Fuel(
                    enrichment=cell.get("enrichment", 3.2),
                    is_movable=cell.get("is_movable", True)
                )
                fa.life = cell.get("life", 1.0)
                fa.temperature = cell.get("temperature", 300.0)
                fa.total_energy = cell.get("total_energy", 0.0)
            elif t == "control_rod":
                fa = ControlRod()
                fa.life = cell.get("life", 1.0)
                fa.temperature = cell.get("temperature", 300.0)
            elif t == "moderator":
                fa = Moderator()
                fa.life = cell.get("life", 1.0)
                fa.temperature = cell.get("temperature", 300.0)
            elif t == "blank":
                fa = Blank()
                fa.life = cell.get("life", 1.0)
                fa.temperature = cell.get("temperature", 300.0)
            else:
                fa = Blank()
            grid_row.append(fa)
        grid.append(grid_row)
    return grid

if __name__ == "__main__":
    grid = load_layout("../visualization/data/example_layout.json")
    print("Załadowano grid:", len(grid), "x", len(grid[0]))
    print("FA[0][0]:", grid[0][0], "life:", grid[0][0].life)
