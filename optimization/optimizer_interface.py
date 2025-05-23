# optimizer_interface.py
from core_sim.fuel_assembly import Fuel
from core_sim.recorder import Recorder
from models.penalty_model import PenaltyModel
from models.energy_output_model import EnergyOutputModel
# Możesz dołączyć inne modele (np. temperature_model), jeśli będą potrzebne

def simulate_layout(grid_layout, num_steps=50, overheat_temp=620, enrichment=3.2, record_path=None):
    """
    Uruchamia pełną symulację dla danego layoutu FA.
    Argumenty:
        grid_layout : 2D lista stringów lub typów FA (np. [["fuel", "fuel", ...], ...])
        num_steps : liczba kroków symulacji
        overheat_temp : próg temperatury do penalizacji
        enrichment : domyślne wzbogacenie, jeśli nie podano
        record_path : jeśli podasz, historia symulacji zostanie zapisana do pliku (opcjonalne)
    Zwraca:
        final_fitness : końcowy fitness layoutu po symulacji
        (opcjonalnie: inne metryki z ostatniego kroku)
    """
    rows = len(grid_layout)
    cols = len(grid_layout[0])
    # Tworzymy grid obiektów FA na podstawie podanego layoutu
    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            cell_type = grid_layout[i][j]
            if isinstance(cell_type, Fuel):
                row.append(cell_type)  # już Fuel, użyj bez zmian
            elif cell_type == "fuel":
                row.append(Fuel(enrichment=enrichment))
            else:
                # Tu możesz dodać obsługę innych typów, np. ControlRod, Moderator, Blank
                row.append(Fuel(enrichment=0.0))  # domyślnie fuel z zerowym enrichment
        grid.append(row)

    recorder = Recorder()
    penalty_model = PenaltyModel(overheat_temp=overheat_temp)
    energy_output_model = EnergyOutputModel()

    for step in range(num_steps):
        # --- Update grid ---
        old_grid = [[fa for fa in row] for row in grid]
        for i in range(rows):
            for j in range(cols):
                neighbors = []
                for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ni, nj = i+di, j+dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        neighbors.append(old_grid[ni][nj])
                grid[i][j].update(neighbors)

        # --- Obliczenia scoringu ---
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

    # --- Zapis historii, jeśli chcesz ---
    if record_path is not None:
        recorder.save(record_path)

    # --- Zwracamy końcowy fitness z ostatniego kroku ---
    final_record = recorder.records[-1]["meta"]
    return final_record["fitness"]

# Przykład użycia interfejsu:
if __name__ == "__main__":
    # Przykładowy layout: 5x5 grid, wszystko fuel
    layout = [["fuel"]*5 for _ in range(5)]
    fitness = simulate_layout(layout, num_steps=30, enrichment=3.2)
    print(f"Final fitness for test layout: {fitness:.2f}")
