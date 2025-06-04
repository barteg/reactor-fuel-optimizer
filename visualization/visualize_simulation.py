import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json

def load_simulation_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    temperature = np.array(data["temperature"])
    energy_output = np.array(data["energy_output"])
    life = np.array(data["life"])
    total_energy = data["total_energy"]

    # Load static type grid: shape (height, width)
    types = np.array(data["types"])  # e.g., [['fuel', 'moderator', ...], [...], ...]
    return temperature, energy_output, life, total_energy, types


def animate_full_grid_json(filepath):
    temperature, energy_output, life, total_energy, types = load_simulation_json(filepath)
    timesteps, height, width = temperature.shape

    # Build a boolean mask of shape (height, width) where type == 'fuel'
    fuel_mask = (types == "fuel")  # shape: (height, width)
    fuel_mask_expanded = fuel_mask[None, :, :]  # shape: (1, height, width), for broadcasting

    # Pre-compute total energy per timestep
    total_energy_over_time = np.array(total_energy)

    # --- Calculate averages only over fuel cells ---
    num_fuel_cells = np.sum(fuel_mask)
    if num_fuel_cells == 0:
        raise ValueError("No 'fuel' elements found in the type grid.")

    average_temperature_over_time = np.sum(temperature * fuel_mask_expanded, axis=(1, 2)) / num_fuel_cells
    average_life_over_time = np.sum(life * fuel_mask_expanded, axis=(1, 2)) / num_fuel_cells

    # --- Rescaling section without derivative ---
    max_total_energy = np.max(total_energy_over_time)
    if max_total_energy == 0:
        max_total_energy = 1.0

    max_abs_avg_temp = np.max(np.abs(average_temperature_over_time))
    scaled_average_temperature = (
        average_temperature_over_time * (max_total_energy / max_abs_avg_temp)
        if max_abs_avg_temp > 0 else average_temperature_over_time
    )

    max_avg_life = np.max(average_life_over_time)
    scaled_average_life = (
        average_life_over_time * (max_total_energy / max_avg_life)
        if max_avg_life > 0 else average_life_over_time
    )

    # --- Visualization setup without derivative plot ---
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    im_temp = axs[0, 0].imshow(temperature[0], cmap='hot', interpolation='nearest')
    axs[0, 0].set_title("Temperature")
    fig.colorbar(im_temp, ax=axs[0, 0])

    im_energy = axs[0, 1].imshow(energy_output[0], cmap='viridis', interpolation='nearest')
    axs[0, 1].set_title("Energy Output")
    fig.colorbar(im_energy, ax=axs[0, 1])

    im_life = axs[1, 0].imshow(life[0], cmap='cool', interpolation='nearest', vmin=0.0, vmax=1.0)
    axs[1, 0].set_title("Life Remaining")
    fig.colorbar(im_life, ax=axs[1, 0])

    axs[1, 1].set_title("Total Energy, Rescaled Metrics vs Time")
    axs[1, 1].set_xlim(0, timesteps)
    all_values = np.concatenate([total_energy_over_time, scaled_average_temperature, scaled_average_life])
    min_y = np.min(all_values) * 0.9
    max_y = np.max(all_values) * 1.1
    axs[1, 1].set_ylim(min_y, max_y)

    axs[1, 1].set_xlabel("Timestep")
    axs[1, 1].set_ylabel("Scaled Value")

    line_energy, = axs[1, 1].plot([], [], color='orange', linewidth=2, label='Total Energy')
    line_avg_temp, = axs[1, 1].plot([], [], color='crimson', linestyle=':', linewidth=1.5, label='Rescaled Avg. Temp.')
    line_avg_life, = axs[1, 1].plot([], [], color='green', linestyle='-.', linewidth=1.5, label='Rescaled Avg. Life')
    axs[1, 1].legend()

    energy_history = []
    scaled_avg_temp_history = []
    scaled_avg_life_history = []

    def update(frame):
        im_temp.set_array(temperature[frame])
        im_energy.set_array(energy_output[frame])
        im_life.set_array(life[frame])

        energy_history.append(total_energy_over_time[frame])
        scaled_avg_temp_history.append(scaled_average_temperature[frame])
        scaled_avg_life_history.append(scaled_average_life[frame])

        line_energy.set_data(np.arange(len(energy_history)), energy_history)
        line_avg_temp.set_data(np.arange(len(scaled_avg_temp_history)), scaled_avg_temp_history)
        line_avg_life.set_data(np.arange(len(scaled_avg_life_history)), scaled_avg_life_history)

        return [im_temp, im_energy, im_life, line_energy, line_avg_temp, line_avg_life]

    ani = animation.FuncAnimation(fig, update, frames=timesteps, blit=False, interval=1)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    animate_full_grid_json("../output/simulation_log.json")
