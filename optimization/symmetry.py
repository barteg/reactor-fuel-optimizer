def symmetry(FA_lifes, FA_energies, N):
    """
    Ocena symetrii: im bliżej 1, tym bardziej symetryczne.
    """
    symmetry_score = 0
    for i in range(N):
        for j in range(i + 1, N):
            symmetry_score += abs(FA_lifes[i] - FA_lifes[j]) + abs(FA_energies[i] - FA_energies[j])
    return 1 - (1 / (2 * N)) * symmetry_score
