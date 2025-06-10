# core_sim/fuel_burnup.py

import math

# Physical constants
PHI_0 = 1e14               # Reference neutron flux [n/cm²/s]
SIGMA_F = 585e-24          # U-235 fission cross-section [cm²] = 585 barns
N_U235 = 4.5e21            # U-235 number density [atoms/cm³]
ENERGY_PER_FISSION = 3.2e-11  # Energy per fission [J]
SECONDS_PER_STEP = 86400   # 1 timestep = 1 day

def compute_life(flux, dt):
    """Compute the amount of fuel life consumed in a single timestep."""
    phi = flux * PHI_0
    burn = phi * SIGMA_F * dt
    burn = min(burn, 0.1)  # safety clamp
    return burn

def compute_energy_output(initial_density=N_U235, life=1.0):
    """
    Estimate energy produced so far, assuming linear fission of atoms.
    :param initial_density: starting U-235 atom density
    :param life: remaining life fraction (1.0 = unused, 0.0 = spent)
    :return: energy produced per unit volume [J]
    """
    atoms_fissioned = initial_density * (1.0 - life)
    return atoms_fissioned * ENERGY_PER_FISSION
