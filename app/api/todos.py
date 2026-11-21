from fastapi import APIRouter, Request

from app.models.todo import CreateTodo, UpdateTodo
from app.services.todo_service import (
    EmptyUpdateError,
    TodoService,
)

router = APIRouter(prefix="/todos", tags=["todos"])


def get_service(request: Request) -> TodoService:
    return request.app.state.todo_service


@router.get("")
def list_todos(request: Request):
    return get_service(request).list()


@router.post("", status_code=201)
def create_todo(payload: CreateTodo, request: Request):
    return get_service(request).create(payload.title, payload.description, payload.completed)


@router.get("/{todo_id}")
def get_todo(todo_id: str, request: Request):
    return get_service(request).get(todo_id)


@router.patch("/{todo_id}")
def update_todo(todo_id: str, payload: UpdateTodo, request: Request):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise EmptyUpdateError
    return get_service(request).update(todo_id, updates)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: str, request: Request):
    get_service(request).delete(todo_id)
    return None
