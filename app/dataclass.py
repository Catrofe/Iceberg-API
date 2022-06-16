from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class Error:
    reason: Literal["BAD_REQUEST", "CONFLICT", "UNKNOWN", "NOT_FOUND"]
    message: str
    status_code: int


@dataclass
class SuccessCreateUser:
    id: Optional[int]
    email: Optional[str]


@dataclass
class SuccessCreateEmployee:
    id: Optional[int]
    email: Optional[str]


@dataclass
class SuccessLoginUser:
    login: str
    message: str
    token: str


@dataclass
class SuccessLoginEmployee:
    login: str
    message: str
    token: str
