from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends, FastAPI, HTTPException

from app.authorization import decode_token_jwt
from app.database import setup_db_main, setup_db_tests
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
    GetAllOrdersOutput,
    GetAllProductsOutput,
    GetEmployeeLoggedOutput,
    GetEmployeesOutput,
    GetOrderOutputToUser,
    GetProductIdOutput,
    GetProductsActivesOutput,
    GetUserLoggedOutput,
    InactivateProductInput,
    InactivateProductOutput,
    InputOrderShop,
    LoginEmployeeOutput,
    LoginUser,
    LoginUserOutput,
    OrderInput,
    OrderOutput,
    SearchPasswordInput,
    SearchPasswordOutPut,
    UpdateProductInput,
    UpdateProductOutput,
    UserOutput,
    UserRegister,
    UserToken,
)
from app.order import (
    cancel_order,
    order_create,
    orders_active,
    return_all_orders,
    return_order_by_id,
)
from app.product import (
    delete_product,
    get_all_products,
    get_product,
    get_products_actives,
    product_create,
    update_product,
    update_product_status,
)
from app.settings import Settings
from app.shop_order import (
    accepted_or_recused_order,
    cancel_order_accepted,
    finish_order_accepted,
    return_open_orders,
)
from app.user import (
    change_occupation,
    change_password,
    create_employee,
    create_user,
    edit_account_employee,
    edit_account_user,
    forgot_password_verify,
    get_account_logged,
    get_all_employees,
    login_employee,
    login_user,
)

app = FastAPI()


@dataclass
class ServerContext:
    session_maker: Any


context = ServerContext(session_maker=None)


@app.on_event("startup")
async def startup_event(test: bool = False, settings: Settings = Settings()) -> None:
    if test:
        session = await setup_db_tests(str(settings.db_test))
    else:
        session = await setup_db_main(str(settings.db_url))

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


@app.post("/forgot/password", status_code=201, response_model=SearchPasswordOutPut)
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


@app.get(
    "/account/logged",
    status_code=200,
)
async def get_user(
    user: UserToken = Depends(decode_token_jwt),
) -> GetUserLoggedOutput | GetEmployeeLoggedOutput | Error:
    response = await get_account_logged(user, context.session_maker)

    if isinstance(response, GetUserLoggedOutput):
        return response

    elif isinstance(response, GetEmployeeLoggedOutput):
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
async def update_product_by_id(
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


@app.delete("/delete/product/{id}", status_code=200, response_model=UpdateProductOutput)
async def delete_product_by_id(
    id: int, user: UserToken = Depends(decode_token_jwt)
) -> UpdateProductOutput:

    if user.type == "employee":
        response = await delete_product(id, context.session_maker)
    else:
        raise HTTPException(403, "ACCESS_DENIED")

    if isinstance(response, UpdateProductOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.patch(
    "/inactivate/product", status_code=200, response_model=InactivateProductOutput
)
async def change_status_product(
    request: InactivateProductInput, user: UserToken = Depends(decode_token_jwt)
) -> InactivateProductOutput:
    print(request)
    if user.type == "employee":
        response = await update_product_status(request, context.session_maker)
    else:
        raise HTTPException(403, "ACCESS_DENIED")

    if isinstance(response, InactivateProductOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/product/{id}", status_code=200, response_model=GetProductIdOutput)
async def get_product_by_id(
    id: int,
    user: UserToken = Depends(decode_token_jwt),
) -> GetProductIdOutput:

    response = await get_product(id, context.session_maker)

    if isinstance(response, GetProductIdOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/products/actives", status_code=200, response_model=GetProductsActivesOutput)
async def get_all_product_actives(
    user: UserToken = Depends(decode_token_jwt),
) -> GetProductsActivesOutput:

    response = await get_products_actives(context.session_maker)

    if isinstance(response, GetProductsActivesOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/products/all", status_code=200, response_model=GetAllProductsOutput)
async def get_all_products_createds(
    user: UserToken = Depends(decode_token_jwt),
) -> GetAllProductsOutput:

    response = await get_all_products(context.session_maker)

    if isinstance(response, GetAllProductsOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.post("/order", status_code=201, response_model=CreateProductOutput)
async def order_by_client(
    request: OrderInput, user: UserToken = Depends(decode_token_jwt)
) -> OrderOutput:
    response = await order_create(request, user, context.session_maker)

    if isinstance(response, OrderOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/order/{id}", status_code=200, response_model=OrderOutput)
async def order_cancel(
    id: int, user: UserToken = Depends(decode_token_jwt)
) -> OrderOutput:
    response = await cancel_order(id, context.session_maker)

    if isinstance(response, OrderOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/order/{id}", status_code=200, response_model=GetOrderOutputToUser)
async def get_order_by_id(
    id: int, user: UserToken = Depends(decode_token_jwt)
) -> GetOrderOutputToUser:
    response = await return_order_by_id(id, context.session_maker)

    if isinstance(response, GetOrderOutputToUser):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/orders", status_code=200, response_model=GetAllOrdersOutput)
async def get_order_by_user(
    user: UserToken = Depends(decode_token_jwt),
) -> GetAllOrdersOutput:
    response = await return_all_orders(user, context.session_maker)

    if isinstance(response, GetAllOrdersOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/orders/active", status_code=200, response_model=GetAllOrdersOutput)
async def get_order_active(
    user: UserToken = Depends(decode_token_jwt),
) -> GetAllOrdersOutput:
    response = await orders_active(user, context.session_maker)

    if isinstance(response, GetAllOrdersOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.get("/shop_orders/open", status_code=200, response_model=GetAllOrdersOutput)
async def shop_orders_opens(
    user: UserToken = Depends(decode_token_jwt),
) -> GetAllOrdersOutput:

    if not user.type == "employee":
        raise HTTPException(403, "ACCESS_DENIED")

    response = await return_open_orders(context.session_maker)

    if isinstance(response, GetAllOrdersOutput):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/shop_orders", status_code=200, response_model=GetOrderOutputToUser)
async def accepted_or_recused_order_shop(
    request: InputOrderShop,
    user: UserToken = Depends(decode_token_jwt),
) -> GetOrderOutputToUser:

    if not user.type == "employee":
        raise HTTPException(403, "ACCESS_DENIED")

    response = await accepted_or_recused_order(request, context.session_maker)

    if isinstance(response, GetOrderOutputToUser):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.put("/shop_orders/{id}", status_code=200, response_model=GetOrderOutputToUser)
async def cancel_order_shop(
    id: int,
    user: UserToken = Depends(decode_token_jwt),
) -> GetOrderOutputToUser:

    if not user.type == "employee":
        raise HTTPException(403, "ACCESS_DENIED")

    response = await cancel_order_accepted(id, context.session_maker)

    if isinstance(response, GetOrderOutputToUser):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)


@app.patch("/shop_orders/{id}", status_code=200, response_model=GetOrderOutputToUser)
async def order_finished(
    id: int,
    user: UserToken = Depends(decode_token_jwt),
) -> GetOrderOutputToUser:

    if not user.type == "employee":
        raise HTTPException(403, "ACCESS_DENIED")

    response = await finish_order_accepted(id, context.session_maker)

    if isinstance(response, GetOrderOutputToUser):
        return response

    if isinstance(response, Error):
        raise HTTPException(response.status_code, response.message)
