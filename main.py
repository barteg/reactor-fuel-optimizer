from core_sim.core_layout import generate_random_layout
from core_sim.fusion_solver import simulate_core
from optimization.genetic import GAOptimizer

if __name__ == "__main__":
    # Parameters
    population_size = 50
    mutation_rate = 0.1
    crossover_rate = 0.7
    generations = 100

    # Initialize optimizer
    optimizer = GAOptimizer(
        population_size=population_size,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        generations=generations
    )

    # Run genetic algorithm
    best_layout = run_genetic_algorithm()

    # Simulate the best layout to get fitness and flux map
    fitness, flux_map = simulate_core(best_layout)

    # TODO: Visualize results