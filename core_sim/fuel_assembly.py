# core_sim/fuel_assembly.py

class FuelAssembly:
    def __init__(self, fa_id, fa_type, enrichment, life, position):
        self.fa_id = fa_id          # Unikalny ID
        self.fa_type = fa_type      # Typ FA: movable, control, detector, dummy, empty
        self.enrichment = enrichment  # Wzbogacenie (procentowe)
        self.life = life            # Pozostałe życie (0–1)
        self.position = position    # Pozycja (x, y)

    def __repr__(self):
        return f"FA({self.fa_id}, {self.fa_type}, Enr={self.enrichment}, Life={self.life}, Pos={self.position})"
