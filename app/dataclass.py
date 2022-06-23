from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class UserToken:
    id: int
    type: str


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


@dataclass
class SuccessForgotPassword:
    cpf: str
    token: str


@dataclass
class SuccessChangePassword:
    id: int
    message: str


@dataclass
class SuccesEditUser:
    id: int
    message: str


@dataclass
class SuccesGetEmployees:
    data: list[dict[str, str]]


@dataclass
class SuccesGetEmployee:
    name: str
    email: str
    cpf: str
    occupation: str


@dataclass
class SuccesGetUser:
    name: str
    email: str
    cpf: str
    number: str


@dataclass
class SuccessChangeOccupation:
    cpf: str
    old_occupation: str
    new_occupation: str
