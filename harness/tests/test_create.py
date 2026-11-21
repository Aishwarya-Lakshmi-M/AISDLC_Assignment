import pytest

from assertions import assert_error_response, assert_todo_shape


def test_create_uses_documented_defaults(create_todo):
    todo = assert_todo_shape(create_todo({"title": "harness default values"}))

    assert todo["title"] == "harness default values"
    assert todo["description"] == ""
    assert todo["completed"] is False


def test_create_accepts_optional_fields_and_boundary_lengths(create_todo):
    title = "t" * 200
    description = "d" * 2000
    todo = assert_todo_shape(
        create_todo(
            {"title": title, "description": description, "completed": True}
        )
    )

    assert todo["title"] == title
    assert todo["description"] == description
    assert todo["completed"] is True


def test_create_trims_title_before_validation_and_storage(create_todo):
    todo = assert_todo_shape(create_todo({"title": "  trimmed title  "}))
    assert todo["title"] == "trimmed title"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "t" * 201},
        {"title": "valid", "description": "d" * 2001},
        {"title": 123},
        {"title": "valid", "completed": "false"},
    ],
)
def test_create_rejects_invalid_values(api_client, payload):
    response = api_client.post("/todos", json=payload)
    assert response.status_code == 422
    assert_error_response(response)


def test_create_rejects_unknown_fields(api_client):
    response = api_client.post(
        "/todos", json={"title": "unknown field", "unexpected": True}
    )
    assert response.status_code == 422
    assert_error_response(response)
