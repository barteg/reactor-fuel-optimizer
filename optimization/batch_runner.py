# batch_runner.py

import os
import glob
from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator
from layout_utils.load_layout import load_layout
from core_sim.constants import TIMESTEPS

def evaluate_layouts_in_batch(layout_dir, output_dir, config):
    os.makedirs(output_dir, exist_ok=True)
    layout_files = glob.glob(os.path.join(layout_dir, "*.json"))

    results = []

    for layout_path in layout_files:
        layout_name = os.path.basename(layout_path)
        print(f"\n🔄 Evaluating layout: {layout_name}")

        layout = load_layout(layout_path)
        grid = CoreGrid(width=layout["width"], height=layout["height"])
        grid.initialize_from_layout(layout)

        output_path = os.path.join(output_dir, layout_name.replace(".json", "_log.json"))

        sim = Simulator(grid=grid, max_timesteps=TIMESTEPS, output_path=output_path, config=config)
        sim.run()

        final_fitness = sim.meta_history[-1]["fitness"]

        results.append({
            "layout": layout_name,
            "fitness": final_fitness,
            "output_path": output_path
        })

    # Sort by fitness descending
    results.sort(key=lambda x: x["fitness"], reverse=True)

    # Save summary
    summary_path = os.path.join(output_dir, "batch_summary.json")
    with open(summary_path, "w") as f:
        import json
        json.dump(results, f, indent=2)

    print(f"\n✅ Batch evaluation complete. Summary saved to {summary_path}")
    return results
