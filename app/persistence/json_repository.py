import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonTodoRepository:
    def __init__(self, file_path: Path) -> None:
        self.file_path = Path(file_path)

    def load(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []

        try:
            raw = self.file_path.read_text(encoding="utf-8")
            value = json.loads(raw)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Unable to read valid Todo JSON storage") from exc

        if not isinstance(value, list):
            raise ValueError("Todo JSON storage must contain a list")
        return value

    def save(self, todos: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: str | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                json.dump(todos, temporary_file, ensure_ascii=False)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
                temporary_path = temporary_file.name

            os.replace(temporary_path, self.file_path)
        except OSError as exc:
            if temporary_path:
                try:
                    Path(temporary_path).unlink(missing_ok=True)
                except OSError:
                    pass
            raise ValueError("Unable to write Todo JSON storage") from exc
