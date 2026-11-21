# Independent Todo API harness

This harness validates the Todo API only through HTTP. It does not import the
application, its dependencies, or the existing test suite.

## Setup and run

Use an environment separate from the application's environment if desired:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:TODO_API_BASE_URL = "http://127.0.0.1:8000"
python -m pytest
```

The API must already be running. `TODO_API_BASE_URL` defaults to
`http://127.0.0.1:8000`. The harness checks `GET /todos` before running tests;
it never starts, stops, or restarts the API.

Tests create uniquely named records and delete only IDs returned by their own
successful create requests. The harness never clears the collection. Run it
against an isolated API instance if other clients may concurrently modify
records; list-order validation considers all records returned by that API.

## Optional persistence check

The persistence check is skipped by default. To run it, set
`TODO_PERSISTENCE_PHASE` to `before_restart`, run only that test, manually
restart the API using your normal operational procedure, and then run the test
again with the phase set to `after_restart`:

```powershell
$env:TODO_PERSISTENCE_PHASE = "before_restart"
python -m pytest tests/test_persistence.py

# Restart the API manually; the harness does not manage it.

$env:TODO_PERSISTENCE_PHASE = "after_restart"
python -m pytest tests/test_persistence.py
Remove-Item Env:\TODO_PERSISTENCE_PHASE
```

The first phase creates a record and stores its ID in the ignored
`.persistence_state.json` file so the second phase can verify it. The second
phase deletes that harness-created record through the API and removes the state
file. If the second phase is not run, the record remains in the API; use the ID
in the state file to delete only that record via the API, then remove the state
file.
