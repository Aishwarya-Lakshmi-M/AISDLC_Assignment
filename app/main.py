from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.todos import router
from app.services.todo_service import (
    EmptyUpdateError,
    InvalidTodoIdError,
    TodoNotFoundError,
    TodoService,
    TodoStorageError,
)


def error_response(code: str, message: str, status_code: int, details=None):
    body = {"code": code, "message": message}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def create_app(todo_file: Path) -> FastAPI:
    app = FastAPI(title="Todo REST API", version="1.0.0")
    app.state.todo_service = TodoService(todo_file)

    @app.exception_handler(InvalidTodoIdError)
    async def invalid_todo_id_handler(request: Request, exc: InvalidTodoIdError):
        return error_response("invalid_todo_id", "Todo ID must be a valid UUID", 400)

    @app.exception_handler(TodoNotFoundError)
    async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
        return error_response("todo_not_found", "Todo task was not found", 404)

    @app.exception_handler(EmptyUpdateError)
    async def empty_update_handler(request: Request, exc: EmptyUpdateError):
        return error_response(
            "empty_update",
            "PATCH must include at least one supported field",
            422,
        )

    @app.exception_handler(TodoStorageError)
    async def storage_error_handler(request: Request, exc: TodoStorageError):
        return error_response("storage_error", "Unable to access Todo storage", 500)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [
            {
                "field": ".".join(str(part) for part in item["loc"]),
                "message": item["msg"],
            }
            for item in exc.errors()
        ]
        return error_response("validation_error", "Request validation failed", 422, details)

    app.include_router(router)
    return app


app = create_app(Path("data/todos.json"))
