# layout_utils/layout_generator.py

import json
import os
import random

DEFAULT_DIMENSIONS = (20, 20)
DEFAULT_ENRICHMENTS = [1.0, 2.0, 3.0]
DEFAULT_TYPES = ["fuel", "control_rod", "moderator", "blank"]

def generate_random_layout(width=20, height=20, enrichment_levels=None, type_probs=None):
    """
    Generates a random layout with optional enrichment and type probabilities.

    Args:
        width (int): Grid width.
        height (int): Grid height.
        enrichment_levels (list): Enrichment levels for fuel.
        type_probs (dict): Optional dict of type:probability.

    Returns:
        layout (dict): Layout dictionary ready to save or simulate.
    """
    enrichment_levels = enrichment_levels or DEFAULT_ENRICHMENTS
    type_probs = type_probs or {
        "fuel": 0.65,
        "control_rod": 0.1,
        "moderator": 0.2,
        "blank": 0.05
    }

    layout = {
        "width": width,
        "height": height,
        "grid": []  # <-- renamed from "assemblies"
    }

    for y in range(height):
        row = []
        for x in range(width):
            assembly_type = random.choices(
                population=list(type_probs.keys()),
                weights=list(type_probs.values()),
                k=1
            )[0]

            fa = {"fa_type": assembly_type}
            if assembly_type == "fuel":
                fa["enrichment"] = random.choice(enrichment_levels)

            row.append(fa)

        layout["grid"].append(row)  # <-- group each row into sublist

    return layout

def generate_initial_population(n, output_dir="layouts/batch/", width=20, height=20):
    """
    Generates N random layouts and saves them to output_dir.

    Args:
        n (int): Number of layouts.
        output_dir (str): Path to output dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    for i in range(n):
        layout = generate_random_layout(width=width, height=height)
        path = os.path.join(output_dir, f"layout_{i:03d}.json")
        with open(path, "w") as f:
            json.dump(layout, f, indent=2)

    print(f"✅ Generated {n} layouts in: {output_dir}")
