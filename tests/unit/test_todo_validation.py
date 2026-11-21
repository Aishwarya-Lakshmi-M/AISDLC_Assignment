import uuid


def test_uuid_timestamps_and_validation_limits(client) -> None:
    too_long_title = client.post("/todos", json={"title": "x" * 201})
    too_long_description = client.post("/todos", json={"title": "ok", "description": "d" * 2001})
    assert too_long_title.status_code == 422
    assert too_long_description.status_code == 422

    created = client.post("/todos", json={"title": "x" * 200, "description": "d" * 2000})
    assert created.status_code == 201
    body = created.json()
    uuid.UUID(body["id"])
    assert body["created_at"]
    assert body["updated_at"]
