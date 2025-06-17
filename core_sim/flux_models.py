import numpy as np
from scipy.ndimage import convolve
from core_sim.core_grid import CoreGrid


def diffusion_approx_flux(grid: CoreGrid, diffusion_coeff: float = 0.2) -> np.ndarray:
    """
    Approximate neutron flux diffusion using a 2D discrete Laplacian.

    Args:
        grid (CoreGrid): The reactor grid object.
        diffusion_coeff (float): Diffusion coefficient controlling how far flux spreads.

    Returns:
        np.ndarray: A (height, width) array representing the neutron flux at each location.
    """
    H, W = grid.height, grid.width
    flux_map = np.zeros((H, W), dtype=np.float64)

    # Step 1: Emitters contribute their neutron yield
    for y in range(H):
        for x in range(W):
            fa = grid.get_fa(x, y)
            if fa:
                flux_map[y, x] = fa.neutron_yield()

    # Step 2: Diffusion via discrete Laplacian
    laplacian_kernel= np.array([
        [1 / 6, 2 / 3, 1 / 6],
        [2 / 3, -10 / 3, 2 / 3],
        [1 / 6, 2 / 3, 1 / 6]
    ], dtype=np.float64)

    # Apply convolution to simulate flux spread
    diffused_flux = flux_map + diffusion_coeff * convolve(flux_map, laplacian_kernel, mode="nearest")

    # Step 3: Apply absorption for each cell
    for y in range(H):
        for x in range(W):
            fa = grid.get_fa(x, y)
            if fa:
                absorption = fa.absorption_factor()
                diffused_flux[y, x] *= (1.0 - absorption)

    return diffused_flux
