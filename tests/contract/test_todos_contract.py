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


def test_contract_invalid_and_unknown_ids(client) -> None:
    assert client.get("/todos/not-a-uuid").status_code == 400
    assert client.get("/todos/550e8400-e29b-41d4-a716-446655440000").status_code == 404
