# optimization_ga/fitness_evaluator.py
import os
from core_sim.core_grid import CoreGrid
from core_sim.simulator import Simulator


class FitnessEvaluator:
    """Ewaluator fitness dla chromosomów reaktora"""

    def __init__(self, timesteps=100, temp_limit=800, critical_temp=1000, optimal_fuel_ratio=0.7):
        self.timesteps = timesteps
        self.temp_limit = temp_limit  # Temperatura optymalna
        self.critical_temp = critical_temp  # Temperatura krytyczna (dyskwalifikacja)
        self.optimal_fuel_ratio = optimal_fuel_ratio
        self.cache = {}
        self.eval_count = 0

    def evaluate(self, chromosome):
        """Oblicz fitness dla danego chromosomu"""
        # Cache dla przyspieszenia
        gene_hash = tuple(chromosome.genes)
        if gene_hash in self.cache:
            return self.cache[gene_hash]

        # Konwertuj chromosom na layout
        layout = chromosome.to_layout()

        # Stwórz siatkę i zainicjalizuj
        grid = CoreGrid(width=layout['width'], height=layout['height'])
        grid.initialize_from_layout(layout)

        # Ścieżka dla tymczasowych wyników
        temp_dir = "output/ga_temp"
        os.makedirs(temp_dir, exist_ok=True)
        output_path = f"{temp_dir}/eval_{self.eval_count}.json"

        # Stwórz symulator
        simulator = Simulator(
            grid=grid,
            max_timesteps=self.timesteps,
            output_path=output_path
        )

        # Uruchom symulację
        total_energy = 0.0
        max_temp = 0.0
        avg_temp = 0.0
        temp_violations = 0
        critical_violation = False

        try:
            for step in range(self.timesteps):
                simulator.step()

                if simulator.meta_history:
                    total_energy += simulator.meta_history[-1]['total_energy']

                    # Sprawdź temperatury w tym kroku
                    step_max_temp = 0.0
                    step_temps = []

                    for y in range(grid.height):
                        for x in range(grid.width):
                            fa = grid.get_fa(x, y)
                            if fa and hasattr(fa, 'temperature'):
                                temp = fa.temperature
                                step_temps.append(temp)
                                step_max_temp = max(step_max_temp, temp)

                                # Sprawdź przekroczenia
                                if temp > self.temp_limit:
                                    temp_violations += 1
                                if temp > self.critical_temp:
                                    critical_violation = True

                    max_temp = max(max_temp, step_max_temp)
                    if step_temps:
                        avg_temp += sum(step_temps) / len(step_temps)

                    # Przerwij jeśli temperatura krytyczna
                    if critical_violation:
                        break

        except Exception as e:
            print(f"Błąd podczas symulacji: {e}")
            total_energy = -1000000  # Duża kara za błędną konfigurację

        # Oblicz średnią temperaturę
        if self.timesteps > 0:
            avg_temp /= min(step + 1, self.timesteps)  # step+1 bo może być przerwane

        # Oblicz fitness
        fitness_value = self._calculate_fitness(
            total_energy=total_energy,
            max_temp=max_temp,
            avg_temp=avg_temp,
            fuel_ratio=chromosome.get_fuel_ratio(),
            temp_violations=temp_violations,
            critical_violation=critical_violation,
            steps_completed=step + 1 if 'step' in locals() else 0
        )

        # Cache wynik
        self.cache[gene_hash] = fitness_value
        self.eval_count += 1

        # Usuń tymczasowe pliki
        self._cleanup_temp_files(output_path)

        return fitness_value

    def _calculate_fitness(self, total_energy, max_temp, avg_temp, fuel_ratio,
                           temp_violations, critical_violation, steps_completed):
        """Oblicz wartość fitness na podstawie parametrów"""

        # Jeśli przekroczono temperaturę krytyczną - dyskwalifikacja
        if critical_violation:
            return -1000000 - max_temp  # Ujemny fitness proporcjonalny do temperatury

        # Jeśli symulacja nie dobiegła końca
        if steps_completed < self.timesteps:
            completion_penalty = (self.timesteps - steps_completed) * 1000
            return -completion_penalty

        # Podstawowy fitness = energia
        fitness = total_energy

        # Kary za temperaturę
        if max_temp > self.temp_limit:
            # Progresywna kara za przekroczenie temperatury
            temp_excess = max_temp - self.temp_limit
            temp_penalty = temp_excess ** 2  # Kwadratowa kara
            fitness -= temp_penalty * 10

        # Kara za średnią temperaturę
        if avg_temp > self.temp_limit * 0.8:  # 80% limitu
            avg_penalty = (avg_temp - self.temp_limit * 0.8) * 100
            fitness -= avg_penalty

        # Kara za liczbę przekroczeń temperatury
        fitness -= temp_violations * 50

        # Bonus za utrzymanie temperatury w bezpiecznym zakresie
        if max_temp < self.temp_limit * 0.9:  # 90% limitu
            safety_bonus = (self.temp_limit * 0.9 - max_temp) * 20
            fitness += safety_bonus

        # Kara za zbyt dużo lub za mało paliwa
        if fuel_ratio > 0.8:  # Więcej niż 80% to za dużo
            fuel_penalty = (fuel_ratio - 0.8) * 10000
            fitness -= fuel_penalty
        elif fuel_ratio < 0.4:  # Mniej niż 40% to za mało
            fuel_penalty = (0.4 - fuel_ratio) * 10000
            fitness -= fuel_penalty

        # Bonus za optymalny stosunek paliwa (60-70%)
        if 0.6 <= fuel_ratio <= 0.7:
            fuel_bonus = 5000
            fitness += fuel_bonus

        return fitness

    def _cleanup_temp_files(self, output_path):
        """Usuń tymczasowe pliki"""
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
            snapshots_path = output_path.replace('.json', '_snapshots.json')
            if os.path.exists(snapshots_path):
                os.remove(snapshots_path)
        except:
            pass