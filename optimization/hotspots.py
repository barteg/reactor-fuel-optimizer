def hotspots(core_grid, life_threshold=0.15):
    """
    Kara za hotspoty: duże różnice w 'life' pomiędzy sąsiadami (8-sąsiadów, Moore neighborhood).
    """
    penalty = 0
    size = core_grid.shape[0]
    for x in range(size):
        for y in range(size):
            life_i = core_grid[x, y].life
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < size and 0 <= ny < size:
                        life_j = core_grid[nx, ny].life
                        diff = abs(life_i - life_j)
                        if diff > life_threshold:
                            penalty += diff - life_threshold
    # Każda para liczona podwójnie, dziel przez 2
    return penalty / 2
