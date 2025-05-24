import json
import os
import matplotlib.pyplot as plt

history_path = "../visualization/data/simulation_history.json"

assert os.path.exists(history_path), f"Nie znaleziono pliku historii: {history_path}"

with open(history_path, "r") as f:
    data = json.load(f)

steps = [rec["meta"]["step"] for rec in data]
penalty = [rec["meta"]["penalty"] for rec in data]
fitness = [rec["meta"]["fitness"] for rec in data]
total_energy = [rec["meta"]["total_energy"] for rec in data]

plt.figure(figsize=(10,6))
plt.plot(steps, penalty, label="Penalty", marker="o")
plt.plot(steps, fitness, label="Fitness", marker="x")
plt.plot(steps, total_energy, label="Total Energy", linestyle="--", marker=".")
plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Penalty, Fitness & Total Energy over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
os.makedirs("visualization/data", exist_ok=True)
plt.savefig("visualization/data/history_plot.png")
plt.show()

print("Wykres zapisano jako visualization/data/history_plot.png")
