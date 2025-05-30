import json


def load_layout(path):
    """
    Load reactor core layout from a JSON file.

    Args:
        path (str): Path to the JSON layout file.

    Returns:
        dict: Parsed JSON data with keys like 'width', 'height', 'grid'.
    """
    with open(path, "r") as f:
        data = json.load(f)
    return data
