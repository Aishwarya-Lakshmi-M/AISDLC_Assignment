import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Set
from urllib.parse import quote

import httpx
import pytest


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.environ.get("TODO_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def api_client(api_base_url: str) -> httpx.Client:
    with httpx.Client(base_url=api_base_url, timeout=5.0) as client:
        try:
            response = client.get("/todos")
        except httpx.HTTPError as exc:
            pytest.fail("Todo API is not reachable at {}: {}".format(api_base_url, exc))
        if response.status_code != 200:
            pytest.fail(
                "Todo API readiness check GET /todos returned {}: {}".format(
                    response.status_code, response.text
                )
            )
        yield client


@pytest.fixture
def preexisting_todo_ids(api_client: httpx.Client) -> Set[str]:
    response = api_client.get("/todos")
    assert response.status_code == 200, response.text
    todos = response.json()
    assert isinstance(todos, list), todos
    return {
        todo["id"]
        for todo in todos
        if isinstance(todo, dict) and isinstance(todo.get("id"), str)
    }


@pytest.fixture
def created_todo_ids(api_client: httpx.Client) -> List[str]:
    todo_ids: List[str] = []
    yield todo_ids

    failures = []
    for todo_id in reversed(todo_ids):
        try:
            response = api_client.delete("/todos/{}".format(quote(todo_id, safe="")))
        except httpx.HTTPError as exc:
            failures.append("DELETE {} failed: {}".format(todo_id, exc))
            continue
        if response.status_code not in (204, 404):
            failures.append(
                "DELETE {} returned {}: {}".format(
                    todo_id, response.status_code, response.text
                )
            )

    if failures:
        pytest.fail("Harness cleanup failed:\n{}".format("\n".join(failures)))
    if os.environ.get("TODO_PERSISTENCE_PHASE") == "after_restart":
        state_file = Path(__file__).resolve().parents[1] / ".persistence_state.json"
        if state_file.exists():
            state_file.unlink()


@pytest.fixture
def post_todo(
    api_client: httpx.Client,
    preexisting_todo_ids: Set[str],
    created_todo_ids: List[str],
) -> Callable[[Dict[str, Any]], httpx.Response]:
    def post(payload: Dict[str, Any]) -> httpx.Response:
        response = api_client.post("/todos", json=payload)
        if response.is_success:
            body = response.json()
            todo_id = body.get("id") if isinstance(body, dict) else None
            if (
                isinstance(todo_id, str)
                and todo_id
                and todo_id not in preexisting_todo_ids
                and todo_id not in created_todo_ids
            ):
                created_todo_ids.append(todo_id)
        return response

    return post


@pytest.fixture
def create_todo(
    post_todo: Callable[[Dict[str, Any]], httpx.Response]
) -> Callable[..., Dict[str, Any]]:
    def create(payload: Dict[str, Any]) -> Dict[str, Any]:
        response = post_todo(payload)
        assert response.status_code == 201, response.text
        body = response.json()
        todo_id = body.get("id")
        assert isinstance(todo_id, str), body
        return body

    return create
