import random
from core_sim.empty import Fuel
from core_sim.recorder import Recorder
from models.penalty_model import PenaltyModel
from models.energy_output_model import EnergyOutputModel

def initialize_grid(rows, cols, enrichment=3.2):
    return [[Fuel(enrichment=enrichment) for _ in range(cols)] for _ in range(rows)]

def overheat_random_fas(grid, num_overheated=5, temp_value=700.0):
    """
    Losowo ustawia wysoką temperaturę w kilku FA na starcie.
    """
    rows, cols = len(grid), len(grid[0])
    positions = [(i, j) for i in range(rows) for j in range(cols)]
    overheated = random.sample(positions, num_overheated)
    for i, j in overheated:
        grid[i][j].temperature = temp_value
    print(f"Przegrzane FA na starcie: {overheated}")
    return overheated

def simulate_one_step(grid):
    """
    Aktualizuje stan wszystkich FA w siatce (aktualizacja sąsiadów).
    """
    rows, cols = len(grid), len(grid[0])
    # Deep copy stanu siatki do odczytu sąsiadów
    old_grid = [[fa for fa in row] for row in grid]
    for i in range(rows):
        for j in range(cols):
            neighbors = []
            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = i+di, j+dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    neighbors.append(old_grid[ni][nj])
            grid[i][j].update(neighbors)
    return grid

def main():
    rows, cols = 10, 10
    num_steps = 50
    num_overheated = 5   # Ile FA ma być przegrzanych na starcie
    overheat_temp = 700.0

    # Przegrzej kilka FA
    grid = initialize_grid(rows, cols)
    overheat_random_fas(grid, num_overheated=num_overheated, temp_value=overheat_temp)

    recorder = Recorder()
    penalty_model = PenaltyModel(overheat_temp=620)
    energy_output_model = EnergyOutputModel()

    # ZAPISZ STAN "STARTOWY" Z PRZEGRZANIEM PRZED PIERWSZYM UPDATE
    penalty = penalty_model.compute_penalty(grid)
    total_energy = energy_output_model.compute_output(grid)
    fitness = total_energy - penalty
    meta = {
        "step": 0,
        "fitness": fitness,
        "penalty": penalty,
        "total_energy": total_energy
    }
    recorder.record(grid, meta=meta)
    print(f"Step 0: Fitness={fitness:.2f}, Penalty={penalty:.2f}, Total Energy={total_energy:.2f}")

    # Potem od step=1:
    for step in range(1, num_steps):
        grid = simulate_one_step(grid)
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
        print(f"Step {step}: Fitness={fitness:.2f}, Penalty={penalty:.2f}, Total Energy={total_energy:.2f}")

    recorder.save("visualization/data/simulation_history.json")
    print("Symulacja zakończona. Historia zapisana.")

if __name__ == "__main__":
    main()
