import math

def temperature_penalty(temperatures, limit=620.0, scale=50.0):
    """
    Calculates temperature-based penalties for overheating fuel assemblies.

    Parameters:
    - temperatures (list of float): List of FA temperatures.
    - limit (float): Safe operating temperature threshold.
    - scale (float): Scaling factor for exponential growth of penalty.

    Returns:
    - float: Total overheating penalty.
    - int: Number of overheated assemblies.
    """
    total_penalty = 0.0
    overheated_count = 0

    for temp in temperatures:
        if temp > limit:
            overheated_count += 1
            total_penalty += math.exp((temp - limit) / scale)

    return total_penalty, overheated_count
