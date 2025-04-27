def penalties(FA_temperatures, FA_lifes, life_threshold=0.95, temperature_threshold=620):
    """
    Calculate penalties for exceeding safety limits, such as temperature and life usage.

    Parameters:
    - FA_temperatures (list): List of temperature values for the FAs.
    - FA_lifes (list): List of life values for the FAs.
    - life_threshold (float): The maximum allowed life usage for FAs (default 0.95).
    - temperature_threshold (float): The maximum allowed temperature for FAs (default 620°C).

    Returns:
    - float: Total penalty for violations of safety limits.
    """
    penalty = 0
    for temp, life in zip(FA_temperatures, FA_lifes):
        if temp > temperature_threshold:
            penalty += 1.0 * (temp - temperature_threshold)  # Exponential penalty can be applied here
        if life > life_threshold:
            penalty += 1.0 * (life - life_threshold)
    return penalty
