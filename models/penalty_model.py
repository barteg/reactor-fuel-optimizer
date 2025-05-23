# models/penalty_model.py

class PenaltyModel:
    def __init__(self, overheat_temp=620):
        self.overheat_temp = overheat_temp

    def compute_penalty(self, grid):
        """
        Penalizuje każde FA o temperaturze powyżej zadanego progu.
        Kara rośnie kwadratowo wraz z przekroczeniem progu.
        """
        penalty = 0.0
        for row in grid:
            for fa in row:
                if hasattr(fa, "temperature") and fa.temperature > self.overheat_temp:
                    penalty += (fa.temperature - self.overheat_temp) ** 2
        return penalty
