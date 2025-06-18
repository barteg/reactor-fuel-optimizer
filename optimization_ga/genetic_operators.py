# optimization_ga/genetic_operators.py
import random
from copy import deepcopy


class GeneticOperators:
    """Operatory genetyczne dla algorytmu GA"""

    @staticmethod
    def tournament_selection(population, fitness_scores, tournament_size=3):
        """Selekcja turniejowa"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament = [(population[i], fitness_scores[i]) for i in tournament_indices]
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]

    @staticmethod
    def crossover(parent1, parent2, crossover_rate=0.8):
        """Krzyżowanie dwupunktowe"""
        if random.random() > crossover_rate:
            return deepcopy(parent1), deepcopy(parent2)

        # Stwórz dzieci z tymi samymi parametrami co rodzice
        child1 = type(parent1)(parent1.base_layout, parent1.movable_positions)
        child2 = type(parent2)(parent2.base_layout, parent2.movable_positions)

        # Dwa punkty krzyżowania
        if len(parent1.genes) > 2:
            points = sorted(random.sample(range(1, len(parent1.genes)), 2))
        else:
            points = [1, len(parent1.genes) - 1]

        # Krzyżowanie genów
        child1.genes = (parent1.genes[:points[0]] +
                        parent2.genes[points[0]:points[1]] +
                        parent1.genes[points[1]:])
        child2.genes = (parent2.genes[:points[0]] +
                        parent1.genes[points[0]:points[1]] +
                        parent2.genes[points[1]:])

        return child1, child2

    @staticmethod
    def mutate(chromosome, mutation_rate=0.02):
        """Mutacja bitowa z lokalnym przeszukiwaniem"""
        mutated = deepcopy(chromosome)

        # Standardowa mutacja
        for i in range(len(mutated.genes)):
            if random.random() < mutation_rate:
                mutated.genes[i] = 1 - mutated.genes[i]

        # Lokalna optymalizacja (10% szans)
        if random.random() < 0.1:
            idx = random.randint(0, len(mutated.genes) - 1)
            mutated.genes[idx] = 1 - mutated.genes[idx]

        return mutated

    @staticmethod
    def smart_mutation(chromosome, mutation_rate=0.02, temp_aware=True):
        """Inteligentna mutacja - preferuje usuwanie paliwa jeśli za dużo"""
        mutated = deepcopy(chromosome)
        fuel_ratio = mutated.get_fuel_ratio()

        for i in range(len(mutated.genes)):
            if random.random() < mutation_rate:
                if temp_aware and fuel_ratio > 0.75:
                    # Jeśli za dużo paliwa, preferuj usuwanie
                    if mutated.genes[i] == 1 and random.random() < 0.7:
                        mutated.genes[i] = 0
                elif temp_aware and fuel_ratio < 0.5:
                    # Jeśli za mało paliwa, preferuj dodawanie
                    if mutated.genes[i] == 0 and random.random() < 0.7:
                        mutated.genes[i] = 1
                else:
                    # Standardowa mutacja
                    mutated.genes[i] = 1 - mutated.genes[i]

        return mutated