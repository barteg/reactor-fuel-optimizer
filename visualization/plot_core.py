"""
visualization/plot_core.py
Function to graphically display the reactor core layout (20×20) with matplotlib.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Mapping FA types to integer codes
TYPE_CODES = {
    'movable': 0,
    'control': 1,
    'dummy': 2,
    'detector': 3,
    'empty': 4
}
# Color map for codes
COLORS = [
    'green',    # movable
    'blue',     # control
    'gray',     # dummy
    'purple',   # detector
    'white'     # empty
]


def plot_core(core, title: str = "Core Layout"):
    """
    Plot the 20×20 CoreGrid of FuelAssemblies.

    Args:
        core: CoreGrid instance with .grid and .size
        title: Title for the plot
    """
    # Build numeric matrix
    size = core.size
    mat = np.zeros((size, size), dtype=int)
    for x in range(size):
        for y in range(size):
            fa = core.grid[x, y]
            mat[x, y] = TYPE_CODES.get(fa.fa_type, 4)

    # Display
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = plt.matplotlib.colors.ListedColormap(COLORS)
    im = ax.imshow(mat, cmap=cmap, origin='upper')

    # Gridlines
    ax.set_xticks(np.arange(-.5, size, 1), minor=True)
    ax.set_yticks(np.arange(-.5, size, 1), minor=True)
    ax.grid(which='minor', color='black', linewidth=0.5)
    ax.set_xticks([])
    ax.set_yticks([])

    # Legend
    legend_handles = [Patch(color=COLORS[i], label=key) for key, i in TYPE_CODES.items()]
    ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.15, 1))

    ax.set_title(title)
    plt.tight_layout()
    plt.show()
