def symmetry_score(FA_lifes, FA_energies, grid_size):
    """
    Calculates a horizontal+vertical mirror symmetry score for a square core layout.

    Parameters:
    - FA_lifes (list of float): Life values of fuel assemblies.
    - FA_energies (list of float): Energy outputs of fuel assemblies.
    - grid_size (int): Number of FAs (should be a perfect square).

    Returns:
    - float: Symmetry score between 0.0 (worst) and 1.0 (perfect symmetry).
    """
    size = int(grid_size**0.5)
    assert size * size == grid_size, "Grid must be square."

    total_diff = 0.0
    max_diff = 0.0

    for x in range(size):
        for y in range(size):
            idx = x * size + y
            mirror_x = size - 1 - x
            mirror_y = size - 1 - y
            mirror_idx = mirror_x * size + mirror_y

            life_diff = abs(FA_lifes[idx] - FA_lifes[mirror_idx])
            energy_diff = abs(FA_energies[idx] - FA_energies[mirror_idx])
            total_diff += life_diff + energy_diff
            max_diff += 2  # Max possible difference (each value ∈ [0, 1])

    score = 1.0 - (total_diff / max_diff) if max_diff > 0 else 1.0
    return max(0.0, score)
