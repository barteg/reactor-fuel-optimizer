from core_sim.core_grid import CoreGrid
from optimization.fitness import fitness

def main():
    core = CoreGrid(size=20)
    fit = fitness(core)
    print(f"Fitness of initial core layout: {fit:.4f}")

if __name__ == "__main__":
    main()
