"""Base models for API responses."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIError(BaseModel):
    """API error response."""

    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    """Wrapper for all API responses."""

    success: bool
    data: T | None = None
    error: APIError | None = None


class PageCursor(BaseModel):
    """Pagination cursor info."""

    model_config = ConfigDict(populate_by_name=True)

    cursor: str
    has_more: bool


class CamelModel(BaseModel):
    """Base model that converts snake_case to camelCase for API."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: "".join(
            word.capitalize() if i else word for i, word in enumerate(s.split("_"))
        ),
    )
