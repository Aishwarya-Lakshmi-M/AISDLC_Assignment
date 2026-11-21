from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from app.persistence.json_repository import JsonTodoRepository


class TodoNotFoundError(Exception):
    pass


class InvalidTodoIdError(Exception):
    pass


class EmptyUpdateError(Exception):
    pass


class TodoStorageError(Exception):
    pass


class TodoService:
    def __init__(self, file_path: Path) -> None:
        self.repository = JsonTodoRepository(file_path)

    def _load(self) -> list[dict[str, Any]]:
        try:
            return self.repository.load()
        except (OSError, ValueError) as exc:
            raise TodoStorageError from exc

    def _save(self, todos: list[dict[str, Any]]) -> None:
        try:
            self.repository.save(todos)
        except (OSError, ValueError) as exc:
            raise TodoStorageError from exc

    @staticmethod
    def _parse_id(todo_id: str) -> UUID:
        try:
            return UUID(todo_id)
        except (ValueError, AttributeError, TypeError) as exc:
            raise InvalidTodoIdError from exc

    def create(self, title: str, description: str, completed: bool) -> dict[str, Any]:
        now = datetime.now(UTC)
        todo = {
            "id": str(uuid4()),
            "title": title,
            "description": description,
            "completed": completed,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        todos = self._load()
        todos.append(todo)
        self._save(todos)
        return todo

    def list(self) -> list[dict[str, Any]]:
        todos = self._load()
        return sorted(todos, key=lambda todo: (todo["created_at"], todo["id"]))

    def get(self, todo_id: str) -> dict[str, Any]:
        parsed_id = str(self._parse_id(todo_id))
        for todo in self._load():
            if todo["id"] == parsed_id:
                return todo
        raise TodoNotFoundError

    def update(self, todo_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        parsed_id = str(self._parse_id(todo_id))
        if not updates:
            raise EmptyUpdateError

        todos = self._load()
        for index, todo in enumerate(todos):
            if todo["id"] == parsed_id:
                todo.update(updates)
                todo["updated_at"] = datetime.now(UTC).isoformat()
                todos[index] = todo
                self._save(todos)
                return todo
        raise TodoNotFoundError

    def delete(self, todo_id: str) -> None:
        parsed_id = str(self._parse_id(todo_id))
        todos = self._load()
        remaining = [todo for todo in todos if todo["id"] != parsed_id]
        if len(remaining) == len(todos):
            raise TodoNotFoundError
        self._save(remaining)
