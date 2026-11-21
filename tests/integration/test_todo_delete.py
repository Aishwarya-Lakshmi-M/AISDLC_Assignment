def test_delete_then_retrieve_and_repeated_delete(client) -> None:
    created = client.post("/todos", json={"title": "Delete me"})
    todo_id = created.json()["id"]

    deleted = client.delete(f"/todos/{todo_id}")
    assert deleted.status_code == 204
    assert client.get(f"/todos/{todo_id}").status_code == 404
    assert client.delete(f"/todos/{todo_id}").status_code == 404


def test_delete_malformed_and_unknown_id(client) -> None:
    assert client.delete("/todos/bad-id").status_code == 400

    unknown = "550e8400-e29b-41d4-a716-446655440000"
    assert client.delete(f"/todos/{unknown}").status_code == 404
