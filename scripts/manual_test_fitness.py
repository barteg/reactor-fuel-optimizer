import random
from core_sim.core import CoreGrid  # zakładam, że masz coś takiego
from core_sim.fitness import compute_fitness  # i funkcje fitness tutaj
from core_sim.constants import MOVABLE_TYPES, CONTROL_TYPES, DUMMY_TYPES, DETECTOR_TYPES, EMPTY_TYPES

def generate_random_core(seed=None):
    if seed is not None:
        random.seed(seed)

    core = CoreGrid(20, 20)

    for y in range(20):
        for x in range(20):
            roll = random.random()
            if roll < 0.7:
                fa_type = 'movable'
                life = round(random.uniform(0.2, 0.8), 2)
                enrichment = random.choice([2.4, 3.6, 4.5])
            elif roll < 0.8:
                fa_type = 'control'
                life = 0.0
                enrichment = 0.0
            elif roll < 0.9:
                fa_type = 'dummy'
                life = 0.0
                enrichment = 0.0
            else:
                fa_type = 'empty'
                life = 0.0
                enrichment = 0.0
            core.set_fuel_assembly(x, y, fa_type=fa_type, life=life, enrichment=enrichment)
    return core

def report_fitness(core):
    print("\n==== Fuel Assembly Types ====")
    for y in range(core.height):
        row = []
        for x in range(core.width):
            fa = core.get_fuel_assembly(x, y)
            if fa is None:
                row.append("  ")
            else:
                row.append(fa.type[:2].upper())
        print(' '.join(row))

    fitness_report = compute_fitness(core, return_components=True)

    print("\n==== Fitness Report ====")
    for key, value in fitness_report.items():
        print(f"{key}: {value:.4f}")

def main():
    for i in range(5):
        print(f"\n\n===== Test case {i+1} =====")
        core = generate_random_core(seed=i)
        report_fitness(core)

if __name__ == "__main__":
    main()
