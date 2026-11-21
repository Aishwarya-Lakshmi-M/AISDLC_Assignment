import json
import os
from pathlib import Path

import pytest

from assertions import assert_todo_shape


STATE_FILE = Path(__file__).resolve().parents[1] / ".persistence_state.json"


def test_todo_survives_manually_managed_api_restart(
    api_client, create_todo, created_todo_ids
):
    phase = os.environ.get("TODO_PERSISTENCE_PHASE")
    if phase not in ("before_restart", "after_restart"):
        pytest.skip(
            "Set TODO_PERSISTENCE_PHASE to before_restart or after_restart "
            "to run the two-phase persistence check."
        )

    if phase == "before_restart":
        if STATE_FILE.exists():
            pytest.fail(
                "Persistence state already exists; complete or clean up the "
                "previous persistence check before starting another."
            )
        todo = create_todo({"title": "harness persistence {}".format(os.urandom(8).hex())})
        STATE_FILE.write_text(
            json.dumps({"id": todo["id"], "title": todo["title"]}),
            encoding="utf-8",
        )
        created_todo_ids.remove(todo["id"])
        return

    if not STATE_FILE.exists():
        pytest.fail(
            "Persistence state is missing; run the before_restart phase first."
        )

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    todo_id = state["id"]
    created_todo_ids.append(todo_id)
    response = api_client.get("/todos/{}".format(todo_id))
    assert response.status_code == 200, response.text
    todo = assert_todo_shape(response.json())
    assert todo["id"] == todo_id
    assert todo["title"] == state["title"]
