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
    flux = np.array(data["flux"])
    total_energy = data["total_energy"]
    types = np.array(data["types"])

    return temperature, energy_output, life, flux, total_energy, types

def animate_full_grid_json(filepath):
    temperature, energy_output, life, flux, total_energy, types = load_simulation_json(filepath)
    timesteps, height, width = temperature.shape

    type_to_letter = {
        "fuel": "F",
        "moderator": "M",
        "control_rod": "C",
        "blank": "B"
    }

    fuel_mask = (types == "fuel")
    fuel_mask_expanded = fuel_mask[None, :, :]

    num_fuel_cells = np.sum(fuel_mask)
    if num_fuel_cells == 0:
        raise ValueError("No 'fuel' elements found in the type grid.")

    average_temperature_over_time = np.sum(temperature * fuel_mask_expanded, axis=(1, 2)) / num_fuel_cells
    average_life_over_time = np.sum(life * fuel_mask_expanded, axis=(1, 2)) / num_fuel_cells

    total_energy_over_time = np.array(total_energy)
    max_total_energy = np.max(total_energy_over_time) or 1.0
    max_abs_avg_temp = np.max(np.abs(average_temperature_over_time)) or 1.0
    max_avg_life = np.max(average_life_over_time) or 1.0

    scaled_average_temperature = average_temperature_over_time * (max_total_energy / max_abs_avg_temp)
    scaled_average_life = average_life_over_time * (max_total_energy / max_avg_life)

    fig, axs = plt.subplots(3, 2, figsize=(12, 14))  # ← CHANGED to 3 rows

    im_temp = axs[0, 0].imshow(temperature[0], cmap='hot', interpolation='nearest')
    axs[0, 0].set_title("Temperature")
    fig.colorbar(im_temp, ax=axs[0, 0])

    text_grid = []
    for i in range(height):
        row_texts = []
        for j in range(width):
            letter = type_to_letter.get(types[i, j].lower(), "?")
            txt = axs[0, 0].text(j, i, letter, ha='center', va='center',
                                 color='white', fontsize=8, fontweight='bold')
            row_texts.append(txt)
        text_grid.append(row_texts)

    im_energy = axs[0, 1].imshow(energy_output[0], cmap='viridis', interpolation='nearest')
    axs[0, 1].set_title("Energy Output")
    fig.colorbar(im_energy, ax=axs[0, 1])

    im_life = axs[1, 0].imshow(life[0], cmap='cool', interpolation='nearest', vmin=0.0, vmax=1.0)
    axs[1, 0].set_title("Life Remaining")
    fig.colorbar(im_life, ax=axs[1, 0])

    im_flux = axs[1, 1].imshow(flux[0], cmap='plasma', interpolation='nearest')
    axs[1, 1].set_title("Flux")
    fig.colorbar(im_flux, ax=axs[1, 1])

    axs[2, 0].set_title("Total Energy, Rescaled Metrics vs Time")
    axs[2, 0].set_xlim(0, timesteps)
    all_values = np.concatenate([total_energy_over_time, scaled_average_temperature, scaled_average_life])
    min_y = np.min(all_values) * 0.9
    max_y = np.max(all_values) * 1.1
    axs[2, 0].set_ylim(min_y, max_y)
    axs[2, 0].set_xlabel("Timestep")
    axs[2, 0].set_ylabel("Scaled Value")

    line_energy, = axs[2, 0].plot([], [], color='orange', linewidth=2, label='Total Energy')
    line_avg_temp, = axs[2, 0].plot([], [], color='crimson', linestyle=':', linewidth=1.5, label='Rescaled Avg. Temp.')
    line_avg_life, = axs[2, 0].plot([], [], color='green', linestyle='-.', linewidth=1.5, label='Rescaled Avg. Life')
    axs[2, 0].legend()

    axs[2, 1].axis('off')  # Empty or use for stats later

    energy_history = []
    scaled_avg_temp_history = []
    scaled_avg_life_history = []

    def update(frame):
        im_temp.set_array(temperature[frame])
        im_energy.set_array(energy_output[frame])
        im_life.set_array(life[frame])
        im_flux.set_array(flux[frame])

        energy_history.append(total_energy_over_time[frame])
        scaled_avg_temp_history.append(scaled_average_temperature[frame])
        scaled_avg_life_history.append(scaled_average_life[frame])

        line_energy.set_data(np.arange(len(energy_history)), energy_history)
        line_avg_temp.set_data(np.arange(len(scaled_avg_temp_history)), scaled_avg_temp_history)
        line_avg_life.set_data(np.arange(len(scaled_avg_life_history)), scaled_avg_life_history)

        return [im_temp, im_energy, im_life, im_flux, line_energy, line_avg_temp, line_avg_life]

    ani = animation.FuncAnimation(fig, update, frames=timesteps, blit=False, interval=1)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    animate_full_grid_json("../output/single_run_log.json")
