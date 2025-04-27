# visualization/plot_core.py

import matplotlib.pyplot as plt

TYPE_COLOR_MAP = {
    "movable": "yellow",
    "control": "red",
    "detector": "blue",
    "dummy": "gray",
    "empty": "white"
}

def plot_core(grid):
    size = grid.size
    fig, ax = plt.subplots(figsize=(10, 10))

    for x in range(size):
        for y in range(size):
            fa = grid.grid[x, y]
            color = TYPE_COLOR_MAP.get(fa.fa_type, "black")
            rect = plt.Rectangle((y, size - x - 1), 1, 1, facecolor=color, edgecolor="black")
            ax.add_patch(rect)

    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Reactor Core Layout")

    # Dodaj legendę
    handles = [plt.Rectangle((0,0),1,1, color=col) for col in TYPE_COLOR_MAP.values()]
    labels = TYPE_COLOR_MAP.keys()
    ax.legend(handles, labels, loc='upper right')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
