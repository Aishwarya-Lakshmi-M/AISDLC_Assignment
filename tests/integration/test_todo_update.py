def test_partial_update_preserves_created_at(client) -> None:
    created = client.post("/todos", json={"title": "Original", "description": "Old"})
    todo = created.json()

    updated = client.patch(
        f"/todos/{todo['id']}",
        json={"title": "Changed", "completed": True},
    )

    assert updated.status_code == 200
    body = updated.json()
    assert body["title"] == "Changed"
    assert body["completed"] is True
    assert body["created_at"] == todo["created_at"]
    assert body["updated_at"] >= todo["updated_at"]


def test_empty_patch_malformed_and_unknown_id(client) -> None:
    created = client.post("/todos", json={"title": "Task"})
    todo_id = created.json()["id"]

    assert client.patch(f"/todos/{todo_id}", json={}).status_code == 422
    assert client.patch("/todos/bad-id", json={"completed": True}).status_code == 400

    unknown = "550e8400-e29b-41d4-a716-446655440000"
    assert client.patch(f"/todos/{unknown}", json={"completed": True}).status_code == 404
