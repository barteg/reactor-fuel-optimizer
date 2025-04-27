from core_sim.core_grid import CoreGrid
from visualization.plot_core import plot_core

def main():
    # Tworzenie rdzenia
    core = CoreGrid(size=20)

    # Wyświetlanie kilku przykładowych FA
    fas = core.get_all_fuel_assemblies()
    sample_fas = [fa for fa in fas if fa.fa_type == "movable"][:5]

    print("Sample Movable Fuel Assemblies:")
    for fa in sample_fas:
        print(fa)

    # Rysowanie siatki
    plot_core(core)

if _name_ == "_main_":
    main()