from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.authorization import decode_token_jwt

# build_engine, build_session_maker, setup_db,
from app.database import ASYNC_SESSION, ENGINE, async_main
from app.dataclass import (
    Error,
    SuccessChangePassword,
    SuccessCreateEmployee,
    SuccessCreateUser,
    SuccessForgotPassword,
    SuccessLoginEmployee,
    SuccessLoginUser,
    UserToken,
)
from app.models import (
    ChagedPasswordInput,
    ChagedPasswordOutput,
    EmployeeOutput,
    EmployeeRegister,
    LoginEmployeeOutput,
    LoginUser,
    LoginUserOutput,
    SearchPasswordInput,
    SearchPasswordOutPut,
    UserOutput,
    UserRegister,
)
from app.user import (
    change_password,
    create_employee,
    create_user,
    forgot_password_verify,
    login_employee,
    login_user,
)

app = FastAPI()


@dataclass
class ServerContext:
    engine: AsyncEngine
    session_maker: sessionmaker[AsyncSession]


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
        return LoginUserOutput(
            login=response.login, message=response.message, token=response.token
        )

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/employee", status_code=200, response_model=LoginEmployeeOutput)
async def login_backoffice(request: LoginUser) -> LoginEmployeeOutput:
    response = await login_employee(request, context.session_maker)

    if isinstance(response, SuccessLoginEmployee):
        return LoginEmployeeOutput(
            login=response.login, message=response.message, token=response.token
        )

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/forgot/password", status_code=200, response_model=SearchPasswordOutPut)
async def forgot_password(request: SearchPasswordInput) -> SearchPasswordOutPut:
    response = await forgot_password_verify(request, context.session_maker)

    if isinstance(response, SuccessForgotPassword):
        return SearchPasswordOutPut(cpf=response.cpf, token=response.token)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.patch("/change/password", status_code=200, response_model=ChagedPasswordOutput)
async def change_password_response(
    request: ChagedPasswordInput, user: UserToken = Depends(decode_token_jwt)
) -> ChagedPasswordOutput:
    response = await change_password(request, user, context.session_maker)

    if isinstance(response, SuccessChangePassword):
        return ChagedPasswordOutput(id=response.id, message=response.message)

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)
