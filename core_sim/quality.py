from core_sim.fuel_assembly import FuelAssembly
from core_sim.core_grid import CoreGrid

def calculate_fa_quality(fa: FuelAssembly, grid: CoreGrid) -> Optional[float]:
    if fa.fa_type != "movable":
        return None

    direct_neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    diagonal_neighbors = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    influence = 0.0

    for dx, dy in direct_neighbors:
        neighbor = grid.get_fa(fa.position[0] + dx, fa.position[1] + dy)
        if neighbor:
            influence += 1.0 * neighbor.enrichment * (1 - neighbor.life)

    for dx, dy in diagonal_neighbors:
        neighbor = grid.get_fa(fa.position[0] + dx, fa.position[1] + dy)
        if neighbor:
            influence += 0.5 * neighbor.enrichment * (1 - neighbor.life)

    influence_factor = influence ** 0.7

    quality = (fa.enrichment * (1 - fa.life)) + influence_factor
    return quality
