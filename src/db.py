import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path("data/app.db")


def get_db_path() -> Path:
    env_path = os.getenv("FEEDBACKIQ_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn