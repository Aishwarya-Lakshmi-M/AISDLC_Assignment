from uuid import uuid4

from assertions import assert_error_response


def test_delete_removes_created_todo(create_todo, api_client):
    todo = create_todo({"title": "harness delete"})

    response = api_client.delete("/todos/{}".format(todo["id"]))
    assert response.status_code == 204
    assert response.content == b""

    get_response = api_client.get("/todos/{}".format(todo["id"]))
    assert get_response.status_code == 404
    assert_error_response(get_response)


def test_delete_malformed_id_returns_400(api_client):
    response = api_client.delete("/todos/not-a-uuid")
    assert response.status_code == 400
    assert_error_response(response)


def test_delete_unknown_valid_uuid_returns_404(api_client):
    response = api_client.delete(f"/todos/{uuid4()}")
    assert response.status_code == 404
    assert_error_response(response)
