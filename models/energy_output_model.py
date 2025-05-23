# models/energy_output_model.py

class EnergyOutputModel:
    def compute_output(self, grid):
        """
        Sumuje aktualną produkcję energii wszystkich FA w siatce.
        """
        return sum(getattr(fa, "energy_output", 0.0) for row in grid for fa in row)
