# optimization_ga/ga_optimizer.py
import json
import os
import shutil
import numpy as np
from copy import deepcopy
from datetime import datetime
from .chromosome import ReactorChromosome
from .fitness_evaluator import FitnessEvaluator
from .genetic_operators import GeneticOperators


class ReactorGA:
    """Główna klasa algorytmu genetycznego dla optymalizacji reaktora"""

    def __init__(self, base_layout_file, config=None):
        # Wczytaj bazowy layout
        with open(base_layout_file, 'r') as f:
            self.base_layout = json.load(f)

        # Znajdź pozycje do optymalizacji
        self.movable_positions = self._find_movable_positions()
        print(f"Znaleziono {len(self.movable_positions)} pozycji do optymalizacji")

        # Domyślna konfiguracja
        default_config = {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.02,
            'crossover_rate': 0.8,
            'elitism_count': 5,
            'tournament_size': 3,
            'timesteps': 50,
            'temp_limit': 1000,
            'optimal_fuel_ratio': 0.7
        }

        # Połącz z podaną konfiguracją
        self.config = {**default_config, **(config or {})}

        # Inicjalizuj ewaluator
        self.evaluator = FitnessEvaluator(
            timesteps=self.config['timesteps'],
            temp_limit=self.config['temp_limit'],
            optimal_fuel_ratio=self.config['optimal_fuel_ratio']
        )

        # Operatory genetyczne
        self.operators = GeneticOperators()

    def _find_movable_positions(self):
        """Znajdź pozycje które można optymalizować (Fuel lub Blank)"""
        movable = []
        grid = self.base_layout['grid']

        for y in range(self.base_layout['height']):
            for x in range(self.base_layout['width']):
                cell = grid[y][x]
                fa_type = cell.get('fa_type', '')

                # Tylko Fuel i Blank są zmienne
                if fa_type in ['Fuel', 'Blank']:
                    movable.append((x, y))

        return movable

    def initialize_population(self):
        """Inicjalizacja populacji początkowej"""
        population = []

        for i in range(self.config['population_size']):
            chromosome = ReactorChromosome(self.base_layout, self.movable_positions)

            if i == 0:
                # Zachowaj obecny układ
                chromosome.genes = []
                for x, y in self.movable_positions:
                    current_type = self.base_layout['grid'][y][x]['fa_type']
                    chromosome.genes.append(1 if current_type == 'Fuel' else 0)
            elif i == 1:
                # Wszystko paliwo
                chromosome.genes = [1] * len(self.movable_positions)
            elif i == 2:
                # Połowa paliwa (szachownica)
                chromosome.genes = [1 if j % 2 == 0 else 0
                                    for j in range(len(self.movable_positions))]
            else:
                # Losowa inicjalizacja
                fuel_probability = 0.7
                chromosome.genes = [1 if np.random.random() < fuel_probability else 0
                                    for _ in self.movable_positions]

            population.append(chromosome)

        return population

    def run(self):
        """Główna pętla algorytmu genetycznego"""
        population = self.initialize_population()
        best_fitness_history = []
        avg_fitness_history = []
        best_ever = None
        best_fitness_ever = float('-inf')

        self._print_header()

        for generation in range(self.config['generations']):
            gen_start_time = datetime.now()

            # Ewaluacja populacji
            fitness_scores = []
            print(f"\nGeneracja {generation + 1}/{self.config['generations']}")

            for i, chromosome in enumerate(population):
                print(f"  Ewaluacja osobnika {i + 1}/{len(population)}", end='\r')
                fitness = self.evaluator.evaluate(chromosome)
                fitness_scores.append(fitness)

            # Statystyki i aktualizacja najlepszego
            best_idx = np.argmax(fitness_scores)
            best_fitness = fitness_scores[best_idx]
            best_chromosome = population[best_idx]

            if best_fitness > best_fitness_ever:
                best_fitness_ever = best_fitness
                best_ever = deepcopy(best_chromosome)
                print(f"\n  🎯 NOWY REKORD! Fitness: {best_fitness:.2f}")

            best_fitness_history.append(best_fitness)
            avg_fitness = np.mean(fitness_scores)
            avg_fitness_history.append(avg_fitness)

            # Wyświetl statystyki
            self._print_generation_stats(
                generation + 1, best_fitness, avg_fitness,
                np.min(fitness_scores), best_chromosome,
                (datetime.now() - gen_start_time).total_seconds()
            )

            # Tworzenie nowej populacji
            new_population = self._create_new_population(population, fitness_scores)
            population = new_population

            # Checkpoint co 10 generacji
            if (generation + 1) % 10 == 0:
                self._save_checkpoint(best_ever, generation + 1)

        # Cleanup
        self._cleanup_temp_files()

        return best_ever, best_fitness_ever, best_fitness_history, avg_fitness_history

    def _create_new_population(self, population, fitness_scores):
        """Stwórz nową populację używając operatorów genetycznych"""
        new_population = []

        # Elityzm - zachowaj najlepszych
        sorted_indices = np.argsort(fitness_scores)[::-1]
        for i in range(self.config['elitism_count']):
            new_population.append(deepcopy(population[sorted_indices[i]]))

        # Generuj resztę populacji
        while len(new_population) < self.config['population_size']:
            # Selekcja rodziców
            parent1 = self.operators.tournament_selection(
                population, fitness_scores, self.config['tournament_size']
            )
            parent2 = self.operators.tournament_selection(
                population, fitness_scores, self.config['tournament_size']
            )

            # Krzyżowanie
            child1, child2 = self.operators.crossover(
                parent1, parent2, self.config['crossover_rate']
            )

            # Mutacja
            child1 = self.operators.mutate(child1, self.config['mutation_rate'])
            child2 = self.operators.mutate(child2, self.config['mutation_rate'])

            new_population.extend([child1, child2])

        # Ogranicz do rozmiaru populacji
        return new_population[:self.config['population_size']]

    def _print_header(self):
        """Wyświetl nagłówek z informacjami o optymalizacji"""
        print(f"\n{'=' * 60}")
        print(f"ALGORYTM GENETYCZNY - OPTYMALIZACJA UKŁADU PALIWA W REAKTORZE")
        print(f"{'=' * 60}")
        print(f"Parametry:")
        print(f"  • Pozycje do optymalizacji: {len(self.movable_positions)}")
        print(f"  • Rozmiar populacji: {self.config['population_size']}")
        print(f"  • Liczba generacji: {self.config['generations']}")
        print(f"  • Kroki symulacji: {self.config['timesteps']}")
        print(f"  • Prawdopodobieństwo mutacji: {self.config['mutation_rate']}")
        print(f"  • Prawdopodobieństwo krzyżowania: {self.config['crossover_rate']}")
        print(f"{'=' * 60}")

    def _print_generation_stats(self, gen_num, best_fit, avg_fit, min_fit, best_chrom, gen_time):
        """Wyświetl statystyki generacji"""
        fuel_count = best_chrom.get_fuel_count()
        fuel_ratio = best_chrom.get_fuel_ratio()

        print(f"\n  📊 Statystyki generacji {gen_num}:")
        print(f"     • Najlepszy fitness: {best_fit:.2f}")
        print(f"     • Średni fitness: {avg_fit:.2f}")
        print(f"     • Najgorszy fitness: {min_fit:.2f}")
        print(f"     • Paliwo w najlepszym: {fuel_count}/{len(best_chrom.genes)} ({fuel_ratio * 100:.1f}%)")
        print(f"     • Czas generacji: {gen_time:.1f}s")
        print(f"     • Cache hits: {len(self.evaluator.cache)}")

        # Dodaj ostrzeżenie jeśli za dużo paliwa
        if fuel_ratio > 0.8:
            print(f"     ⚠️  UWAGA: Za dużo paliwa! Może prowadzić do przegrzania!")
        elif fuel_ratio < 0.4:
            print(f"     ⚠️  UWAGA: Za mało paliwa! Niska produkcja energii!")

    def _save_checkpoint(self, chromosome, generation):
        """Zapisz checkpoint"""
        checkpoint_dir = "layouts/ga_optimized/checkpoints"
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_file = f"{checkpoint_dir}/checkpoint_gen{generation}.json"
        self.save_layout(chromosome, checkpoint_file)
        print(f"  💾 Zapisano checkpoint: {checkpoint_file}")

    def _cleanup_temp_files(self):
        """Usuń pliki tymczasowe"""
        temp_dir = "output/ga_temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def save_layout(self, chromosome, filename):
        """Zapisz layout do pliku JSON"""
        layout = chromosome.to_layout()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(layout, f, indent=2)

    def save_best_layout(self, chromosome, filename):
        """Zapisz najlepszy layout z dodatkowymi informacjami"""
        self.save_layout(chromosome, filename)
        print(f"\n✅ Zapisano zoptymalizowany layout do: {filename}")

        # Statystyki
        fuel_count = chromosome.get_fuel_count()
        total_positions = len(chromosome.genes)
        print(f"   Liczba elementów paliwa: {fuel_count}/{total_positions} ({100 * fuel_count / total_positions:.1f}%)")