from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: int
    message: str
    data: Any = None
    errors: list[dict[str, Any]] | None = None
