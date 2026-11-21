# Todo REST API

A small FastAPI Todo REST API with JSON file persistence.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run

```powershell
uvicorn app.main:app --reload
```

API documentation is available at `http://127.0.0.1:8000/docs`.

## Validate

```powershell
pytest
ruff check app tests
ruff format --check app tests
bandit -r app
```

The API supports creating, listing, retrieving, updating, and deleting Todo tasks. Persistence uses
`data/todos.json`; test runs use temporary JSON files.
