# optimization_ga/run_ga.py
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from .ga_optimizer import ReactorGA
from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator


def plot_evolution(best_history, avg_history, output_dir):
    """Stwórz wykres ewolucji algorytmu"""
    plt.figure(figsize=(12, 6))

    generations = range(1, len(best_history) + 1)

    plt.plot(generations, best_history, 'b-', linewidth=2, label='Najlepszy fitness')
    plt.plot(generations, avg_history, 'r--', linewidth=1, label='Średni fitness')

    plt.xlabel('Generacja')
    plt.ylabel('Fitness')
    plt.title('Ewolucja Algorytmu Genetycznego - Optymalizacja Reaktora')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plot_path = os.path.join(output_dir, 'evolution_plot.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    return plot_path


def save_optimization_report(ga, best_chromosome, best_fitness, history, output_dir):
    """Zapisz raport z optymalizacji"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = {
        "timestamp": timestamp,
        "configuration": ga.config,
        "movable_positions": len(ga.movable_positions),
        "best_fitness": best_fitness,
        "fuel_count": best_chromosome.get_fuel_count(),
        "fuel_ratio": best_chromosome.get_fuel_ratio(),
        "generations_run": len(history[0]),
        "final_best_fitness": history[0][-1],
        "final_avg_fitness": history[1][-1],
        "improvement": history[0][-1] - history[0][0]
    }

    report_path = os.path.join(output_dir, 'optimization_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report_path


def run_final_simulation(best_layout, timesteps=1000, output_filename='ga_optimized_simulation.json'):
    """Uruchom pełną symulację dla najlepszego layoutu i zapisz w output/"""
    print(f"\n🔄 Uruchamiam pełną symulację najlepszego layoutu ({timesteps} kroków)...")

    # Stwórz siatkę
    grid = CoreGrid(width=best_layout['width'], height=best_layout['height'])
    grid.initialize_from_layout(best_layout)

    # Ścieżka wyjściowa
    output_path = f"output/{output_filename}"

    # Stwórz symulator
    simulator = Simulator(
        grid=grid,
        max_timesteps=timesteps,
        output_path=output_path
    )

    # Uruchom symulację
    simulator.run()

    print(f"✅ Symulacja zakończona. Wyniki zapisane w: {output_path}")
    print(f"   Możesz teraz uruchomić wizualizację:")
    print(f"   python visualisation/visualize_simulation.py {output_path}")

    return output_path


def run_optimization(base_layout_path=None, config=None, run_final_sim=True):
    """Uruchom optymalizację GA"""

    # Domyślna ścieżka do bazowego layoutu
    if base_layout_path is None:
        base_layout_path = 'layouts/ga_base_layouts/base_layout.json'

    # Domyślna konfiguracja
    default_config = {
        'population_size': 30,
        'generations': 50,
        'mutation_rate': 0.02,
        'crossover_rate': 0.85,
        'elitism_count': 5,
        'tournament_size': 3,
        'timesteps': 50,
        'temp_limit': 1000,
        'optimal_fuel_ratio': 0.7
    }

    # Połącz z podaną konfiguracją
    if config:
        default_config.update(config)

    # Timestamp dla unikalnych nazw
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Katalog wyjściowy dla GA
    ga_output_dir = f"layouts/ga_optimized/run_{timestamp}"
    os.makedirs(ga_output_dir, exist_ok=True)

    print(f"🚀 Uruchamiam algorytm genetyczny...")
    print(f"📁 Bazowy layout: {base_layout_path}")
    print(f"📁 Katalog wyjściowy GA: {ga_output_dir}")

    # Inicjalizuj i uruchom GA
    ga = ReactorGA(base_layout_path, config=default_config)

    # Optymalizacja
    best_chromosome, best_fitness, best_history, avg_history = ga.run()

    # Zapisz najlepszy layout
    best_layout_path = os.path.join(ga_output_dir, 'best_layout.json')
    ga.save_best_layout(best_chromosome, best_layout_path)

    # Stwórz wykres
    plot_path = plot_evolution(best_history, avg_history, ga_output_dir)
    print(f"📊 Zapisano wykres ewolucji: {plot_path}")

    # Zapisz raport
    report_path = save_optimization_report(ga, best_chromosome, best_fitness,
                                           (best_history, avg_history), ga_output_dir)
    print(f"📄 Zapisano raport: {report_path}")

    print(f"\n✨ Optymalizacja GA zakończona!")
    print(f"🏆 Najlepszy fitness: {best_fitness:.2f}")
    print(f"⚡ Liczba elementów paliwa: {best_chromosome.get_fuel_count()}")

    # Uruchom pełną symulację dla najlepszego layoutu
    simulation_output = None
    if run_final_sim:
        best_layout = best_chromosome.to_layout()
        simulation_filename = f"ga_optimized_{timestamp}.json"
        simulation_output = run_final_simulation(
            best_layout,
            timesteps=1000,  # Pełna symulacja
            output_filename=simulation_filename
        )

    return {
        'best_chromosome': best_chromosome,
        'best_fitness': best_fitness,
        'best_history': best_history,
        'avg_history': avg_history,
        'ga_output_dir': ga_output_dir,
        'simulation_output': simulation_output
    }


if __name__ == "__main__":
    # Przykładowe uruchomienie
    results = run_optimization()