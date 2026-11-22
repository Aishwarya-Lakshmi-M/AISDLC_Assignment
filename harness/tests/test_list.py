from assertions import assert_todo_shape, parse_utc_timestamp


def test_list_returns_array_and_orders_todos(create_todo, api_client):
    first = create_todo({"title": "harness list first"})
    second = create_todo({"title": "harness list second"})

    response = api_client.get("/todos")
    assert response.status_code == 200, response.text
    todos = response.json()
    assert isinstance(todos, list), todos
    for todo in todos:
        assert_todo_shape(todo)

    ordering_keys = [(parse_utc_timestamp(todo["created_at"]), todo["id"]) for todo in todos]
    assert ordering_keys == sorted(ordering_keys), ordering_keys

    listed_by_id = {todo["id"]: todo for todo in todos}
    assert first["id"] in listed_by_id
    assert second["id"] in listed_by_id
