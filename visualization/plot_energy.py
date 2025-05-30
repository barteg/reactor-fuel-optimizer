import json
import matplotlib.pyplot as plt

def load_simulation_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def extract_plot_data(records):
    steps = []
    temperatures = []
    energies = []

    for record in records:
        meta = record.get("meta", {})
        step = meta.get("step", len(steps))
        steps.append(step)

        # Average fuel temperature
        fuel_temps = [
            fa["temperature"]
            for row in record["grid"]
            for fa in row
            if fa["type"] == "fuel"
        ]
        avg_temp = sum(fuel_temps) / len(fuel_temps) if fuel_temps else 0
        temperatures.append(avg_temp)

        # Total energy from meta
        energies.append(meta.get("total_energy", 0))

    return steps, temperatures, energies

def plot_energy_vs_time(steps, energies):
    plt.figure(figsize=(8, 4))
    plt.plot(steps, energies, color='blue', label="Total Energy Output")
    plt.xlabel("Timestep")
    plt.ylabel("Energy Output")
    plt.title("Total Energy Output vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

def plot_temperature_vs_time(steps, temperatures):
    plt.figure(figsize=(8, 4))
    plt.plot(steps, temperatures, color='red', label="Avg Fuel Temperature [°C]")
    plt.xlabel("Timestep")
    plt.ylabel("Temperature [°C]")
    plt.title("Average Fuel Temperature vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

def main(filename):
    data = load_simulation_data(filename)
    steps, temperatures, energies = extract_plot_data(data)
    plot_energy_vs_time(steps, energies)
    plot_temperature_vs_time(steps, temperatures)

# Example usage
if __name__ == "__main__":
    main("../output/simulation_log.json")
