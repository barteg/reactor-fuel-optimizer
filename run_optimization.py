from optimization.genetic import run_genetic_algorithm

from visualization.plot_core import plot_core


def main():
    best_layout = run_genetic_algorithm(
        population_size=10,
        generations=5,
        mutation_rate=0.2,
        crossover_rate=0.7,
        layout_size=(20, 20),
        num_fuel_types=3,
        log_to_file=True
    )
    plot_core(best_layout, title="GA Best Core Layout")


if __name__ == "__main__":
    main()
