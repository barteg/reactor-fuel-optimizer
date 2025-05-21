def calculate_fa_quality(fa, grid):
    """
    Oblicza jakość FA na podstawie własnych parametrów oraz sąsiadów (8-stronnych).
    Zakłada, że grid to CoreGrid lub 2D numpy array.
    """
    # Obsługa gridu jako obiektu (CoreGrid) lub numpy array
    if hasattr(grid, "grid"):
        grid_array = grid.grid
        size = grid.size
    else:
        grid_array = grid
        size = grid.shape[0]

    if fa.fa_type != "movable":
        return None

    direct_neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    diagonal_neighbors = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    influence = 0.0

    x0, y0 = fa.position

    for dx, dy in direct_neighbors:
        x, y = x0 + dx, y0 + dy
        if 0 <= x < size and 0 <= y < size:
            neighbor = grid_array[x, y]
            if neighbor:
                influence += 1.0 * neighbor.enrichment * (1 - neighbor.life)

    for dx, dy in diagonal_neighbors:
        x, y = x0 + dx, y0 + dy
        if 0 <= x < size and 0 <= y < size:
            neighbor = grid_array[x, y]
            if neighbor:
                influence += 0.5 * neighbor.enrichment * (1 - neighbor.life)

    influence_factor = influence ** 0.7 if influence > 0 else 0

    quality = (fa.enrichment * (1 - fa.life)) + influence_factor
    return quality
