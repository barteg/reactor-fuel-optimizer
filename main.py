from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator
from core_sim.recorder import Recorder
from core_sim.penalties import PenaltyCalculator
from layout_utils.load_layout import load_layout
from visualization.plot_flux import animate_flux_map
MAX_TIMESTEPS = 1000

def main():
    layout_path = "layouts/test_layout.json"
    log_path = "output/simulation_log.json"

    # Load layout from JSON file
    layout = load_layout(layout_path)

    # Initialize CoreGrid with loaded layout dimensions
    grid = CoreGrid(width=layout["width"], height=layout["height"])
    grid.initialize_from_layout(layout)

    # Set up recorder and simulator
    recorder = Recorder(grid_shape=(layout["height"], layout["width"]), total_steps=MAX_TIMESTEPS)
    sim = Simulator(grid=grid, max_timesteps=MAX_TIMESTEPS, config={
        "weights": {
            "total_energy": 3.0,
            "life_uniformity": 1.5,
            "thermal_stability": 1.0,
            "penalties": 5.0
        },
        "reference_max_energy": 2500.0,
        "return_breakdown": True
    })
    sim.run()

    print("⏳ Running simulation...")

    # Export simulation log
    recorder.save(log_path)
    print("✅ Simulation complete.")

    # Evaluate penalties on final grid state
    penalty_calc = PenaltyCalculator()
    penalties = penalty_calc.evaluate(grid)

    print("🔎 Final penalty breakdown:")
    print(f"  🔥 Temperature Penalty: {penalties['temp']:.4f}")
    print(f"  🌡️ Hotspot Penalty:     {penalties['hotspot']:.4f}")
    print(f"  🪞 Symmetry Score:      {penalties['symmetry']:.4f}")
    print(f"  ⚖️ Weights:              {penalties['weights']}")
if __name__ == "__main__":
    main()
