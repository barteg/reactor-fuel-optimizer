import json
import gzip

class Recorder:
    def __init__(self):
        self.records = []

    def record(self, grid, meta=None):
        """
        Serializes the current grid (2D list of FA objects) to a serializable list of dicts.
        Appends a snapshot to self.records.
        Optionally attaches meta info (step, fitness, energy, etc.).
        """
        serialized_grid = []
        for row in grid:
            serialized_row = []
            for fa in row:
                cell = {
                    "type": getattr(fa, 'type', None),
                    "life": getattr(fa, 'life', None),
                    "temperature": getattr(fa, 'temperature', None),
                    "enrichment": getattr(fa, 'enrichment', None),
                    "energy_output": getattr(fa, 'energy_output', None),
                    "total_energy": getattr(fa, 'total_energy', None)
                }
                serialized_row.append(cell)
            serialized_grid.append(serialized_row)
        record = {"grid": serialized_grid}
        if meta:
            record["meta"] = meta
        self.records.append(record)

    def save(self, path, compress=False):
        """
        Saves recorded states to JSON or GZipped JSON.
        """
        if compress or path.endswith(".gz"):
            with gzip.open(path, 'wt', encoding='utf-8') as f:
                json.dump(self.records, f)
        else:
            with open(path, 'w') as f:
                json.dump(self.records, f)

    def load(self, path):
        """
        Loads records from JSON or compressed JSON file.
        """
        if path.endswith(".gz"):
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            with open(path, 'r') as f:
                self.records = json.load(f)

    def get_snapshot(self, idx=-1):
        """
        Returns the grid from the given step (by default the last one).
        """
        if not self.records:
            return None
        return self.records[idx]["grid"]

    def clear(self):
        self.records = []
