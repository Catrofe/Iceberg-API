from __future__ import annotations

import datetime
import secrets
from typing import Any, List

import bcrypt
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.authorization import encode_token_jwt
from app.database import Employee, ForgotPassword, User
from app.models import (
    ChagedPasswordInput,
    ChagedPasswordOutput,
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
    UserOutput,
    UserRegister,
    UserToken,
)


async def create_user(
    user: UserRegister, session_maker: sessionmaker[AsyncSession]
) -> UserOutput | Error:
    if await verify_email_already_exists(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    try:
        user_add = User(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            phone=user.phone,
            password=await encrypt_password(user.password),
        )
        async with session_maker() as session:
            session.add(user_add)
            await session.commit()

            return UserOutput(id=user_add.id, email=user_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def create_employee(
    user: EmployeeRegister, session_maker: sessionmaker[AsyncSession]
) -> EmployeeOutput | Error:
    if await verify_email_alread_exists_to_employee(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    if user.manager and user.attendant:
        return Error(
            reason="BAD_REQUEST",
            message="USER_MUST_HAVE_ONLY_ONE_ROLE",
            status_code=400,
        )
    elif not user.manager and not user.attendant:
        user.attendant = True

    try:
        employee_add = Employee(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            password=await encrypt_password(user.password),
            manager=user.manager,
            attendant=user.attendant,
        )

        async with session_maker() as session:
            session.add(employee_add)
            await session.commit()

            return EmployeeOutput(id=employee_add.id, email=employee_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def login_user(
    request: LoginUser, session_maker: sessionmaker[AsyncSession]
) -> LoginUserOutput | Error:
    login = request.login
    password = str(request.password)
    password_input = password.encode("utf8")

    async with session_maker() as session:
        user_email = await session.execute(select(User).where(User.email == login))
        user_cpf = await session.execute(select(User).where(User.cpf == login))
        user_phone = await session.execute(select(User).where(User.phone == login))

        print(type(user_phone))

        passwords: List[Any] = [user_email.scalar()]
        passwords.append(user_cpf.scalar())
        passwords.append(user_phone.scalar())

        for iten in passwords:
            try:
                password_db = iten.password
                if isinstance(password_db, str):
                    password_db = password_db.encode("utf-8")
                    if bcrypt.checkpw(password_input, password_db):
                        token = await encode_token_jwt(iten.id, "user")
                        print(token)
                        return LoginUserOutput(
                            login=login, message="LOGIN_SUCCESSFUL", token=token
                        )
            except Exception:
                continue

        return Error(
            reason="BAD_REQUEST", message="INVALID_CREDENTIALS", status_code=400
        )


async def login_employee(
    request: LoginUser, session_maker: sessionmaker[AsyncSession]
) -> LoginEmployeeOutput | Error:

    login = request.login
    password = str(request.password)
    password_input = password.encode("utf8")

    async with session_maker() as session:
        employee_email = await (
            session.execute(select(Employee).where(Employee.email == login))
        )
        employee_cpf = await (
            session.execute(select(Employee).where(Employee.cpf == login))
        )

        passwords: List[Any] = [employee_email.scalar()]
        passwords.append(employee_cpf.scalar())

        for iten in passwords:
            try:
                password_db = iten.password
                if isinstance(password_db, str):
                    password_db = password_db.encode("utf-8")
                    if bcrypt.checkpw(password_input, password_db):
                        token = await encode_token_jwt(iten.id, "employee")
                        return LoginEmployeeOutput(
                            login=login, message="LOGIN_SUCCESSFUL", token=token
                        )
            except Exception as exc:
                print("exc ", exc)
                continue

        return Error(
            reason="BAD_REQUEST", message="INVALID_CREDENTIALS", status_code=400
        )


token_email_test = {}


async def forgot_password_verify(
    request: SearchPasswordInput, session_maker: sessionmaker[AsyncSession]
) -> SearchPasswordOutPut | Error:

    token_email = await create_token_email()
    global token_email_test
    token_email_test = {"token": token_email}

    async with session_maker() as session:
        user_forgot = await (
            session.execute(
                select(User).where(User.email == request.email, User.cpf == request.cpf)
            )
        )

    if user := user_forgot.scalar():
        forgot_add = ForgotPassword(
            token=token_email, user=user.id, requisition_date=datetime.datetime.now()
        )

        async with session_maker() as session:
            session.add(forgot_add)
            await session.commit()

        # Envia e-mail para usuario.

        token_jwt = await encode_token_jwt(user.id, "user")

        return SearchPasswordOutPut(cpf=user.cpf, token=token_jwt)
    else:
        return Error(reason="NOT_FOUND", message="USER_NOT_FOUND", status_code=403)


async def change_password(
    request: ChagedPasswordInput,
    user_request: UserToken,
    session_maker: sessionmaker[AsyncSession],
) -> ChagedPasswordOutput | Error:
    try:
        new_password = request.password
        new_password = await encrypt_password(new_password)

        async with session_maker() as session:
            token_valid = await (
                session.execute(
                    select(ForgotPassword).where(ForgotPassword.token == request.token)
                )
            )

        if token_valid:
            async with session_maker() as session:
                await (
                    session.execute(
                        update(User)
                        .where(User.id == user_request.id)
                        .values(password=new_password)
                    )
                )

                await session.execute(
                    update(ForgotPassword)
                    .where(ForgotPassword.token == request.token)
                    .values(utilized=True)
                )

                await session.commit()

            return ChagedPasswordOutput(
                id=user_request.id, message="SUCCESS_CHANGE_PASSWORD"
            )
        else:
            return Error(
                reason="BAD_REQUEST",
                message="INVALID_TOKEN_TO_CHANGE_PASSWORD",
                status_code=404,
            )

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def edit_account_user(
    request: EditUserInput,
    user_request: UserToken,
    session_maker: sessionmaker[AsyncSession],
) -> EditUserOutput | Error:
    try:
        async with session_maker() as session:
            if request.name:
                await (
                    session.execute(
                        update(User)
                        .where(User.id == user_request.id)
                        .values(name=request.name)
                    )
                )
            if request.email:
                await (
                    session.execute(
                        update(User)
                        .where(User.id == user_request.id)
                        .values(email=request.email)
                    )
                )
            if request.password:
                await (
                    session.execute(
                        update(User)
                        .where(User.id == user_request.id)
                        .values(password=await encrypt_password(request.password))
                    )
                )
            if request.phone:
                await (
                    session.execute(
                        update(User)
                        .where(User.id == user_request.id)
                        .values(phone=request.phone)
                    )
                )

            await session.commit()

        return EditUserOutput(id=user_request.id, message="SUCCESS_UPDATE_ACCOUNT")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def edit_account_employee(
    request: EditUserInput,
    user_request: UserToken,
    session_maker: sessionmaker[AsyncSession],
) -> EditUserOutput | Error:

    try:
        async with session_maker() as session:
            if request.name:
                await (
                    session.execute(
                        update(Employee)
                        .where(Employee.id == user_request.id)
                        .values(name=request.name)
                    )
                )
            if request.email:
                await (
                    session.execute(
                        update(Employee)
                        .where(Employee.id == user_request.id)
                        .values(email=request.email)
                    )
                )
            if request.password:
                await (
                    session.execute(
                        update(Employee)
                        .where(Employee.id == user_request.id)
                        .values(password=await encrypt_password(request.password))
                    )
                )

            await session.commit()

            return EditUserOutput(id=user_request.id, message="SUCCESS_UPDATE_ACCOUNT")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_all_employees(
    session_maker: sessionmaker[AsyncSession],
) -> GetEmployeesOutput | Error:
    async with session_maker() as session:
        employees_select = await session.execute(select(Employee))

    employees = employees_select.scalars()

    try:
        list_employees = []

        for iten in employees:
            data = {}
            if iten.manager:
                data = {"name": iten.name, "occupation": "Manager"}
            elif iten.attendant:
                data = {"name": iten.name, "occupation": "Attendant"}

            list_employees.append(data)

        return GetEmployeesOutput(ListEmployees=list_employees)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_account_logged(
    user: UserToken, session_maker: sessionmaker[AsyncSession]
) -> GetUserLoggedOutput | GetEmployeeLoggedOutput | Error:
    try:
        if user.type == "user":
            async with session_maker() as session:
                account_select = await session.execute(
                    select(User).where(User.id == user.id)
                )
                account = account_select.scalar()

            if account:
                return GetUserLoggedOutput(
                    name=account.name,
                    email=account.email,
                    cpf=account.cpf,
                    phone=str(account.phone),
                )
        elif user.type == "employee":
            async with session_maker() as session:
                account_select = await session.execute(
                    select(Employee).where(Employee.id == user.id)
                )
                account = account_select.scalar()

            if account:
                if account.manager:
                    return GetEmployeeLoggedOutput(
                        name=account.name,
                        email=account.email,
                        cpf=account.cpf,
                        occupation="Manager",
                    )
                else:
                    return GetEmployeeLoggedOutput(
                        name=account.name,
                        email=account.email,
                        cpf=account.cpf,
                        occupation="Attendant",
                    )

        return Error(reason="NOT_FOUND", message="EMPLOYEE_NOT_FOUND", status_code=404)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def change_occupation(
    request: EditOccupationInput,
    user: UserToken,
    session_maker: sessionmaker[AsyncSession],
) -> EditOccupationOutput | Error:
    try:
        if request.manager == request.attendant:
            return Error(
                reason="BAD_REQUEST",
                message="USER_MUST_HAVE_ONLY_ONE_ROLE",
                status_code=400,
            )

        async with session_maker() as session:
            account_select = await session.execute(
                select(Employee).where(Employee.id == user.id, Employee.manager)
            )
            account = account_select.scalar()

        if account:
            async with session_maker() as session:
                if request.manager:
                    await (
                        session.execute(
                            update(Employee)
                            .where(Employee.cpf == request.cpf)
                            .values(manager=True, attendant=False)
                        )
                    )

                    await session.commit()

                    return EditOccupationOutput(
                        cpf=request.cpf,
                        old_occupation="Attendant",
                        new_occupation="Manager",
                    )
                else:
                    await (
                        session.execute(
                            update(Employee)
                            .where(Employee.cpf == request.cpf)
                            .values(manager=False, attendant=True)
                        )
                    )

                    await session.commit()

                    return EditOccupationOutput(
                        cpf=request.cpf,
                        old_occupation="Manager",
                        new_occupation="Attendant",
                    )

        else:
            return Error(
                reason="BAD_REQUEST", message="UNAUTHORIZED_ACCESS", status_code=404
            )

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def create_token_email() -> str:
    return secrets.token_hex(6)


async def verify_email_already_exists(
    email_user: str, session_maker: sessionmaker[AsyncSession]
) -> bool:
    async with session_maker() as session:
        user = await session.execute(select(User).where(User.email == email_user))
        return bool(user.scalar())


async def verify_email_alread_exists_to_employee(
    email_user: str, session_maker: sessionmaker[AsyncSession]
) -> bool:
    async with session_maker() as session:
        employee = await session.execute(
            select(Employee).where(Employee.email == email_user)
        )
        return bool(employee.scalar())


async def encrypt_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf8"), bcrypt.gensalt(8)).decode()


def return_token_tests() -> dict[str, str]:
    return token_email_test
