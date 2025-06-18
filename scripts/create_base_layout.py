# scripts/create_base_layout.py
import json
import random
import os


def create_base_layout_from_existing(input_file, output_file, blank_probability=0.3):
    """
    Tworzy bazowy layout dla GA na podstawie istniejącego layoutu.
    Zamienia część pozycji Fuel na Blank.
    """
    # Wczytaj istniejący layout
    with open(input_file, 'r') as f:
        layout = json.load(f)

    # Statystyki
    fuel_count = 0
    blank_count = 0
    control_count = 0
    moderator_count = 0

    # Modyfikuj grid
    grid = layout['grid']
    for y in range(layout['height']):
        for x in range(layout['width']):
            cell = grid[y][x]
            fa_type = cell.get('fa_type', '')

            if fa_type == 'Fuel':
                # Losowo zamień część paliwa na puste miejsca
                if random.random() < blank_probability:
                    grid[y][x] = {"fa_type": "Blank"}
                    blank_count += 1
                else:
                    fuel_count += 1
            elif fa_type == 'ControlRod':
                control_count += 1
            elif fa_type == 'Moderator':
                moderator_count += 1
            elif fa_type == 'Blank':
                blank_count += 1

    # Zapisz zmodyfikowany layout
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(layout, f, indent=2)

    # Wyświetl statystyki
    total = layout['width'] * layout['height']
    print(f"✅ Utworzono bazowy layout dla GA: {output_file}")
    print(f"\n📊 Statystyki layoutu:")
    print(f"   • Rozmiar: {layout['width']}x{layout['height']} = {total} pozycji")
    print(f"   • Paliwo (Fuel): {fuel_count} ({100 * fuel_count / total:.1f}%)")
    print(f"   • Puste (Blank): {blank_count} ({100 * blank_count / total:.1f}%)")
    print(f"   • Pręty kontrolne: {control_count} ({100 * control_count / total:.1f}%)")
    print(f"   • Moderatory: {moderator_count} ({100 * moderator_count / total:.1f}%)")
    print(f"   • Pozycje do optymalizacji: {fuel_count + blank_count}")


def create_empty_base_layout(width=15, height=15, output_file='layouts/ga_base_layouts/empty_base.json'):
    """
    Tworzy pusty layout z samymi prętami kontrolnymi na brzegach
    i pustymi miejscami w środku.
    """
    layout = {
        "width": width,
        "height": height,
        "grid": []
    }

    for y in range(height):
        row = []
        for x in range(width):
            # Pręty kontrolne na brzegach
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                row.append({"fa_type": "ControlRod"})
            # Moderatory w rogach środkowej części
            elif (x == 2 or x == width - 3) and (y == 2 or y == height - 3):
                row.append({"fa_type": "Moderator"})
            # Reszta to puste miejsca
            else:
                row.append({"fa_type": "Blank"})
        layout["grid"].append(row)

    # Zapisz layout
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(layout, f, indent=2)

    print(f"✅ Utworzono pusty bazowy layout: {output_file}")


if __name__ == "__main__":
    # Ustawienia
    random.seed(42)  # Dla powtarzalności

    # Opcja 1: Stwórz layout na podstawie istniejącego
    if os.path.exists('layouts/test_layout1.json'):
        create_base_layout_from_existing(
            input_file='layouts/test_layout1.json',
            output_file='layouts/ga_base_layouts/base_layout.json',
            blank_probability=0.3  # 30% szans na zamianę Fuel na Blank
        )

    # Opcja 2: Stwórz pusty layout
    create_empty_base_layout()