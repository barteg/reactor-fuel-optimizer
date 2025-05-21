def penalties(FA_temperatures, FA_lifes, life_threshold=0.95, temperature_threshold=620):
    """
    Kara za przekroczenie temperatury oraz (opcjonalnie) zbyt wysokie zużycie FA.
    """
    penalty = 0
    for temp, life in zip(FA_temperatures, FA_lifes):
        if temp > temperature_threshold:
            penalty += (temp - temperature_threshold)
        if life > life_threshold:
            penalty += (life - life_threshold)
    return penalty
