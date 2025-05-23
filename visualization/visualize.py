import json
import numpy as np
import matplotlib.pyplot as plt

def load_layout(filepath):
    """
    Loads a 2D grid layout from a JSON file.
    Returns: grid (list of list of dict)
    """
    with open(filepath, 'r') as f:
        grid = json.load(f)
    # Weryfikacja: grid to lista list, każda komórka to dict
    rows = len(grid)
    cols = len(grid[0])
    assert all(isinstance(row, list) and len(row) == cols for row in grid), "Grid must be 2D"
    assert all(isinstance(cell, dict) for row in grid for cell in row), "Cells must be dicts"
    return grid

def plot_grid(grid, property_name='temperature', cmap='hot', title=None, show_colorbar=True):
    """
    Plots a heatmap of the chosen property in the fuel assembly grid.

    Args:
        grid: 2D list of dicts representing fuel assemblies
        property_name: string, which property to plot (e.g., 'temperature', 'life', 'enrichment')
        cmap: string, matplotlib colormap
        title: string, plot title
        show_colorbar: bool, whether to show colorbar
    """
    rows = len(grid)
    cols = len(grid[0])
    # Utwórz macierz wartości
    values = np.array([[cell.get(property_name, 0) for cell in row] for row in grid])
    plt.figure(figsize=(cols / 2, rows / 2))
    plt.imshow(values, cmap=cmap, aspect='auto', origin='upper')
    if show_colorbar:
        plt.colorbar(label=property_name)
    plt.xlabel("Column")
    plt.ylabel("Row")
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()

# Test/demo
if __name__ == '__main__':
    # Podmień ścieżkę na swój plik JSON z layoutem!
    test_path = "data/example_layout.json"
    grid = load_layout(test_path)
    plot_grid(grid, property_name='temperature', title="Temperature Map")
    plot_grid(grid, property_name='life', title="Burnup Map", cmap='viridis')
    plot_grid(grid, property_name='enrichment', title="Enrichment Map", cmap='plasma')
