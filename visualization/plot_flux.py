import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate_flux_map(flux_log):
    fig, ax = plt.subplots()
    im = ax.imshow(flux_log[0], cmap='inferno')
    fig.colorbar(im, ax=ax)
    ax.set_title("Neutron Flux Map Over Time")

    def update(frame):
        im.set_array(flux_log[frame])
        ax.set_xlabel(f"Timestep: {frame}")
        return [im]

    ani = animation.FuncAnimation(fig, update, frames=len(flux_log), interval=200, blit=False)
    plt.tight_layout()
    plt.show()
