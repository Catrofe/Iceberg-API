from pydantic import BaseModel, Field

_email_field = Field(
    min_length=7,
    max_length=255,
    regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
)


class UserRegister(BaseModel):
    email: str = _email_field
    name: str = Field(min_length=3)
    cpf: str = Field(max_length=11, min_length=11)
    number: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=255)


class UserOutput(BaseModel):
    id: int
    email: str


class EmployeeRegister(BaseModel):
    name: str = Field(min_length=3)
    email: str = _email_field
    cpf: str = Field(max_length=11, min_length=11)
    password: str = Field(min_length=8, max_length=255)
    manager: bool
    attendant: bool


class EmployeeOutput(BaseModel):
    id: int
    email: str


class LoginUser(BaseModel):
    login: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=5, max_length=255)


class LoginUserOutput(BaseModel):
    login: str
    message: str


class LoginEmployeeOutput(BaseModel):
    login: str
    message: str
