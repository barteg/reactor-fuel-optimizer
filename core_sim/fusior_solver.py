import numpy as np

def simulate_core(layout):
    # Placeholder: power = fuel ID (silly model to replace later)
    power_map = layout.astype(float)
    fitness = -np.std(power_map)  # We want smooth power distribution
    return fitness, power_map
