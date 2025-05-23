from .penalties import penalties
from .hotspots import hotspots
from .symmetry import symmetry
from .energy import energy

def fitness(core_grid, w_temp=1.0, w_burnup=1.0, w_symmetry=1.0):
    size = core_grid.width  # lub core_grid.height
    N = size * size
    FA_lifes = [core_grid.get_fa(x, y).life for x in range(size) for y in range(size)]
    FA_energies = [energy(core_grid.get_fa(x, y).life, core_grid.get_fa(x, y).enrichment) for x in range(size) for y in range(size)]
    FA_temperatures = calculate_temperatures(core_grid)

    penalty_temp = penalties(FA_temperatures, FA_lifes)
    penalty_burnup = hotspots(FA_lifes)
    penalty_asymmetry = 1.0 - symmetry(FA_lifes, FA_energies, N)  # 0 = idealnie symetryczne

    fitness_score = -(
        w_temp * penalty_temp +
        w_burnup * penalty_burnup +
        w_symmetry * penalty_asymmetry
    )
    return fitness_score

# -- poniżej funkcja pomocnicza do temperatur --
def calculate_temperatures(core_grid, k=0.1):
    size = core_grid.width  # <- poprawka tutaj!
    temperatures = []
    for x in range(size):
        for y in range(size):
            fa = core_grid.get_fa(x, y)
            own_energy = energy(fa.life, fa.enrichment)
            neighbor_energies = []
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        nfa = core_grid.get_fa(nx, ny)
                        neighbor_energies.append(energy(nfa.life, nfa.enrichment))
            if neighbor_energies:
                mean_neighbor = sum(neighbor_energies) / len(neighbor_energies)
            else:
                mean_neighbor = 0
            T = own_energy + k * mean_neighbor
            temperatures.append(T)
    return temperatures
