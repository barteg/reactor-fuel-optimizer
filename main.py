from optimization.genetic import run_genetic_algorithm
from core_sim.core_layout import generate_random_layout
from core_sim.diffusion_solver import simulate_core

if __name__ == "__main__":
    layout = generate_random_layout(10, 3)  # 10x10, 3 fuel types
    fitness, flux_map = simulate_core(layout)
    best_layout = run_genetic_algorithm(fitness_function=simulate_core)
    # TODO: Visualize results

