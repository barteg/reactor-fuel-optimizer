import numpy as np

def generate_random_layout(size=10, num_fuel_types=3):
    return np.random.randint(0, num_fuel_types, size=(size, size))
