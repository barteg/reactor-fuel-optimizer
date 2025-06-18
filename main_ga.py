# main_ga.py
from optimization_ga.run_ga import run_optimization
import sys


def main():
    """Główna funkcja do uruchomienia optymalizacji GA"""

    # Sprawdź argumenty linii poleceń
    quick_mode = '--quick' in sys.argv
    no_sim = '--no-sim' in sys.argv
    safe_mode = '--safe' in sys.argv

    # Konfiguracja algorytmu
    if quick_mode:
        print("⚡ Tryb szybki - mniejsza populacja i mniej generacji")
        config = {
            'population_size': 20,
            'generations': 30,
            'mutation_rate': 0.02,
            'crossover_rate': 0.85,
            'elitism_count': 3,
            'tournament_size': 3,
            'timesteps': 50,
            'temp_limit': 800,  # Limit optymalnej temperatury
            'critical_temp': 1000,  # Temperatura krytyczna
            'optimal_fuel_ratio': 0.65
        }
    elif safe_mode:
        print("🛡️ Tryb bezpieczny - niższe limity temperatury")
        config = {
            'population_size': 40,
            'generations': 80,
            'mutation_rate': 0.025,
            'crossover_rate': 0.8,
            'elitism_count': 5,
            'tournament_size': 4,
            'timesteps': 100,
            'temp_limit': 700,  # Niższy limit
            'critical_temp': 900,  # Niższa temperatura krytyczna
            'optimal_fuel_ratio': 0.6
        }
    else:
        print("🚀 Tryb standardowy")
        config = {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.02,
            'crossover_rate': 0.85,
            'elitism_count': 5,
            'tournament_size': 3,
            'timesteps': 100,
            'temp_limit': 800,  # Limit optymalnej temperatury
            'critical_temp': 1000,  # Temperatura krytyczna
            'optimal_fuel_ratio': 0.65
        }

    print(f"\n⚙️  Parametry bezpieczeństwa:")
    print(f"   • Limit temperatury: {config['temp_limit']}°C")
    print(f"   • Temperatura krytyczna: {config['critical_temp']}°C")
    print(f"   • Optymalny stosunek paliwa: {config['optimal_fuel_ratio'] * 100:.0f}%")

    # Ścieżka do bazowego layoutu
    base_layout = 'layouts/ga_base_layouts/base_layout.json'

    # Uruchom optymalizację
    results = run_optimization(
        base_layout,
        config,
        run_final_sim=not no_sim
    )

    print("\n🎉 Gotowe!")
    print(f"📁 Wyniki GA zapisane w: {results['ga_output_dir']}")

    if results['simulation_output']:
        print(f"📁 Symulacja zapisana w: {results['simulation_output']}")
        print(f"\n🎨 Aby zobaczyć wizualizację, uruchom:")
        print(f"   python visualisation/visualize_simulation.py {results['simulation_output']}")


if __name__ == "__main__":
    print("=" * 60)
    print("OPTYMALIZACJA UKŁADU PALIWA W REAKTORZE - ALGORYTM GENETYCZNY")
    print("=" * 60)
    print("\nOpcje:")
    print("  python main_ga.py           - standardowa optymalizacja")
    print("  python main_ga.py --quick   - szybki tryb (mniej generacji)")
    print("  python main_ga.py --safe    - tryb bezpieczny (niższe limity)")
    print("  python main_ga.py --no-sim  - bez końcowej symulacji")
    print("=" * 60)

    main()