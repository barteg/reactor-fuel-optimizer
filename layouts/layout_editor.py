import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

GRID_SIZE = 15
CELL_SIZE = 30
TYPES = ["Fuel", "ControlRod", "Moderator", "Blank"]


class GridEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Reactor Layout Editor")

        self.grid_data = [[{"fa_type": "Blank"} for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_type = tk.StringVar(value="Fuel")

        # Use StringVar for Entry widgets
        self.fuel_enrichment_str = tk.StringVar(value="0.050")
        self.fuel_life_str = tk.StringVar(value="1.000")

        # Actual numeric values, updated upon successful validation
        self.current_enrichment = 0.050
        self.current_life = 1.000

        # For continuous placing
        self.is_dragging = False
        self.last_placed_coords = None  # (x, y) tuple of the last cell filled during a drag

        self.setup_ui()
        self.draw_grid()  # Initial draw

    def setup_ui(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(control_frame, text="Component Type:").pack(anchor=tk.W)
        for t in TYPES:
            ttk.Radiobutton(control_frame, text=t, variable=self.selected_type, value=t).pack(anchor=tk.W)

        # Register validation command for numeric inputs
        # %P is the value of the entry if the edit is allowed
        # %s is the current value of the entry
        # %S is the text string being inserted or deleted, if any
        vcmd_enrichment = (self.root.register(self._validate_enrichment_input), '%P')
        vcmd_life = (self.root.register(self._validate_life_input), '%P')

        # Enrichment input for Fuel type
        ttk.Label(control_frame, text="Enrichment (0.01-0.10):").pack(anchor=tk.W, pady=(10, 0))
        self.enrichment_entry = ttk.Entry(control_frame, textvariable=self.fuel_enrichment_str,
                                          validate="key", validatecommand=vcmd_enrichment)
        self.enrichment_entry.pack(fill=tk.X)

        # Life input for Fuel type
        ttk.Label(control_frame, text="Life (0.1-1.0):").pack(anchor=tk.W, pady=(10, 0))
        self.life_entry = ttk.Entry(control_frame, textvariable=self.fuel_life_str,
                                    validate="key", validatecommand=vcmd_life)
        self.life_entry.pack(fill=tk.X)

        ttk.Button(control_frame, text="Save Layout", command=self.save_layout).pack(fill=tk.X, pady=(10, 5))
        ttk.Button(control_frame, text="Load Layout", command=self.load_layout).pack(fill=tk.X)

        self.canvas = tk.Canvas(self.root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="lightgray")
        self.canvas.pack(side=tk.RIGHT)

        # Bind mouse events for continuous placing
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def _validate_enrichment_input(self, P):
        """Validates input for the enrichment entry."""
        if not P:  # Allow empty string for temporary input clearing
            return True
        try:
            value = float(P)
            if 0.01 <= value <= 0.10:
                self.current_enrichment = round(value, 3)  # Update the actual value
                return True
            else:
                # messagebox.showwarning("Input Error", "Enrichment must be between 0.01 and 0.10")
                return False  # Reject invalid range
        except ValueError:
            # messagebox.showwarning("Input Error", "Enrichment must be a number.")
            return False  # Reject non-numeric input

    def _validate_life_input(self, P):
        """Validates input for the life entry."""
        if not P:  # Allow empty string
            return True
        try:
            value = float(P)
            if 0.1 <= value <= 1.0:
                self.current_life = round(value, 3)  # Update the actual value
                return True
            else:
                return False  # Reject invalid range
        except ValueError:
            return False  # Reject non-numeric input

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                x1, y1 = x * CELL_SIZE, y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color = self.get_color(self.grid_data[y][x]["fa_type"])
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def get_color(self, cell_type):
        return {
            "Fuel": "orange",
            "ControlRod": "gray",
            "Moderator": "blue",
            "Blank": "white",
        }.get(cell_type, "white")

    def place_component(self, x, y):
        """Places the currently selected component at (x, y) if valid."""
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return

        cell_type = self.selected_type.get()
        cell = {"fa_type": cell_type}

        if cell_type == "Fuel":
            # Use the validated numeric values
            cell["enrichment"] = self.current_enrichment
            cell["life"] = self.current_life

            # Additional check to prevent placing Fuel if current values are default/invalid from entry
            if not (0.01 <= cell["enrichment"] <= 0.10 and 0.1 <= cell["life"] <= 1.0):
                messagebox.showwarning("Invalid Fuel Properties",
                                       "Please enter valid Enrichment (0.01-0.10) and Life (0.1-1.0) values for Fuel.")
                return  # Do not place if values are out of range or not yet validated

        self.grid_data[y][x] = cell
        self.draw_grid()

    def on_mouse_down(self, event):
        self.is_dragging = True
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        self.last_placed_coords = (x, y)  # Initialize last placed
        self.place_component(x, y)

    def on_mouse_drag(self, event):
        if self.is_dragging:
            x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
            if (x, y) != self.last_placed_coords:  # Only place if moved to a new cell
                self.place_component(x, y)
                self.last_placed_coords = (x, y)

    def on_mouse_up(self, event):
        self.is_dragging = False
        self.last_placed_coords = None  # Reset state

    def save_layout(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            layout_data = {
                "width": GRID_SIZE,
                "height": GRID_SIZE,
                "grid": self.grid_data
            }
            try:
                with open(file_path, "w") as f:
                    json.dump(layout_data, f, indent=2)
                messagebox.showinfo("Save Successful", f"Layout saved to {file_path}")
            except IOError as e:
                messagebox.showerror("Save Error", f"Could not save file: {e}")

    def load_layout(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    layout_data = json.load(f)
                    # Basic validation of loaded data
                    if "grid" in layout_data and isinstance(layout_data["grid"], list):
                        loaded_grid = layout_data["grid"]
                        # Check if grid dimensions match or handle resizing
                        if len(loaded_grid) == GRID_SIZE and all(len(row) == GRID_SIZE for row in loaded_grid):
                            self.grid_data = loaded_grid
                            self.draw_grid()
                            messagebox.showinfo("Load Successful", f"Layout loaded from {file_path}")
                        else:
                            messagebox.showwarning("Load Warning",
                                                   "Loaded grid dimensions do not match current editor size (15x15). Displaying partial grid if smaller, or only first 15x15 if larger.")
                            # For simplicity, if dimensions don't match, we'll try to fit the data
                            # A more robust solution would dynamically resize GRID_SIZE or prompt the user.
                            self.grid_data = [[{"fa_type": "Blank"} for _ in range(GRID_SIZE)] for _ in
                                              range(GRID_SIZE)]
                            for r_idx, row in enumerate(loaded_grid):
                                if r_idx < GRID_SIZE:
                                    for c_idx, cell in enumerate(row):
                                        if c_idx < GRID_SIZE:
                                            self.grid_data[r_idx][c_idx] = cell
                            self.draw_grid()
                    else:
                        messagebox.showerror("Load Error", "Invalid JSON format: 'grid' key missing or malformed.")
            except json.JSONDecodeError as e:
                messagebox.showerror("Load Error", f"Invalid JSON file: {e}")
            except IOError as e:
                messagebox.showerror("Load Error", f"Could not open file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GridEditor(root)
    root.mainloop()