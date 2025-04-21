import numpy as np

def run_genetic_algorithm(fitness_function, pop_size=20, generations=50):
    population = [np.random.randint(0, 3, (10, 10)) for _ in range(pop_size)]
    for gen in range(generations):
        fitnesses = [fitness_function(ind)[0] for ind in population]
        best = population[np.argmax(fitnesses)]
        # TODO: Crossover + mutation
    return best
