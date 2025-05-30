import numpy as np

DEFAULT_WEIGHTS = {
    "total_energy": 3.0,
    "life_uniformity": 1.5,
    "thermal_stability": 1.0,
    "penalties": 5.0
}

# Penalty thresholds
TEMP_LIMIT = 1500  # K
LIFE_THRESHOLD = 0.05  # Fraction
UNUSED_ENRICHMENT_THRESHOLD = 1.0  # Output per enrichment

def compute_fitness(meta_history, grid_history, config=None):
    """
    Computes the fitness score for a fuel assembly layout based on a time-evolving simulation.

    Args:
        meta_history (list[dict]): Simulation meta data over time.
        grid_history (list[list[list[dict]]]): Simulation grid data over time.
        config (dict): Optional config with weights and penalty settings.

    Returns:
        fitness_score (float)
    """

    weights = config.get("weights", DEFAULT_WEIGHTS) if config else DEFAULT_WEIGHTS
    final_meta = meta_history[-1]
    final_grid = grid_history[-1]

    # --- 1. Total Energy Output ---
    total_energy = final_meta.get("total_energy", 0.0)
    max_energy = config.get("reference_max_energy", 2000.0) if config else 2000.0
    energy_score = total_energy / max_energy

    # --- 2. Fuel Life Uniformity ---
    fuel_lives = [
        fa["life"]
        for row in final_grid
        for fa in row
        if fa["type"] == "fuel"
    ]
    life_uniformity_score = 1.0 - np.std(fuel_lives) if fuel_lives else 0.0

    # --- 3. Thermal Stability ---
    fuel_temps = [
        fa["temperature"]
        for row in final_grid
        for fa in row
        if fa["type"] == "fuel"
    ]
    temp_variance = np.var(fuel_temps) if fuel_temps else 1e6
    thermal_stability_score = 1.0 / (1.0 + temp_variance)

    # --- 4. Penalties ---
    overheating_penalty = sum(
        1.0 for row in final_grid for fa in row
        if fa["type"] == "fuel" and fa["temperature"] > TEMP_LIMIT
    )

    dead_fuel_penalty = sum(
        1.0 for row in final_grid for fa in row
        if fa["type"] == "fuel" and fa["life"] < LIFE_THRESHOLD
    )

    unused_enrichment_penalty = sum(
        fa["enrichment"]
        for row in final_grid
        for fa in row
        if fa["type"] == "fuel" and fa.get("total_energy", 0.0) / max(fa["enrichment"], 1e-6) < UNUSED_ENRICHMENT_THRESHOLD
    )

    total_penalty = overheating_penalty + dead_fuel_penalty + unused_enrichment_penalty

    # --- Weighted Score Composition ---
    fitness_score = (
        weights["total_energy"] * energy_score +
        weights["life_uniformity"] * life_uniformity_score +
        weights["thermal_stability"] * thermal_stability_score -
        weights["penalties"] * total_penalty
    )

    return fitness_score
