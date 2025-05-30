from core_sim.fuel_assembly import FuelAssembly
def compute_hotspots(grid, life_threshold=0.15):
    penalty = 0
    for y in range(grid.height):
        for x in range(grid.width):
            fa = grid.get_fa(x, y)
            if not isinstance(fa, FuelAssembly):
                continue
            life_i = fa.life

            # Check neighbors: up, down, left, right
            neighbors = []
            if x > 0:
                neighbors.append(grid.get_fa(x-1, y))
            if x < grid.width - 1:
                neighbors.append(grid.get_fa(x+1, y))
            if y > 0:
                neighbors.append(grid.get_fa(x, y-1))
            if y < grid.height - 1:
                neighbors.append(grid.get_fa(x, y+1))

            for neighbor in neighbors:
                if not isinstance(neighbor, FuelAssembly):
                    continue
                life_j = neighbor.life
                diff = abs(life_i - life_j)
                if diff > life_threshold:
                    penalty += diff - life_threshold

    # Since each pair counted twice (i,j and j,i), divide penalty by 2
    return penalty / 2
