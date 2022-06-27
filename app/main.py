from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends, FastAPI, HTTPException

from app.authorization import decode_token_jwt

# build_engine, build_session_maker, setup_db,
from app.database import async_main, setup_db
from app.models import (
    ChagedPasswordInput,
    ChagedPasswordOutput,
    CreateProductInput,
    CreateProductOutput,
    EditOccupationInput,
    EditOccupationOutput,
    EditUserInput,
    EditUserOutput,
    EmployeeOutput,
    EmployeeRegister,
    Error,
    GetEmployeeLoggedOutput,
    GetEmployeesOutput,
    GetUserLoggedOutput,
    LoginEmployeeOutput,
    LoginUser,
    LoginUserOutput,
    SearchPasswordInput,
    SearchPasswordOutPut,
    UpdateProductInput,
    UpdateProductOutput,
    UserOutput,
    UserRegister,
    UserToken,
)
from app.product import product_create, update_product
from app.user import (
    change_occupation,
    change_password,
    create_employee,
    create_user,
    edit_account_employee,
    edit_account_user,
    forgot_password_verify,
    get_all_employees,
    get_employee_logged,
    get_user_logged,
    login_employee,
    login_user,
)
from settings import Config

app = FastAPI()


@dataclass
class ServerContext:
    session_maker: Any


context = ServerContext(session_maker=None)


@app.on_event("startup")
async def startup_event(test: bool = False) -> None:
    if test:
        config = Config(config={"env": "test"})
        session = await setup_db(str(config.config.db_url))
    else:
        config = Config(config={"env": "dev"})
        session = await async_main(str(config.config.db_url))

    global context
    context = ServerContext(session_maker=session)


@app.post("/register/user", status_code=201, response_model=UserOutput)
async def register_user(user: UserRegister) -> UserOutput:
    response = await create_user(user, context.session_maker)

    if isinstance(response, UserOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/register/employee", status_code=201, response_model=EmployeeOutput)
async def register_employee(user: EmployeeRegister) -> EmployeeOutput:
    response = await create_employee(user, context.session_maker)

    if isinstance(response, EmployeeOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/user", status_code=200, response_model=LoginUserOutput)
async def login(request: LoginUser) -> LoginUserOutput:
    response = await login_user(request, context.session_maker)

    if isinstance(response, LoginUserOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/login/employee", status_code=200, response_model=LoginEmployeeOutput)
async def login_backoffice(request: LoginUser) -> LoginEmployeeOutput:
    response = await login_employee(request, context.session_maker)

    if isinstance(response, LoginEmployeeOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/forgot/password", status_code=200, response_model=SearchPasswordOutPut)
async def forgot_password(request: SearchPasswordInput) -> SearchPasswordOutPut:
    response = await forgot_password_verify(request, context.session_maker)

    if isinstance(response, SearchPasswordOutPut):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.patch("/change/password", status_code=200, response_model=ChagedPasswordOutput)
async def change_password_response(
    request: ChagedPasswordInput, user: UserToken = Depends(decode_token_jwt)
) -> ChagedPasswordOutput:
    response = await change_password(request, user, context.session_maker)

    if isinstance(response, ChagedPasswordOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/edit/account", status_code=200, response_model=EditUserOutput)
async def edit_user(
    request: EditUserInput, user: UserToken = Depends(decode_token_jwt)
) -> EditUserOutput:

    if user.type == "user":
        response = await edit_account_user(request, user, context.session_maker)
    else:
        response = await edit_account_employee(request, user, context.session_maker)

    if isinstance(response, EditUserOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/employees", status_code=200, response_model=GetEmployeesOutput)
async def get_employees(
    user: UserToken = Depends(decode_token_jwt),
) -> GetEmployeesOutput:

    if not user.type == "employee":
        raise HTTPException(401, "ACCESS_DENIED")

    response = await get_all_employees(context.session_maker)

    if isinstance(response, GetEmployeesOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/employee/logged", status_code=200, response_model=GetEmployeeLoggedOutput)
async def get_employee(
    user: UserToken = Depends(decode_token_jwt),
) -> GetEmployeeLoggedOutput:
    response = await get_employee_logged(user, context.session_maker)

    if isinstance(response, GetEmployeeLoggedOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/user/logged", status_code=200, response_model=GetUserLoggedOutput)
async def get_user(user: UserToken = Depends(decode_token_jwt)) -> GetUserLoggedOutput:
    response = await get_user_logged(user, context.session_maker)

    if isinstance(response, GetUserLoggedOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/edit/occupation", status_code=200, response_model=EditOccupationOutput)
async def edit_occupation(
    request: EditOccupationInput, user: UserToken = Depends(decode_token_jwt)
) -> EditOccupationOutput:

    response = await change_occupation(request, user, context.session_maker)

    if isinstance(response, EditOccupationOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/create/product", status_code=201, response_model=CreateProductOutput)
async def create_product(
    request: CreateProductInput, user: UserToken = Depends(decode_token_jwt)
) -> CreateProductOutput:

    if user.type == "employee":
        response = await product_create(request, context.session_maker)
    else:
        raise HTTPException(403, "ACCESS_DENIED")

    if isinstance(response, CreateProductOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/update/product/{id}", status_code=200, response_model=UpdateProductOutput)
async def update_product_input(
    id: int, request: UpdateProductInput, user: UserToken = Depends(decode_token_jwt)
) -> UpdateProductOutput:

    if user.type == "employee":
        response = await update_product(request, id, context.session_maker)
    else:
        raise HTTPException(403, "ACCESS_DENIED")

    if isinstance(response, UpdateProductOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)
