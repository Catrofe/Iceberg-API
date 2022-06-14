from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# build_engine, build_session_maker, setup_db,
from app.database import ASYNC_SESSION, ENGINE, async_main
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


context = ServerContext(engine=ENGINE, session_maker=ASYNC_SESSION)


@app.on_event("startup")
async def startup_event() -> None:
    await async_main()


@app.post("/register/user", status_code=201, response_model=UserOutput)
async def register_user(user: UserRegister) -> UserOutput:
    print(context)
    response = await create_user(user, context.session_maker)

    if isinstance(response, SuccessCreateUser):
        return UserOutput(id=response.id, email=response.email)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/register/employee", status_code=201, response_model=EmployeeOutput)
async def register_employee(user: EmployeeRegister) -> EmployeeOutput:
    response = await create_employee(user, context.session_maker)

    if isinstance(response, SuccessCreateEmployee):
        return EmployeeOutput(id=response.id, email=response.email)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/user", status_code=200, response_model=LoginUserOutput)
async def login(request: LoginUser) -> LoginUserOutput:
    response = await login_user(request, context.session_maker)

    if isinstance(response, SuccessLoginUser):
        return LoginUserOutput(login=response.login, message=response.message)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/employee", status_code=200, response_model=LoginEmployeeOutput)
async def login_backoffice(request: LoginUser) -> LoginEmployeeOutput:
    response = await login_employee(request, context.session_maker)

    if isinstance(response, SuccessLoginEmployee):
        return LoginEmployeeOutput(login=response.login, message=response.message)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)
