
TYPE_WEIGHTS = {
    "Fuel": {"Fuel": 0.0, "Moderator": 0.5, "ControlRod": 1.0, "Blank": 0.7},
    "Moderator": {"Fuel": 0.5, "Moderator": 0.0, "ControlRod": 0.8, "Blank": 0.2},
    "ControlRod": {"Fuel": 1.0, "Moderator": 0.8, "ControlRod": 0.0, "Blank": 0.6},
    "Blank": {"Fuel": 0.7, "Moderator": 0.2, "ControlRod": 0.6, "Blank": 0.0}
}


def symmetry_score(grid):
    """
    Computes vertical + horizontal symmetry score considering type mismatches.
    Returns score ∈ [0, 1] where 1 = perfect symmetry.
    """
    width, height = grid.width, grid.height
    total_weighted_diff = 0.0
    max_possible_diff = 0.0

    def get_type(fa):
        if fa is None:
            return "Blank"
        return type(fa).__name__

    for y in range(height):
        for x in range(width):
            fa = grid.get_fa(x, y)

            # Horizontal mirror
            mirror_y = height - 1 - y
            if mirror_y != y:
                fa_h = grid.get_fa(x, mirror_y)
                t1, t2 = get_type(fa), get_type(fa_h)
                total_weighted_diff += TYPE_WEIGHTS[t1][t2]
                max_possible_diff += max(TYPE_WEIGHTS[t1].values())

            # Vertical mirror
            mirror_x = width - 1 - x
            if mirror_x != x:
                fa_v = grid.get_fa(mirror_x, y)
                t1, t2 = get_type(fa), get_type(fa_v)
                total_weighted_diff += TYPE_WEIGHTS[t1][t2]
                max_possible_diff += max(TYPE_WEIGHTS[t1].values())

    score = 1.0 - (total_weighted_diff / max_possible_diff) if max_possible_diff > 0 else 1.0
    return max(0.0, score)
