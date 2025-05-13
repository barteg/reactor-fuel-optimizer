import json
import matplotlib.pyplot as plt
import numpy as np

# Define color for each type
FA_TYPE_COLORS = {
    "fuel": "orange",
    "control_rod": "black",
    "moderator": "blue",
    "blank": "white",
    "invalid": "gray"
}

def load_layout(filepath, timestep=-1):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data["steps"][timestep]["grid"]

import matplotlib.animation as animation

def animate_simulation(steps, interval=300):
    height = len(steps[0]["grid"])
    width = len(steps[0]["grid"][0])

    fig, ax = plt.subplots(figsize=(10, 10))
    image = ax.imshow(np.zeros((height, width, 3)), interpolation='nearest')

    def get_rgb(fa_type):
        color_index = list(FA_TYPE_COLORS.keys()).index(fa_type)
        return plt.get_cmap('tab10')(color_index)[:3]

    def update(frame):
        grid_data = frame["grid"]
        rgb_image = np.zeros((height, width, 3))
        for y in range(height):
            for x in range(width):
                fa = grid_data[y][x]
                fa_type = fa.get("type", "invalid")
                rgb_image[y, x] = get_rgb(fa_type)
        image.set_data(rgb_image)
        ax.set_title(f"Reactor Core Layout - Step {frame['step']}")
        return [image]

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=interval, blit=False)

    # Optional: Save to file
    # ani.save("simulation.gif", writer='pillow')

    plt.show()


    # Create legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=plt.get_cmap('tab10')(i)[:3], label=t)
                       for i, t in enumerate(FA_TYPE_COLORS.keys())]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    with open("../output/simulation_20250513_200917.json", "r") as f:
        data = json.load(f)
    animate_simulation(data["steps"])
