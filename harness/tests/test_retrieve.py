from uuid import uuid4

from assertions import assert_error_response, assert_todo_shape


def test_get_returns_created_todo(create_todo, api_client):
    created = create_todo({"title": "harness retrieve"})

    response = api_client.get("/todos/{}".format(created["id"]))
    assert response.status_code == 200, response.text
    retrieved = assert_todo_shape(response.json())
    assert retrieved == created


def test_get_malformed_id_returns_400(api_client):
    response = api_client.get("/todos/not-a-uuid")
    assert response.status_code == 400
    assert_error_response(response)


def test_get_unknown_valid_uuid_returns_404(api_client):
    response = api_client.get("/todos/{}".format(uuid4()))
    assert response.status_code == 404
    assert_error_response(response)
