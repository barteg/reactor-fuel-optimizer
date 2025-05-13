def hotspots(FA_lifes, life_threshold=0.15):
    """
    Calculate penalties for hotspots, which occur when the difference in life between neighbors exceeds a given threshold.

    Parameters:
    - FA_lifes (list): List of life values for the Fuel Assemblies in the grid.
    - life_threshold (float): The life difference threshold for considering hotspots (default 0.15).

    Returns:
    - float: Total penalty for hotspots.
    """
    penalty = 0
    for i, life_i in enumerate(FA_lifes):
        for j, life_j in enumerate(FA_lifes):
            if i != j and abs(life_i - life_j) > life_threshold:
                penalty += abs(life_i - life_j) - life_threshold
    return penalty
