import argparse
import os
import json
from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator
from layout_utils.load_layout import load_layout
from optimization.batch_runner import evaluate_layouts_in_batch
from core_sim.constants import TIMESTEPS  # Make sure this exists

def parse_args():
    parser = argparse.ArgumentParser(description="Reactor Fuel Optimizer Simulation")
    parser.add_argument(
        "--layout", type=str, default="layouts/test_layout1.json",
        help="Path to layout JSON file (ignored in batch mode)"
    )
    parser.add_argument(
        "--output", type=str, default="output/single_run_log.json",
        help="Path to output log file (ignored in batch mode)"
    )
    parser.add_argument(
        "--timesteps", type=int, default=TIMESTEPS,
        help="Number of simulation timesteps"
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="Run batch evaluation mode (processes all layouts in layouts/batch/)"
    )
    parser.add_argument(
        "--batch-dir", type=str, default="layout_utils/layouts/batch",
        help="Directory containing layout JSONs for batch mode"
    )
    parser.add_argument(
        "--batch-output", type=str, default="output/batch",
        help="Output directory for batch results"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    config = {
        "some_parameter": 1.0,  # You can expand this config as needed
    }

    if args.batch:
        print("🚀 Running in batch mode...")
        evaluate_layouts_in_batch(args.batch_dir, args.batch_output, config)

    else:
        print(f"🚀 Running single simulation for layout: {args.layout}")
        layout = load_layout(args.layout)
        grid = CoreGrid(width=layout["width"], height=layout["height"])
        grid.initialize_from_layout(layout)

        sim = Simulator(
            grid=grid,
            max_timesteps=args.timesteps,
            output_path=args.output,
            config=config
        )
        sim.run()

        # Load final meta snapshot from saved log
        with open(args.output, "r") as f:
            data = json.load(f)

        if "meta" not in data or not isinstance(data["meta"], list) or not data["meta"]:
            print("⚠️  Warning: No valid 'meta' list found in the output log.")
        else:
            final_meta = data["meta"][-1]
            penalties = final_meta.get("penalties", {})

            print(f"\n✅ Simulation complete.")
            print(f"📈 Final fitness:        {final_meta.get('fitness', 'N/A'):.4f}")
            print(f"⚡ Total energy output:  {final_meta.get('total_energy', 'N/A'):.4f}")
            print(f"⚠️  Total penalty:        {penalties.get('total', 'N/A'):.4e}")
            print(f"🔥 Hotspot penalty:      {penalties.get('hotspot', 'N/A'):.4f}")
            print(f"🌡️  Temp penalty:         {penalties.get('temp', 'N/A'):.4f}")
            print(f"🌀 Symmetry penalty:     {penalties.get('symmetry', 'N/A'):.4f}")
            print(f"⚖️  Penalty weights:      {penalties.get('weights', 'N/A')}")
            print(f"\n📁 Results saved to:     {args.output}")

if __name__ == "__main__":
    main()
