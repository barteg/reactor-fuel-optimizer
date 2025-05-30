import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def load_simulation_npz(filepath):
    data = np.load(filepath)
    return data["temperature"], data["energy_output"], data["life"], data["total_energy"]

def animate_full_grid_npz(filepath):
    temperature, energy_output, life, total_energy = load_simulation_npz(filepath)
    timesteps, height, width = temperature.shape

    # Pre-compute total energy per timestep (sum over the 2D grid)
    total_energy_over_time = np.sum(total_energy, axis=(1, 2))

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

    # Line plot for energy over time
    axs[1, 1].set_title("Total Energy vs Time")
    axs[1, 1].set_xlim(0, timesteps)
    axs[1, 1].set_ylim(0, np.max(total_energy_over_time) * 1.1)
    axs[1, 1].set_xlabel("Timestep")
    axs[1, 1].set_ylabel("Total Energy")

    line, = axs[1, 1].plot([], [], color='orange', linewidth=2)

    energy_history = []

    def update(frame):
        im_temp.set_array(temperature[frame])
        im_energy.set_array(energy_output[frame])
        im_life.set_array(life[frame])

        energy_history.append(total_energy_over_time[frame])
        line.set_data(np.arange(len(energy_history)), energy_history)

        for ax in axs.flat:
            ax.set_xlabel(f"Timestep: {frame}")

        return [im_temp, im_energy, im_life, line]

    ani = animation.FuncAnimation(fig, update, frames=timesteps, blit=False, interval=1)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    animate_full_grid_npz("../output/simulation_log.npz")
