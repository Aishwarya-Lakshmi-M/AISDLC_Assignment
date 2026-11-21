import pytest

from assertions import assert_error_response, assert_todo_shape, parse_utc_timestamp


def test_patch_applies_partial_changes_and_preserves_creation_timestamp(
    create_todo, api_client
):
    original = create_todo(
        {
            "title": "harness before update",
            "description": "description remains",
            "completed": True,
        }
    )

    response = api_client.patch(
        "/todos/{}".format(original["id"]), json={"title": "harness after update"}
    )
    assert response.status_code == 200, response.text
    updated = assert_todo_shape(response.json())

    assert updated["title"] == "harness after update"
    assert updated["description"] == original["description"]
    assert updated["completed"] is original["completed"]
    assert updated["created_at"] == original["created_at"]
    assert parse_utc_timestamp(updated["updated_at"]) >= parse_utc_timestamp(
        original["updated_at"]
    )


def test_patch_accepts_empty_description_and_false_completion(create_todo, api_client):
    original = create_todo(
        {
            "title": "harness patch falsy values",
            "description": "remove this",
            "completed": True,
        }
    )
    response = api_client.patch(
        "/todos/{}".format(original["id"]),
        json={"description": "", "completed": False},
    )
    assert response.status_code == 200, response.text
    updated = assert_todo_shape(response.json())

    assert updated["description"] == ""
    assert updated["completed"] is False
    assert updated["created_at"] == original["created_at"]
    assert parse_utc_timestamp(updated["updated_at"]) >= parse_utc_timestamp(
        original["updated_at"]
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"unexpected": "field"},
        {"title": ""},
        {"title": "t" * 201},
        {"description": "d" * 2001},
        {"completed": "false"},
    ],
)
def test_patch_rejects_invalid_or_unsupported_fields(
    api_client, create_todo, payload
):
    original = create_todo({"title": "harness rejected update"})

    response = api_client.patch(
        "/todos/{}".format(original["id"]), json=payload
    )
    assert response.status_code == 422
    assert_error_response(response)

    unchanged_response = api_client.get("/todos/{}".format(original["id"]))
    assert unchanged_response.status_code == 200, unchanged_response.text
    unchanged = assert_todo_shape(unchanged_response.json())
    assert unchanged == original


def test_patch_malformed_id_returns_400(api_client):
    response = api_client.patch("/todos/not-a-uuid", json={"title": "updated"})
    assert response.status_code == 400
    assert_error_response(response)


def test_patch_unknown_valid_uuid_returns_404(api_client):
    from uuid import uuid4

    response = api_client.patch(
        "/todos/{}".format(uuid4()), json={"title": "updated"}
    )
    assert response.status_code == 404
    assert_error_response(response)
