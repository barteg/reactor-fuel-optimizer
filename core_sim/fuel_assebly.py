from typing import Tuple

class FuelAssembly:
    def __init__(self, fa_type: str, enrichment: float, life: float, position: Tuple[int, int]):
        self.fa_type = fa_type          # "movable", "control", "detector", "dummy", "empty"
        self.enrichment = enrichment    # Enrichment fraction (e.g., 0.036 for 3.6%)
        self.life = life                # Remaining lifetime (0.0 to 1.0)
        self.position = position        # (x, y)

    def __repr__(self) -> str:
        return (
            f"FuelAssembly(type={self.fa_type}, "
            f"enrichment={self.enrichment:.3f}, "
            f"life={self.life:.3f}, "
            f"position={self.position})"
        )
