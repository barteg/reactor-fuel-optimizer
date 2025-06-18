# scripts/run_best_layout_simulation.py
import json
import sys
import os
from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator


def run_layout_simulation(layout_file, timesteps=1000, output_name=None):
    """Uruchom symulację dla podanego pliku layoutu"""

    # Wczytaj layout
    with open(layout_file, 'r') as f:
        layout = json.load(f)

    print(f"📁 Wczytano layout: {layout_file}")

    # Stwórz siatkę
    grid = CoreGrid(width=layout['width'], height=layout['height'])
    grid.initialize_from_layout(layout)

    # Nazwa pliku wyjściowego
    if output_name is None:
        base_name = os.path.basename(layout_file).replace('.json', '')
        output_name = f"{base_name}_simulation.json"

    output_path = f"output/{output_name}"

    print(f"🔄 Uruchamiam symulację ({timesteps} kroków)...")

    # Stwórz symulator
    simulator = Simulator(
        grid=grid,
        max_timesteps=timesteps,
        output_path=output_path
    )

    # Uruchom symulację
    simulator.run()

    print(f"✅ Symulacja zakończona!")
    print(f"📁 Wyniki zapisane w: {output_path}")
    print(f"\n🎨 Aby zobaczyć wizualizację, uruchom:")
    print(f"   python visualisation/visualize_simulation.py {output_path}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Użycie: python scripts/run_best_layout_simulation.py <plik_layoutu.json> [liczba_kroków]")
        print("\nPrzykład:")
        print(
            "  python scripts/run_best_layout_simulation.py layouts/ga_optimized/run_20240101_120000/best_layout.json")
        print(
            "  python scripts/run_best_layout_simulation.py layouts/ga_optimized/run_20240101_120000/best_layout.json 2000")
        sys.exit(1)

    layout_file = sys.argv[1]
    timesteps = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    if not os.path.exists(layout_file):
        print(f"❌ Błąd: Plik {layout_file} nie istnieje!")
        sys.exit(1)

    run_layout_simulation(layout_file, timesteps)


if __name__ == "__main__":
    main()