import random
import copy
import numpy as np
from core_sim.core_layout import generate_random_layout
from core_sim.fusior_solver import simulate_core

class Layout:
    def __init__(self, grid):
        # grid: 2D list/array of FA objects with attributes:
        #   .enrichment (float), .type (str: 'fuel','dummy','control'), .life (0–1)
        self.grid = np.array(grid)
        self.size = self.grid.shape[0]
        self.center = (self.size - 1) / 2

    def enforce_symmetry(self):
        """Mirror the upper-left quadrant across both axes."""
        n = self.size
        for i in range(n):
            for j in range(n):
                # find its mirror positions
                mirrors = {(i, j),
                           (n-1-i, j),
                           (i, n-1-j),
                           (n-1-i, n-1-j)}
                # pick one representative FA (here top-left of the group)
                rep = min(mirrors)
                rep_fa = self.grid[rep]
                for mi, mj in mirrors:
                    self.grid[mi, mj] = copy.deepcopy(rep_fa)

    def evaluate(self):
        # 1) core physics simulation
        fitness, _ = simulate_core(self.grid)

        # 2) aggregate all penalties
        p1 = self._penalty_core_zoning()
        p2 = self._penalty_local_hotspots()
        p3 = self._penalty_coolant_flow()
        p4 = self._penalty_neighbor_influence()
        p5 = self._penalty_edge_enrichment()
        p6 = self._penalty_control_rod_neighbors()
        p7 = self._penalty_life_balancing()

        total_penalty = p1 + p2 + p3 + p4 + p5 + p6 + p7
        return fitness - total_penalty

    def _penalty_core_zoning(self):
        penalty = 0
        inner_r  = self.size * 0.25
        middle_r = self.size * 0.45
        for i in range(self.size):
            for j in range(self.size):
                enr = self.grid[i,j].enrichment
                dist = np.hypot(i - self.center, j - self.center)
                if dist < inner_r:
                    expected, w = 1.6, 5
                elif dist < middle_r:
                    expected, w = 1.4, 3
                else:
                    expected, w = 1.2, 5
                penalty += w * (enr - expected)**2
        return penalty

    def _penalty_local_hotspots(self):
        penalty = 0
        thr = 15
        for i in range(self.size):
            for j in range(self.size):
                local = 0
                for di in (-1,0,1):
                    for dj in (-1,0,1):
                        ni, nj = i+di, j+dj
                        if 0 <= ni < self.size and 0 <= nj < self.size:
                            local += self.grid[ni,nj].enrichment
                if local > thr:
                    penalty += 5 * (local - thr)
        return penalty

    def _penalty_coolant_flow(self):
        penalty = 0
        for i in range(self.size):
            for j in range(self.size):
                fa = self.grid[i,j]
                if fa.type == 'dummy':
                    dcount = 0
                    for di in (-1,0,1):
                        for dj in (-1,0,1):
                            if di==dj==0: continue
                            ni, nj = i+di, j+dj
                            if 0 <= ni < self.size and 0 <= nj < self.size:
                                if self.grid[ni,nj].type == 'dummy':
                                    dcount += 1
                    penalty += 2 * dcount
        return penalty

    def _penalty_neighbor_influence(self):
        penalty = 0
        for i in range(self.size):
            for j in range(self.size):
                infl = 0
                for di in (-1,0,1):
                    for dj in (-1,0,1):
                        if di==dj==0: continue
                        ni, nj = i+di, j+dj
                        if 0 <= ni < self.size and 0 <= nj < self.size:
                            neigh = self.grid[ni,nj]
                            w = 1.0 if abs(di)+abs(dj)==1 else 0.5
                            infl += w * neigh.enrichment * (1 - getattr(neigh,'life',1.0))
                infl = infl**0.7
                if infl > 10: penalty += 2*(infl-10)
                elif infl < 2: penalty += 2*(2-infl)
        return penalty

    def _penalty_edge_enrichment(self):
        penalty = 0
        outer = {0, self.size-1}
        for i in range(self.size):
            for j in range(self.size):
                if i in outer or j in outer:
                    enr = self.grid[i,j].enrichment
                    if enr > 1.3:
                        penalty += 5*(enr - 1.3)
        return penalty

    def _penalty_control_rod_neighbors(self):
        penalty = 0
        for i in range(self.size):
            for j in range(self.size):
                fa = self.grid[i,j]
                if fa.type == 'control':
                    total, cnt = 0, 0
                    for di in (-1,0,1):
                        for dj in (-1,0,1):
                            if di==dj==0: continue
                            ni, nj = i+di, j+dj
                            if 0 <= ni < self.size and 0 <= nj < self.size:
                                total += self.grid[ni,nj].enrichment
                                cnt += 1
                    avg = total/cnt if cnt else 0
                    if avg > 1.6: penalty += 5*(avg-1.6)
                    if avg < 1.2: penalty += 5*(1.2-avg)
        return penalty

    def _penalty_life_balancing(self):
        penalty = 0
        for i in range(self.size):
            for j in range(self.size):
                life = getattr(self.grid[i,j],'life',1.0)
                for di,dj in ((1,0),(0,1)):
                    ni, nj = i+di, j+dj
                    if 0 <= ni < self.size and 0 <= nj < self.size:
                        life_n = getattr(self.grid[ni,nj],'life',1.0)
                        penalty += 3*abs(life-life_n)
        return penalty


class GAOptimizer:
    def __init__(self,
                 population_size=50,
                 generations=100,
                 mutation_rate=0.1,
                 crossover_rate=0.8,
                 layout_size=(10,10),
                 num_fuel_types=3):
        self.population_size = population_size
        self.generations     = generations
        self.mutation_rate   = mutation_rate
        self.crossover_rate  = crossover_rate
        self.layout_size     = layout_size
        self.num_fuel_types  = num_fuel_types

    def initialize_population(self):
        pop = []
        for _ in range(self.population_size):
            grid = generate_random_layout(*self.layout_size, self.num_fuel_types)
            layout = Layout(grid)
            layout.enforce_symmetry()
            pop.append(layout)
        return pop

    def select_parent(self, pop, fits):
        # tournament selection (size=3)
        tour = random.sample(list(zip(pop,fits)), 3)
        tour.sort(key=lambda x: x[1], reverse=True)
        return tour[0][0]

    def crossover(self, p1, p2):
        cp = random.randint(1, self.layout_size[0]-2)
        new_grid = []
        for r in range(self.layout_size[0]):
            row = p1.grid[r] if r < cp else p2.grid[r]
            new_grid.append(copy.deepcopy(row))
        child = Layout(new_grid)
        child.enforce_symmetry()
        return child

    def mutate(self, layout):
        if random.random() < self.mutation_rate:
            r1,c1 = random.randrange(self.layout_size[0]), random.randrange(self.layout_size[1])
            r2,c2 = random.randrange(self.layout_size[0]), random.randrange(self.layout_size[1])
            layout.grid[r1,c1], layout.grid[r2,c2] = layout.grid[r2,c2], layout.grid[r1,c1]
            layout.enforce_symmetry()

    def run(self):
        population = self.initialize_population()
        for gen in range(self.generations):
            fits = [ind.evaluate() for ind in population]
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
            best = max(fits)
            print(f"Gen {gen+1}/{self.generations} best fitness = {best:.2f}")

        fits = [ind.evaluate() for ind in population]
        return population[fits.index(max(fits))]


def run_genetic_algorithm(**kwargs):
    optimizer = GAOptimizer(**kwargs)
    return optimizer.run()
