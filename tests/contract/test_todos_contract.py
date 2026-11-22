import uuid


def test_contract_create_and_get(client) -> None:
    created = client.post("/todos", json={"title": "Contract task", "description": "Details"})
    assert created.status_code == 201
    body = created.json()
    assert set(body) == {"id", "title", "description", "completed", "created_at", "updated_at"}
    uuid.UUID(body["id"])

    listed = client.get("/todos")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["id"]

    retrieved = client.get(f"/todos/{body['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == body


def test_contract_validation_and_empty_patch(client) -> None:
    invalid = client.post("/todos", json={"title": "x" * 201})
    assert invalid.status_code == 422

    created = client.post("/todos", json={"title": "Patch me"})
    todo_id = created.json()["id"]
    empty = client.patch(f"/todos/{todo_id}", json={})
    assert empty.status_code == 422


def test_contract_trims_title_and_rejects_whitespace_only_title(client) -> None:
    created = client.post("/todos", json={"title": "  Trim this title  "})
    assert created.status_code == 201
    assert created.json()["title"] == "Trim this title"

    invalid = client.post("/todos", json={"title": "   "})
    assert invalid.status_code == 422
    assert invalid.json()["code"] == "validation_error"


def test_contract_completed_requires_json_boolean(client) -> None:
    invalid_create = client.post(
        "/todos", json={"title": "Invalid completion", "completed": "false"}
    )
    assert invalid_create.status_code == 422
    assert invalid_create.json()["code"] == "validation_error"

    created = client.post("/todos", json={"title": "Strict completion"})
    assert created.status_code == 201
    todo_id = created.json()["id"]
    assert created.json()["completed"] is False

    invalid_update = client.patch(f"/todos/{todo_id}", json={"completed": "false"})
    assert invalid_update.status_code == 422
    assert invalid_update.json()["code"] == "validation_error"
    assert client.get(f"/todos/{todo_id}").json()["completed"] is False


def test_contract_invalid_and_unknown_ids(client) -> None:
    assert client.get("/todos/not-a-uuid").status_code == 400
    assert client.get("/todos/550e8400-e29b-41d4-a716-446655440000").status_code == 404
