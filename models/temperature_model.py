# models/temperature_model.py

class TemperatureModel:
    def update_temperature(self, grid):
        """
        Przykładowa metoda do globalnej aktualizacji temperatury całej siatki.
        (Najczęściej update jest już w metodzie FA, ale można tu podpiąć bardziej złożone modele.)
        """
        for row in grid:
            for fa in row:
                # Na razie zakładamy, że update() FA robi całą robotę.
                pass  # lub zaimplementuj własną logikę, jeśli potrzeba
