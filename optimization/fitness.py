from penalties import penalties
from hotspots import hotspots
from symmetry import symmetry
from energy import energy
import copy

def run_simulation_and_score(core_grid, num_steps=50, w_temp=1.0, w_burnup=1.0, w_symmetry=1.0):
    """
    Przeprowadza symulację zużywania FA przez num_steps kroków i wylicza fitness na końcu.
    """
    import copy
    grid = copy.deepcopy(core_grid)
    size = len(grid)

    for step in range(num_steps):
        # Aktualizacja FA
        for x in range(size):
            for y in range(size):
                fa = grid[x][y]
                neighbors = []
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        neighbors.append(grid[nx][ny])
                fa.update(neighbors)

    # --- Po symulacji oceniaj zużycie i scoring ---
    FA_lifes = [grid[x][y].life for x in range(size) for y in range(size)]
    FA_energies = [energy(grid[x][y].life, grid[x][y].enrichment) for x in range(size) for y in range(size)]
    FA_temperatures = calculate_temperatures_grid(grid)

    penalty_temp = penalties(FA_temperatures, FA_lifes)
    penalty_burnup = hotspots(FA_lifes)
    penalty_asymmetry = 1.0 - symmetry(FA_lifes, FA_energies, size * size)  # 0 = idealnie symetryczne

    fitness_score = -(
        w_temp * penalty_temp +
        w_burnup * penalty_burnup +
        w_symmetry * penalty_asymmetry
    )
    return fitness_score

def calculate_temperatures_grid(grid, k=0.1):
    size = len(grid)
    temperatures = []
    for x in range(size):
        for y in range(size):
            fa = grid[x][y]
            own_energy = energy(fa.life, fa.enrichment)
            neighbor_energies = []
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        nfa = grid[nx][ny]
                        neighbor_energies.append(energy(nfa.life, nfa.enrichment))
            if neighbor_energies:
                mean_neighbor = sum(neighbor_energies) / len(neighbor_energies)
            else:
                mean_neighbor = 0
            T = own_energy + k * mean_neighbor
            temperatures.append(T)
    return temperatures
