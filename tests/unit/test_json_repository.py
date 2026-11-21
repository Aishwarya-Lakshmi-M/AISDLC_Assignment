import json
from pathlib import Path

import pytest

from app.persistence.json_repository import JsonTodoRepository


def test_missing_file_returns_empty_collection(tmp_path: Path) -> None:
    repository = JsonTodoRepository(tmp_path / "todos.json")
    assert repository.load() == []


def test_atomic_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "todos.json"
    repository = JsonTodoRepository(path)
    todo = {"id": "550e8400-e29b-41d4-a716-446655440000", "title": "Test"}
    repository.save([todo])
    assert json.loads(path.read_text(encoding="utf-8")) == [todo]
    assert repository.load() == [todo]


def test_malformed_json_raises_storage_error(tmp_path: Path) -> None:
    path = tmp_path / "todos.json"
    path.write_text("{broken", encoding="utf-8")
    repository = JsonTodoRepository(path)
    with pytest.raises(ValueError):
        repository.load()
