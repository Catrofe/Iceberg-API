from typing import Literal, Optional

from pydantic import BaseModel, Field

_email_field = Field(
    min_length=7,
    max_length=255,
    regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
)


class Error(BaseModel):
    reason: Literal["BAD_REQUEST", "CONFLICT", "UNKNOWN", "NOT_FOUND"]
    message: str
    status_code: int


class UserRegister(BaseModel):
    email: str = _email_field
    name: str = Field(min_length=3)
    cpf: str = Field(max_length=11, min_length=11)
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=255)


class UserOutput(BaseModel):
    id: Optional[int]
    email: Optional[str]
