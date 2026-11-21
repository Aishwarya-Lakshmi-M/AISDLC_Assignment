from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def todo_file(tmp_path: Path) -> Path:
    return tmp_path / "todos.json"


@pytest.fixture
def client(todo_file: Path) -> TestClient:
    app = create_app(todo_file)
    with TestClient(app) as test_client:
        yield test_client
