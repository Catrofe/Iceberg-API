from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.database import build_engine, build_session_maker, setup_db
from app.dataclass import (
    Error,
    SuccessCreateEmployee,
    SuccessCreateUser,
    SuccessLoginEmployee,
    SuccessLoginUser,
)
from app.models import (
    EmployeeOutput,
    EmployeeRegister,
    LoginEmployeeOutput,
    LoginUser,
    LoginUserOutput,
    UserOutput,
    UserRegister,
)
from app.user import create_employee, create_user, login_employee, login_user

app = FastAPI()


@dataclass
class ServerContext:
    engine: Engine
    session_maker: sessionmaker


engine = build_engine("postgresql+psycopg2://root:root@localhost:5432/Iceberg")
context = ServerContext(engine=engine, session_maker=build_session_maker(engine))


@app.on_event("startup")
def startup_event() -> None:
    setup_db(context.engine)


@app.post("/register/user", status_code=201, response_model=UserOutput)
def register_user(user: UserRegister) -> UserOutput:
    response = create_user(user, context.session_maker)

    if isinstance(response, SuccessCreateUser):
        return UserOutput(id=response.id, email=response.email)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/register/employee", status_code=201, response_model=EmployeeOutput)
def register_employee(user: EmployeeRegister) -> EmployeeOutput:
    response = create_employee(user, context.session_maker)

    if isinstance(response, SuccessCreateEmployee):
        return EmployeeOutput(id=response.id, email=response.email)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/user", status_code=200, response_model=LoginUserOutput)
def login(request: LoginUser) -> LoginUserOutput:
    response = login_user(request, context.session_maker)

    if isinstance(response, SuccessLoginUser):
        return LoginUserOutput(login=response.login, message=response.message)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/employee", status_code=200, response_model=LoginEmployeeOutput)
def login_backoffice(request: LoginUser) -> LoginEmployeeOutput:
    response = login_employee(request, context.session_maker)

    if isinstance(response, SuccessLoginEmployee):
        return LoginEmployeeOutput(login=response.login, message=response.message)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)
