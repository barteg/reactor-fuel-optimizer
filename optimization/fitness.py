# optimization/fitness.py

import numpy as np

# Domyślne wagi (mogą być zmieniane podczas działania)
w1_uniformity = 1.0
w2_hotspots = 1.0
w3_symmetry = 1.0
w4_energy = 1.0
w5_lifetime = 1.0

# Limity bezpieczeństwa
MAX_TEMPERATURE = 620  # °C
MAX_USAGE = 0.95       # Maksymalne zużycie FA
MAX_BURNUP_DIFF = 0.2  # Maksymalna różnica wypalenia

# Stała zamieniająca "pozostałe życie" na temperaturę (prosty model)
LIFE_TO_TEMP_COEFF = 400  # przykładowo: 0.0 → 800°C, 1.0 → 400°C

def calculate_temperature(fa):
    """Szacowanie lokalnej temperatury FA na podstawie życia."""
    return 800 - fa.life * LIFE_TO_TEMP_COEFF

def f_uniformity(grid):
    """Ocena równomierności wypalenia pomiędzy sąsiadami."""
    penalty = 0
    size = grid.size
    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            if fa.fa_type != "movable":
                continue

            neighbors = get_neighbors(grid, x, y)
            for neighbor, weight in neighbors:
                if neighbor.fa_type != "movable":
                    continue
                life_diff = abs(fa.life - neighbor.life)
                penalty += weight * life_diff
    return penalty / (size * size)

def f_hotspots(grid):
    """Penalizacja lokalnych hotspotów."""
    hotspots = 0
    size = grid.size
    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            if fa.fa_type != "movable":
                continue

            temp = calculate_temperature(fa)
            if temp > MAX_TEMPERATURE:
                hotspots += (temp - MAX_TEMPERATURE)
    return hotspots

def f_symmetry(grid):
    """Ocena osiowej symetrii układu."""
    deviation = 0
    size = grid.size
    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            mirror_fa = grid.grid[size - 1 - x, size - 1 - y]
            if fa.fa_type == "movable" and mirror_fa.fa_type == "movable":
                deviation += abs(fa.life - mirror_fa.life)
    return deviation / (size * size)

def f_lifetime(grid):
    """Średnie przewidywane życie FA (im większe, tym lepiej)."""
    total_life = 0
    count = 0
    size = grid.size
    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            if fa.fa_type == "movable":
                total_life += fa.life
                count += 1
    return total_life / count if count else 0

def f_energy(grid):
    """Suma dostępnej energii — model jako suma życia FA."""
    total_energy = 0
    size = grid.size
    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            if fa.fa_type == "movable":
                total_energy += fa.life
    return total_energy

def penalties(grid):
    """Dodatkowe kary za złamanie limitów bezpieczeństwa."""
    penalty = 0
    size = grid.size

    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            if fa.fa_type != "movable":
                continue

            temp = calculate_temperature(fa)
            if temp > MAX_TEMPERATURE:
                penalty += 1000  # Duża kara za przegrzanie

            if (1.0 - fa.life) > MAX_USAGE:
                penalty += 500   # Kara za nadmierne zużycie

            # Sprawdź różnice wypalenia z sąsiadami
            neighbors = get_neighbors(grid, x, y)
            for neighbor, _ in neighbors:
                if neighbor.fa_type != "movable":
                    continue
                burnup_diff = abs(fa.life - neighbor.life)
                if burnup_diff > MAX_BURNUP_DIFF:
                    penalty += 200  # Kara za niejednorodność
    return penalty

def dynamic_weight_adjustment(grid):
    """Dynamiczna adaptacja wag podczas oceny."""
    global w2_hotspots, w1_uniformity, w5_lifetime

    if f_hotspots(grid) > 0:
        w2_hotspots = 2.0  # zwiększ wagę hotspotów

    avg_life = f_lifetime(grid)
    if avg_life < 0.3:
        w5_lifetime = 2.0  # zwiększ wagę życia

    uniformity_penalty = f_uniformity(grid)
    if uniformity_penalty > 0.2:
        w1_uniformity = 2.0  # zwiększ wagę równomierności

def get_neighbors(grid, x, y):
    """Zwraca sąsiadów FA i odpowiadające im wagi."""
    size = grid.size
    neighbors = []

    offsets = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),  # Oś główna
        (-1, -1, 0.5), (-1, 1, 0.5), (1, -1, 0.5), (1, 1, 0.5)  # Ukośne
    ]

    for dx, dy, weight in offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            neighbor = grid.grid[nx, ny]
            neighbors.append((neighbor, weight))
    return neighbors

def fitness(grid):
    """Główna funkcja fitness."""
    # Dynamicznie dostosuj wagi
    dynamic_weight_adjustment(grid)

    f_uni = f_uniformity(grid)
    f_hot = f_hotspots(grid)
    f_sym = f_symmetry(grid)
    f_life = f_lifetime(grid)
    f_en = f_energy(grid)
    penalty = penalties(grid)

    return (
        w1_uniformity * f_uni +
        w2_hotspots * f_hot +
        w3_symmetry * f_sym +
        w5_lifetime * f_life -
        w4_energy * f_en +
        penalty
    )
