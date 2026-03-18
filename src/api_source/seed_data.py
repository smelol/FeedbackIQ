import json
from pathlib import Path

API_SEED_PATH = Path("data/api_reviews_seed.json")


def build_api_reviews_seed():
    if not API_SEED_PATH.exists():
        raise FileNotFoundError(
            f"No existe {API_SEED_PATH}. Ejecuta primero: py .\\seed.py"
        )

    with API_SEED_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)