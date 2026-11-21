import uuid


def test_create_list_retrieve_and_timestamps(client) -> None:
    first = client.post("/todos", json={"title": "First", "description": "One"})
    second = client.post("/todos", json={"title": "Second"})

    assert first.status_code == 201
    assert second.status_code == 201

    first_body = first.json()
    second_body = second.json()
    uuid.UUID(first_body["id"])
    uuid.UUID(second_body["id"])
    assert first_body["completed"] is False
    assert first_body["created_at"]
    assert first_body["updated_at"]

    listing = client.get("/todos")
    assert listing.status_code == 200
    ids = [item["id"] for item in listing.json()]
    assert ids == [first_body["id"], second_body["id"]]

    retrieve = client.get(f"/todos/{first_body['id']}")
    assert retrieve.status_code == 200
    assert retrieve.json() == first_body


def test_empty_collection_and_storage_error(client, todo_file) -> None:
    listing = client.get("/todos")
    assert listing.status_code == 200
    assert listing.json() == []

    todo_file.write_text("{broken", encoding="utf-8")
    storage = client.get("/todos")
    assert storage.status_code == 500
    assert storage.json()["code"] == "storage_error"
