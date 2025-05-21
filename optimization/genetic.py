import random
import copy
import numpy as np
from core_sim.core_grid import CoreGrid
from optimization.fitness import fitness


class Layout:
    def __init__(self, grid):
        self.grid = grid  # 2D numpy array (CoreGrid.grid)
        self.size = grid.shape[0]

    def enforce_symmetry(self):
        """Mirror the upper-left quadrant across both axes."""
        n = self.size
        for i in range(n):
            for j in range(n):
                mirrors = {
                    (i, j),
                    (n - 1 - i, j),
                    (i, n - 1 - j),
                    (n - 1 - i, n - 1 - j)
                }
                rep = min(mirrors)
                rep_fa = copy.deepcopy(self.grid[rep])
                for mi, mj in mirrors:
                    self.grid[mi, mj] = copy.deepcopy(rep_fa)

    def evaluate(self):
        """Ocena przez nową funkcję fitness."""
        return fitness(self.grid)


class GAOptimizer:
    def __init__(
            self,
            population_size=50,
            generations=100,
            mutation_rate=0.1,
            crossover_rate=0.8,
            layout_size=(20, 20),
            num_fuel_types=3,
            log_to_file=False
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.layout_size = layout_size
        self.num_fuel_types = num_fuel_types
        self.log_to_file = log_to_file

    def initialize_population(self):
        pop = []
        for _ in range(self.population_size):
            # Stwórz losowy układ FA, używając CoreGrid
            core = CoreGrid(size=self.layout_size[0])
            grid = copy.deepcopy(core.grid)
            layout = Layout(grid)
            layout.enforce_symmetry()
            pop.append(layout)
        return pop

    def select_parent(self, pop, fits):
        # Turniej (3 losowych), lepszy wygrywa
        tour = random.sample(list(zip(pop, fits)), 3)
        tour.sort(key=lambda x: x[1], reverse=True)
        return tour[0][0]

    def crossover(self, p1, p2):
        # Prosty crossover: dzielimy rzędy
        cp = random.randint(1, self.layout_size[0] - 2)
        new_grid = []
        for r in range(self.layout_size[0]):
            row = p1.grid[r] if r < cp else p2.grid[r]
            new_grid.append(copy.deepcopy(row))
        child_grid = np.array(new_grid)
        child = Layout(child_grid)
        child.enforce_symmetry()
        return child

    def mutate(self, layout):
        # Zamiana losowych FA miejscami
        if random.random() < self.mutation_rate:
            r1 = random.randrange(self.layout_size[0])
            c1 = random.randrange(self.layout_size[1])
            r2 = random.randrange(self.layout_size[0])
            c2 = random.randrange(self.layout_size[1])
            layout.grid[r1, c1], layout.grid[r2, c2] = layout.grid[r2, c2], layout.grid[r1, c1]
            layout.enforce_symmetry()

    def run(self):
        population = self.initialize_population()
        best_log = []

        for gen in range(self.generations):
            fits = [ind.evaluate() for ind in population]

            if gen == 0:
                idxs = random.sample(range(len(population)), k=3)
                print("\n>>> Smoketest: pierwsza generacja fitnessy <<<")
                for idx in idxs:
                    print(f"  Ind[{idx}].fitness = {fits[idx]:.4f}")
                print(f"  Najlepszy[0] = {max(fits):.4f}\n")

            best_f = max(fits)
            best_log.append((gen + 1, best_f))
            print(f"Gen {gen + 1}/{self.generations} best fitness = {best_f:.2f}")

            new_pop = []
            for _ in range(self.population_size):
                if random.random() < self.crossover_rate:
                    p1 = self.select_parent(population, fits)
                    p2 = self.select_parent(population, fits)
                    child = self.crossover(p1, p2)
                else:
                    child = copy.deepcopy(self.select_parent(population, fits))
                self.mutate(child)
                new_pop.append(child)

            population = new_pop

        fits = [ind.evaluate() for ind in population]
        best_layout = population[int(np.argmax(fits))]

        if self.log_to_file:
            with open("smoketest_log.txt", "w") as f:
                for gen, bf in best_log:
                    f.write(f"Gen {gen}: best_fitness = {bf:.4f}\n")
            print("Log saved to smoketest_log.txt")

        return best_layout


def run_genetic_algorithm(**kwargs):
    optimizer = GAOptimizer(**kwargs)
    return optimizer.run()
