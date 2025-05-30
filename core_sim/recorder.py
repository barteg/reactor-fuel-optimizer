import json
import gzip


class Recorder:
    def __init__(self, grid_shape, total_steps):
        self.height, self.width = grid_shape
        self.total_steps = total_steps
        self.data = []
        self.records = []

        # Initialize storage for each timestep
        for _ in range(total_steps):
            self.data.append({
                "life": [[0.0] * self.width for _ in range(self.height)],
                "temperature": [[0.0] * self.width for _ in range(self.height)],
                "energy": [[0.0] * self.width for _ in range(self.height)],
                "total_energy": 0.0,
                "fitness": None,
                "penalties": None
            })

    def record(self, grid, meta=None):
        """
        Serializes the current grid (2D list of FuelAssembly objects) into a list of dictionaries
        and appends a snapshot to self.records. Optionally includes metadata (step, fitness, energy, etc.).
        """
        serialized_grid = []
        for row in grid:
            serialized_row = [fa.as_dict() for fa in row]
            serialized_grid.append(serialized_row)

        record = {"grid": serialized_grid}
        if meta:
            record["meta"] = meta
        self.records.append(record)

    def save(self, path, compress=False):
        """
        Saves recorded states to a JSON or GZipped JSON file.
        """
        if compress or path.endswith(".gz"):
            with gzip.open(path, 'wt', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2)

    def load(self, path):
        """
        Loads records from a JSON or compressed JSON file.
        """
        if path.endswith(".gz"):
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                self.records = json.load(f)

    def get_snapshot(self, idx=-1):
        """
        Returns the serialized grid from a specific recorded step (default: last step).
        """
        if not self.records:
            return None
        return self.records[idx]["grid"]

    def clear(self):
        """
        Clears all recorded data.
        """
        self.records = []
