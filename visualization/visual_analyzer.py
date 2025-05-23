import os
import json
import gzip
import matplotlib.pyplot as plt
import numpy as np
from visualize import plot_grid

try:
    import imageio
except ImportError:
    imageio = None

def load_records(path):
    """
    Loads simulation records from JSON or compressed JSON file.
    Assumes format: [ { "grid": ... , "meta": {...} }, ... ]
    """
    if path.endswith(".gz"):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            records = json.load(f)
    else:
        with open(path, 'r') as f:
            records = json.load(f)
    return records

def save_frames(records, property_name='temperature', frames_dir='frames'):
    import os
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    for idx, rec in enumerate(records):
        grid = rec["grid"]
        fname = os.path.join(frames_dir, f"frame_{idx:04d}.png")
        plot_grid(grid, property_name=property_name, title=f"{property_name.title()} Step {idx}", show_colorbar=True)
        plt.savefig(fname)
        plt.close()      # Zamyka wykres po zapisaniu
        # plt.show()     # <-- NIE używaj tego w tej pętli!

def create_gif(frames_dir='frames', output_gif='animation.gif', fps=4):
    """
    Creates a GIF animation from PNG frames.
    """
    if imageio is None:
        raise ImportError("Install 'imageio' to create GIFs: pip install imageio")
    files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.png')])
    images = [imageio.imread(f) for f in files]
    imageio.mimsave(output_gif, images, fps=fps)
    print(f"GIF saved as {output_gif}")

def plot_metrics_over_time(records, output_dir='plots'):
    """
    Plots total_energy, fitness, penalty over time using meta from records.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    total_energy = []
    fitness = []
    penalty = []
    steps = []
    for idx, rec in enumerate(records):
        meta = rec.get("meta", {})
        total_energy.append(meta.get("total_energy", np.nan))
        fitness.append(meta.get("fitness", np.nan))
        penalty.append(meta.get("penalty", np.nan))
        steps.append(meta.get("step", idx))
    # Plot total energy
    plt.figure()
    plt.plot(steps, total_energy, marker='o')
    plt.xlabel('Step')
    plt.ylabel('Total Energy')
    plt.title('Total Energy Over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'total_energy.png'))
    plt.close()
    # Plot fitness
    plt.figure()
    plt.plot(steps, fitness, marker='o', color='g')
    plt.xlabel('Step')
    plt.ylabel('Fitness')
    plt.title('Fitness Over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fitness.png'))
    plt.close()
    # Plot penalty
    plt.figure()
    plt.plot(steps, penalty, marker='o', color='r')
    plt.xlabel('Step')
    plt.ylabel('Penalty')
    plt.title('Penalty Over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'penalty.png'))
    plt.close()

# Test/demo
if __name__ == "__main__":
    path = "data/simulation_history.json"   # <-- ŚCIEŻKA DO TWOJEGO PLIKU
    property_name = "temperature"
    records = load_records(path)
    save_frames(records, property_name=property_name, frames_dir='frames')
    if imageio:
        create_gif(frames_dir='frames', output_gif='animation.gif', fps=3)
    plot_metrics_over_time(records, output_dir='plots')
    print("Analysis complete.")
