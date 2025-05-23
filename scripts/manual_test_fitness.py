import random
from core_sim.core_grid import CoreGrid
from core_sim.fuel_assembly import Fuel, ControlRod, Moderator, Blank
from optimization.fitness import fitness

def generate_random_core(seed=None):
    if seed is not None:
        random.seed(seed)

    width, height = 20, 20
    core = CoreGrid(width=width, height=height)
    # Wypełniamy całą siatkę losowymi typami FA
    for y in range(height):
        for x in range(width):
            roll = random.random()
            if roll < 0.7:
                enrichment = random.choice([2.4, 3.6, 4.5])
                fa = Fuel(enrichment)
            elif roll < 0.8:
                fa = ControlRod()
            elif roll < 0.9:
                fa = Moderator()
            else:
                fa = Blank()
            core.insert_fa(x, y, fa)
    return core

def extract_energies_and_temperatures(core):
    energies = []
    temperatures = []
    for y in range(core.height):
        row_e = []
        row_t = []
        for x in range(core.width):
            fa = core.get_fa(x, y)
            row_e.append(getattr(fa, 'energy_output', 0.0))
            row_t.append(getattr(fa, 'temperature', 300.0))
        energies.append(row_e)
        temperatures.append(row_t)
    return energies, temperatures

def report_fitness(core):
    print("\n==== Fuel Assembly Types ====")
    for y in range(core.height):
        row = []
        for x in range(core.width):
            fa = core.get_fa(x, y)
            if fa is None:
                row.append("  ")
            else:
                row.append(fa.fa_type[:2].upper())
        print(' '.join(row))

    FA_energies, FA_temperatures = extract_energies_and_temperatures(core)
    N = core.width  # lub core.height, jeśli kwadratowa

    # Przykładowe wagi (zmodyfikuj wg swojego modelu/fizyki)
    w_uniformity = 1.0
    w_hotspot = 1.0
    w_symmetry = 1.0
    w_lifetime = 1.0
    w_energy = 1.0

    score = fitness(core)
    print("\n==== Fitness ====")
    print(f"Fitness score: {score:.4f}")

def main():
    for i in range(5):
        print(f"\n\n===== Test case {i+1} =====")
        core = generate_random_core(seed=i)
        report_fitness(core)

if __name__ == "__main__":
    main()
