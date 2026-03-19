import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def get_base_dir():
    return BASE_DIR

def get_models_dir():
    return os.path.join(BASE_DIR, "models")

def get_data_dir():
    return os.path.join(BASE_DIR, "data")
