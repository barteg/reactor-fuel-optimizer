import random
import copy
import json
from optimization.fitness import run_simulation_and_score
from core_sim.core_grid import CoreGrid
import core_sim.assemblies.empty
import os

class Layout:
    def __init__(self, grid):
        self.grid = grid

    def evaluate(self):
        return run_simulation_and_score(self.grid, num_steps=50)

    def enforce_symmetry(self):
        rows = len(self.grid)
        cols = len(self.grid[0])
        for i in range(rows):
            for j in range(cols // 2):
                self.grid[i][cols - j - 1] = copy.deepcopy(self.grid[i][j])

class GAOptimizer:
    def __init__(self, layout_size=(10, 10), population_size=30, generations=20, mutation_rate=0.2, elitism=2):
        self.layout_size = layout_size
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elitism = elitism

    def initialize_population(self):
        pop = []
        for _ in range(self.population_size):
            core = CoreGrid(self.layout_size[0], self.layout_size[1])
            grid = copy.deepcopy(core.grid)
            for i in range(self.layout_size[0]):
                for j in range(self.layout_size[1]):
                    roll = random.random()
                    if roll < 0.7:
                        enr = random.choice([2.4, 3.2, 4.5])
                        fa = core_sim.fuel_assembly.Fuel(enrichment=enr)
                    elif roll < 0.8:
                        fa = core_sim.fuel_assembly.ControlRod()
                    elif roll < 0.9:
                        fa = core_sim.fuel_assembly.Moderator()
                    else:
                        fa = core_sim.fuel_assembly.Blank()
                    grid[i][j] = fa
            layout = Layout(grid)
            layout.enforce_symmetry()
            pop.append(layout)
        return pop

    def crossover(self, parent1, parent2):
        size_x = len(parent1.grid)
        size_y = len(parent1.grid[0])
        grid1 = parent1.grid
        grid2 = parent2.grid
        new_grid = copy.deepcopy(grid1)
        for i in range(size_x):
            for j in range(size_y):
                if random.random() < 0.5:
                    new_grid[i][j] = copy.deepcopy(grid2[i][j])
        child = Layout(new_grid)
        child.enforce_symmetry()
        return child

    def mutate(self, layout):
        size_x = len(layout.grid)
        size_y = len(layout.grid[0])
        # Zamiana miejscami
        if random.random() < self.mutation_rate:
            r1 = random.randrange(size_x)
            c1 = random.randrange(size_y)
            r2 = random.randrange(size_x)
            c2 = random.randrange(size_y)
            layout.grid[r1][c1], layout.grid[r2][c2] = layout.grid[r2][c2], layout.grid[r1][c1]
            layout.enforce_symmetry()
        # Mutacja enrichment
        if random.random() < self.mutation_rate:
            r = random.randrange(size_x)
            c = random.randrange(size_y)
            fa = layout.grid[r][c]
            if hasattr(fa, "enrichment"):
                fa.enrichment = random.choice([2.4, 3.2, 4.5])
        # Mutacja typu FA
        if random.random() < self.mutation_rate:
            r = random.randrange(size_x)
            c = random.randrange(size_y)
            typ = random.choice(["fuel", "control_rod", "moderator", "blank"])
            if typ == "fuel":
                layout.grid[r][c] = core_sim.fuel_assembly.Fuel(enrichment=random.choice([2.4, 3.2, 4.5]))
            elif typ == "control_rod":
                layout.grid[r][c] = core_sim.fuel_assembly.ControlRod()
            elif typ == "moderator":
                layout.grid[r][c] = core_sim.fuel_assembly.Moderator()
            else:
                layout.grid[r][c] = core_sim.fuel_assembly.Blank()

    def select_parents(self, population, fitnesses):
        idx1 = random.randint(0, len(population) - 1)
        idx2 = random.randint(0, len(population) - 1)
        return population[idx1] if fitnesses[idx1] > fitnesses[idx2] else population[idx2]

    def run(self):
        population = self.initialize_population()
        best_layout = None
        best_fitness = float("-inf")

        for gen in range(self.generations):
            fitnesses = [layout.evaluate() for layout in population]
            gen_best_fitness = max(fitnesses)
            gen_best_layout = population[fitnesses.index(gen_best_fitness)]
            print(f"Gen {gen+1}: best_fitness = {gen_best_fitness:.4f}")

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_layout = copy.deepcopy(gen_best_layout)

            sorted_pop = [x for _, x in sorted(zip(fitnesses, population), key=lambda p: -p[0])]
            new_population = sorted_pop[:self.elitism]

            while len(new_population) < self.population_size:
                p1 = self.select_parents(population, fitnesses)
                p2 = self.select_parents(population, fitnesses)
                child = self.crossover(p1, p2)
                self.mutate(child)
                new_population.append(child)

            population = new_population

        # Po zakończeniu zapisujemy najlepszy layout
        def fa_to_dict(fa):
            return {
                "type": getattr(fa, "type", "blank"),
                "life": getattr(fa, "life", 1.0),
                "enrichment": getattr(fa, "enrichment", 0.0),
                "temperature": getattr(fa, "temperature", 300.0),
                "energy_output": getattr(fa, "energy_output", 0.0),
                "total_energy": getattr(fa, "total_energy", 0.0)
            }
        best_grid_dict = [
            [fa_to_dict(best_layout.grid[i][j]) for j in range(self.layout_size[1])]
            for i in range(self.layout_size[0])
        ]
        os.makedirs("visualization/data", exist_ok=True)
        with open("visualization/data/best_layout.json", "w") as f:
            json.dump(best_grid_dict, f, indent=2)
        print("Zapisano najlepszy layout do visualization/data/best_layout.json")

if __name__ == "__main__":
    ga = GAOptimizer(
        layout_size=(10, 10),      # lub (20, 20)
        population_size=20,
        generations=15,
        mutation_rate=0.2,
        elitism=2
    )
    ga.run()
