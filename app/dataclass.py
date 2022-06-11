from dataclasses import dataclass

from dataclasses import dataclass
from typing import Literal

@dataclass
class Error:
    reason: Literal["BAD_REQUEST", "CONFLICT", "UNKNOWN", "NOT_FOUND"]
    message: str
    status_code: int

@dataclass
class SuccessCreateUser:
    id: int
    email: str

@dataclass
class SuccessCreateEmployee:
    id: int
    email: str

@dataclass
class SuccessLoginUser:
    login: str
    message: str

@dataclass
class SuccessLoginEmployee:
    login: str
    message: str