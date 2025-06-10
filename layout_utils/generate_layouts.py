# scripts/generate_layouts.py

from layout_utils.layout_generator import generate_initial_population
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10, help="Number of layouts to generate")
    parser.add_argument("--width", type=int, default=20)
    parser.add_argument("--height", type=int, default=20)
    parser.add_argument("--out", type=str, default="layouts/batch/")

    args = parser.parse_args()
    generate_initial_population(n=args.n, output_dir=args.out, width=args.width, height=args.height)