def symmetry(FA_lifes, FA_energies, N):
    """
    Calculate the symmetry score of the FA grid based on life and energy differences.

    Parameters:
    - FA_lifes (list): List of life values for the Fuel Assemblies.
    - FA_energies (list): List of energy values for the Fuel Assemblies.
    - N (int): Total number of Fuel Assemblies (grid size).

    Returns:
    - float: The symmetry score (1.0 means perfect symmetry).
    """
    symmetry_score = 0
    for i in range(N):
        for j in range(i + 1, N):  # To compare only once per pair
            if i != j:
                symmetry_score += abs(FA_lifes[i] - FA_lifes[j]) + abs(FA_energies[i] - FA_energies[j])

    return 1 - (1 / (2 * N)) * symmetry_score
