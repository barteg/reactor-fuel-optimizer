import matplotlib.pyplot as plt
import numpy as np
from core_sim.core_grid import CoreGrid
from core_sim.quality import calculate_fa_quality

def plot_core_grid(core: CoreGrid):
    fig, ax = plt.subplots(figsize=(10, 10))
    fa_types = {
        "movable": "green",
        "control": "red",
        "detector": "blue",
        "dummy": "gray",
        "empty": "white"
    }

    for x in range(core.GRID_SIZE):
        for y in range(core.GRID_SIZE):
            fa = core.get_fa(x, y)
            color = fa_types.get(fa.fa_type, "black")
            ax.add_patch(plt.Rectangle((y, core.GRID_SIZE - 1 - x), 1, 1, color=color))

    ax.set_xlim(0, core.GRID_SIZE)
    ax.set_ylim(0, core.GRID_SIZE)
    ax.set_xticks(np.arange(0, core.GRID_SIZE+1, 1))
    ax.set_yticks(np.arange(0, core.GRID_SIZE+1, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True)
    plt.title("Core Grid Layout")
    plt.show()

def main():
    # Inicjalizacja siatki
    core = CoreGrid()

    # Oblicz jakość kilku przykładowych FA
    example_positions = [(7, 7), (10, 5), (5, 10)]
    for pos in example_positions:
        fa = core.get_fa(*pos)
        if fa and fa.fa_type == "movable":
            quality = calculate_fa_quality(fa, core)
            print(f"FA at {pos}: Quality = {quality:.4f}")

    # Rysuj rdzeń
    plot_core_grid(core)

if __name__ == "__main__":
    main()
