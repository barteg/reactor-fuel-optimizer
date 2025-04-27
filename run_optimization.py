from optimization.ga_optimizer import run_genetic_algorithm
from visualization.plot_core import plot_core

def main():
    # Parametry algorytmu — możesz je łatwo dostroić
    best_layout = run_genetic_algorithm(
        population_size=50,      # liczba osobników
        generations=100,         # liczba pokoleń
        mutation_rate=0.1,       # prawdopodobieństwo mutacji
        crossover_rate=0.8,      # prawdopodobieństwo krzyżowania
        layout_size=(20, 20),    # rozmiar rdzenia
        num_fuel_types=3         # liczba różnych wzbogaceń
    )

    # Wyświetlenie najlepszego układu
    plot_core(best_layout, title="Best Core Layout (GA)")

if __name__ == "__main__":
    main()
