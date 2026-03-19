import os
from pathlib import Path

import pytest

from init_db import init_db


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_app.db"
    monkeypatch.setenv("FEEDBACKIQ_DB_PATH", str(db_path))

    init_db()

    return db_path