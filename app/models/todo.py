from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StringConstraints

TodoTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class TodoTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = False
    created_at: datetime
    updated_at: datetime


class CreateTodo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TodoTitle
    description: str = Field(default="", max_length=2000)
    completed: StrictBool = False


class UpdateTodo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TodoTitle | None = None
    description: str | None = Field(default=None, max_length=2000)
    completed: StrictBool | None = None


class ErrorDetails(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ErrorDetails] | None = None
