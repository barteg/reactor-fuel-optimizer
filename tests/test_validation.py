import unittest
import os
import json
import math


class TestSimulationHistoryValidation(unittest.TestCase):
    def setUp(self):
        # Ścieżka do pliku historii generowanego przez symulację
        self.path = "visualization/data/test_simulation_history.json"
        # Jeśli testujesz na innym pliku, zmień ścieżkę powyżej

    def test_history_content(self):
        self.assertTrue(os.path.exists(self.path), f"Plik {self.path} nie istnieje.")

        with open(self.path, "r") as f:
            data = json.load(f)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Plik historii jest pusty.")

        for idx, record in enumerate(data):
            # Sprawdź, czy każda ramka ma metadane
            self.assertIn("meta", record, f"Brak 'meta' w rekordzie {idx}")
            meta = record["meta"]

            # Sprawdź obecność kluczowych pól w meta
            for key in ["step", "fitness", "penalty", "total_energy"]:
                self.assertIn(key, meta, f"Brak '{key}' w meta kroku {idx}")

                # Sprawdź, czy to liczba, a nie None/NaN/inf
                value = meta[key]
                self.assertIsInstance(value, (int, float), f"{key} nie jest liczbą w kroku {idx}")
                self.assertFalse(math.isnan(value), f"{key} to NaN w kroku {idx}")
                self.assertFalse(math.isinf(value), f"{key} to inf w kroku {idx}")

            # Opcjonalnie: sprawdź, czy grid ma odpowiedni rozmiar i strukturę
            self.assertIn("grid", record, f"Brak 'grid' w rekordzie {idx}")
            grid = record["grid"]
            self.assertIsInstance(grid, list, f"Grid nie jest listą w kroku {idx}")
            # Zakładamy kwadratowy grid, np. 5x5
            self.assertEqual(len(grid), len(grid[0]), f"Grid nie jest kwadratowy w kroku {idx}")


if __name__ == "__main__":
    unittest.main()
