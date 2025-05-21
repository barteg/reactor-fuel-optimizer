def symmetry(FA_lifes, FA_energies, N):
    """
    Returns symmetry score between 0 (worst) and 1 (perfect symmetry).
    Compares each cell with its mirror with respect to core center.
    """
    size = int(N**0.5)
    assert size * size == N  # Tylko kwadratowa siatka!
    total_diff = 0.0
    max_diff = 0.0
    for x in range(size):
        for y in range(size):
            idx = x * size + y
            mirror_x = size - 1 - x
            mirror_y = size - 1 - y
            mirror_idx = mirror_x * size + mirror_y
            # Różnice life + energy względem odbicia
            diff = abs(FA_lifes[idx] - FA_lifes[mirror_idx]) + abs(FA_energies[idx] - FA_energies[mirror_idx])
            total_diff += diff
            # Maksymalna możliwa różnica (zakładamy life, energy w [0, 1])
            max_diff += 2  # Maksymalna różnica na jedno pole
    score = 1 - (total_diff / max_diff) if max_diff > 0 else 1
    return max(0.0, score)  # Zawsze w [0, 1]
