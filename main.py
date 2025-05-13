# main.py

from core_sim.core_grid import CoreGrid
from core_sim.fuel_assembly import Fuel, ControlRod, Moderator, Blank
from core_sim.simulator import Simulator
from core_sim.recorder import Recorder
#from visualization.visualize import plot_static_heatmap, animate_heatmap_over_time
import random

GRID_WIDTH = 30
GRID_HEIGHT = 30
MAX_TIMESTEPS = 730

def initialize_core(width=30, height=30):
    grid = CoreGrid(GRID_WIDTH, GRID_HEIGHT)

    for y in range(height):
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                fa = Moderator
            elif (x % 7 == 0 and y % 5 == 0):
                fa = ControlRod
            elif random.random() < 0.05:
                fa = Blank
            else:
                enrichment = round(random.uniform(2.0, 4.5), 2)
                fa = Fuel(enrichment=enrichment, is_movable=True)

            grid.insert_fa(x, y, fa)

    return grid

def main():
    layout_path = "output/special_layout.json"  # Make sure this path is correct
    grid = CoreGrid(width=30, height=30)
    grid.initialize_from_layout(layout_path)

    recorder = Recorder(grid_shape=(GRID_HEIGHT, GRID_WIDTH), total_steps=MAX_TIMESTEPS)
    simulator = Simulator(grid, recorder=recorder, max_timesteps=730)

    print("⏳ Running simulation...")
    simulator.run()

    recorder.export_path("simulation_log.json")

    print("✅ Simulation complete. Visualizing...")

if __name__ == "__main__":
    main()
