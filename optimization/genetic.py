import random
import copy
from core_sim.core_layout import Layout  # assuming you have a Layout class or similar
from core_sim.core_layout import generate_random_layout
from core_sim.diffusion_solver import simulate_core

class GAOptimizer:
    def __init__(self,
                 population_size=50,
                 generations=100,
                 mutation_rate=0.1,
                 crossover_rate=0.8,
                 layout_size=(10, 10),
                 num_fuel_types=3):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.layout_size = layout_size
        self.num_fuel_types = num_fuel_types

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            grid = generate_random_layout(*self.layout_size, self.num_fuel_types)
            layout = Layout(grid)
            population.append(layout)
        return population

    def select_parent(self, population, fitnesses):
        """Tournament selection."""
        tournament_size = 3
        selected = random.sample(list(zip(population, fitnesses)), tournament_size)
        selected.sort(key=lambda x: x[1], reverse=True)  # Higher fitness is better
        return selected[0][0]

    def crossover(self, parent1, parent2):
        """Simple row-based crossover."""
        size_r = len(parent1.grid)
        crossover_point = random.randint(1, size_r - 2)

        child_grid = []
        for r in range(size_r):
            if r < crossover_point:
                child_grid.append(copy.deepcopy(parent1.grid[r]))
            else:
                child_grid.append(copy.deepcopy(parent2.grid[r]))

        return Layout(child_grid)

    def mutate(self, layout):
        """Randomly swap two fuel assemblies."""
        size_r = len(layout.grid)
        size_c = len(layout.grid[0])

        if random.random() < self.mutation_rate:
            r1, c1 = random.randint(0, size_r-1), random.randint(0, size_c-1)
            r2, c2 = random.randint(0, size_r-1), random.randint(0, size_c-1)
            layout.grid[r1][c1], layout.grid[r2][c2] = layout.grid[r2][c2], layout.grid[r1][c1]

    def run(self):
        population = self.initialize_population()

        for gen in range(self.generations):
            fitnesses = [layout.evaluate() for layout in population]
            next_generation = []

            for _ in range(self.population_size):
                if random.random() < self.crossover_rate:
                    parent1 = self.select_parent(population, fitnesses)
                    parent2 = self.select_parent(population, fitnesses)
                    child = self.crossover(parent1, parent2)
                else:
                    child = copy.deepcopy(self.select_parent(population, fitnesses))

                self.mutate(child)
                next_generation.append(child)

            population = next_generation

            # Optional: print the best score of this generation
            best_fitness = max(fitnesses)
            print(f"Generation {gen+1}: Best fitness = {best_fitness:.2f}")

        # Return the best layout after all generations
        final_fitnesses = [layout.evaluate() for layout in population]
        best_layout = population[final_fitnesses.index(max(final_fitnesses))]
        return best_layout


def run_genetic_algorithm(**kwargs):
    optimizer = GAOptimizer(**kwargs)
    best_layout = optimizer.run()
    return best_layout


class Layout:
    def __init__(self, grid):
        self.grid = grid  # 2D list (or numpy array) of fuel assemblies

    def evaluate(self):
        """
        Calculates the fitness of this layout.
        Combines simulation results and penalty functions.
        """
        fitness, flux_map = simulate_core(self.grid)

        total_penalty = 0
        total_penalty += self.core_zoning_penalty()
        total_penalty += self.local_hotspot_penalty()
        total_penalty += self.coolant_flow_penalty()
        total_penalty += self.neighbor_effect_penalty()
        # (Add more penalties here later)

        total_score = fitness - total_penalty
        return total_score

    def core_zoning_penalty(self):
        """
        Penalizes wrong fuel enrichments in different core zones (inner/middle/outer).
        """
        penalty = 0
        size_r = len(self.grid)
        size_c = len(self.grid[0])
        center_r = size_r / 2
        center_c = size_c / 2

        for r in range(size_r):
            for c in range(size_c):
                fuel = self.grid[r][c]
                enrichment = fuel.enrichment if hasattr(fuel, 'enrichment') else 1.0  # fallback

                dist = ((r - center_r)**2 + (c - center_c)**2)**0.5

                # Example radial zoning thresholds
                if dist < size_r * 0.25:
                    expected = 1.6  # inner zone
                elif dist < size_r * 0.4:
                    expected = 1.4  # middle zone
                else:
                    expected = 1.2  # outer zone

                penalty += (enrichment - expected)**2

        return penalty

    def local_hotspot_penalty(self):
        """
        Penalizes layouts that have too high enrichment in small 3x3 neighborhoods.
        """
        penalty = 0
        size_r = len(self.grid)
        size_c = len(self.grid[0])

        for r in range(1, size_r-1):
            for c in range(1, size_c-1):
                local_sum = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        neighbor = self.grid[r+dr][c+dc]
                        local_sum += neighbor.enrichment if hasattr(neighbor, 'enrichment') else 1.0

                if local_sum > 9:  # arbitrary threshold, adjust based on your data
                    penalty += (local_sum - 9)**2

        return penalty

    def coolant_flow_penalty(self):
        """
        Penalizes clusters of dummies or empty fuel assemblies.
        """
        penalty = 0
        size_r = len(self.grid)
        size_c = len(self.grid[0])

        for r in range(size_r):
            for c in range(size_c):
                fuel = self.grid[r][c]
                if hasattr(fuel, 'type') and fuel.type == 'dummy':
                    neighbors = self.get_neighbors(r, c)
                    dummy_neighbors = sum(1 for f in neighbors if hasattr(f, 'type') and f.type == 'dummy')
                    penalty += dummy_neighbors  # each dummy neighbor adds to penalty

        return penalty

    def neighbor_effect_penalty(self):
        """
        Models neutron streaming effects by neighbor interactions.
        """
        penalty = 0
        size_r = len(self.grid)
        size_c = len(self.grid[0])

        for r in range(size_r):
            for c in range(size_c):
                fuel = self.grid[r][c]
                enrichment = fuel.enrichment if hasattr(fuel, 'enrichment') else 1.0

                neighbors = self.get_neighbors(r, c)

                influence = 0
                for n in neighbors:
                    neighbor_enrichment = n.enrichment if hasattr(n, 'enrichment') else 1.0
                    weight = 1.0 if abs(r-n.r)+abs(c-n.c) == 1 else 0.5
                    influence += weight * neighbor_enrichment

                penalty += influence ** 0.7  # nonlinear scaling

        return penalty

    def get_neighbors(self, r, c):
        """
        Returns neighbors of (r, c) (both direct and diagonal).
        """
        neighbors = []
        size_r = len(self.grid)
        size_c = len(self.grid[0])

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < size_r and 0 <= nc < size_c:
                    neighbors.append(self.grid[nr][nc])
        return neighbors