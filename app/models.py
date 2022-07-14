from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

_email_field = Field(
    min_length=7,
    max_length=255,
    regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
)


class UserToken(BaseModel):
    id: int
    type: str


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


class EmployeeRegister(BaseModel):
    name: str = Field(min_length=3)
    email: str = _email_field
    cpf: str = Field(max_length=11, min_length=11)
    password: str = Field(min_length=8, max_length=255)
    manager: Optional[bool]
    attendant: Optional[bool]


class EmployeeOutput(BaseModel):
    id: Optional[int]
    email: Optional[str]


class LoginUser(BaseModel):
    login: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=5, max_length=255)


class LoginUserOutput(BaseModel):
    login: str
    message: str
    token: str


class LoginEmployeeOutput(BaseModel):
    login: str
    message: str
    token: str


class UpdateEmployeeOutput(BaseModel):
    login: str
    message: str
    token: str


class SearchPasswordInput(BaseModel):
    cpf: str
    email: str


class SearchPasswordOutPut(BaseModel):
    cpf: str
    token: str


class ChagedPasswordInput(BaseModel):
    password: str
    token: str


class ChagedPasswordOutput(BaseModel):
    id: int
    message: str


class EditUserInput(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    password: Optional[str]


class EditUserOutput(BaseModel):
    id: int
    message: str


class GetEmployeesOutput(BaseModel):
    ListEmployees: list[dict[str, str]]


class GetEmployeeLoggedOutput(BaseModel):
    name: str
    email: str
    cpf: str
    occupation: str


class GetUserLoggedOutput(BaseModel):
    name: str
    email: str
    cpf: str
    phone: str


class EditOccupationInput(BaseModel):
    cpf: str
    manager: Optional[bool]
    attendant: Optional[bool]


class EditOccupationOutput(BaseModel):
    cpf: str
    new_occupation: str
    old_occupation: str


class CreateProductInput(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: str
    activate: Optional[bool] = False


class CreateProductOutput(BaseModel):
    id: Optional[int]
    message: str


class UpdateProductInput(BaseModel):
    name: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    price: Optional[str]


class UpdateProductOutput(BaseModel):
    id: Optional[int]
    message: str


class InactivateProductOutput(BaseModel):
    id: Optional[int]
    message: str


class InactivateProductInput(BaseModel):
    id: int
    status: bool


class GetProductIdOutput(BaseModel):
    id: int
    name: str
    description: str
    image_url: str
    price: str
    activated: bool


class GetProductsActivesOutput(BaseModel):
    products: list[dict[str, str]]


class GetAllProductsOutput(BaseModel):
    products: list[dict[str, str]]


class ItemsOrders(BaseModel):
    id: int
    quantity: int


class OrderInput(BaseModel):
    items: list[ItemsOrders]


class OrderOutput(BaseModel):
    id: Optional[int]
    message: str


class GetOrderOutputToUser(BaseModel):
    id: Optional[int]
    status: str
    price: float
    requisition_date: date
    finished: bool
    products: Optional[list[ItemsOrders]]


class GetAllOrdersOutput(BaseModel):
    orders: list[GetOrderOutputToUser]


class InputOrderShop(BaseModel):
    id: int
    accepted: bool
