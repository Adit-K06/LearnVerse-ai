import os

def ensure_dir(path):
    """Ensures that a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)