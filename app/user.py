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
    EmployeeRegister,
    LoginUser,
    SearchPasswordInput,
    UserRegister,
)


async def create_user(
    user: UserRegister, session_maker: sessionmaker[AsyncSession]
) -> SuccessCreateUser | Error:
    if await verify_email_already_exists(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    try:
        user_add = User(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            number=user.number,
            password=await encrypt_password(user.password),
        )
        async with session_maker() as session:
            session.add(user_add)
            await session.commit()

            return SuccessCreateUser(id=user_add.id, email=user_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def create_employee(
    user: EmployeeRegister, session_maker: sessionmaker[AsyncSession]
) -> SuccessCreateEmployee | Error:
    if await verify_email_alread_exists_to_employee(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    if user.manager == user.attendant:
        return Error(
            reason="BAD_REQUEST",
            message="USER_MUST_HAVE_ONLY_ONE_ROLE",
            status_code=400,
        )

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

            return SuccessCreateEmployee(id=employee_add.id, email=employee_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def login_user(
    request: LoginUser, session_maker: sessionmaker[AsyncSession]
) -> SuccessLoginUser | Error:
    login = request.login
    password = str(request.password)
    password_input = password.encode("utf8")

    async with session_maker() as session:
        user_email = await session.execute(select(User).where(User.email == login))
        user_cpf = await session.execute(select(User).where(User.cpf == login))
        user_number = await session.execute(select(User).where(User.number == login))

        print(type(user_number))

        passwords: List[Any] = []
        passwords.append(user_email.scalar())
        passwords.append(user_cpf.scalar())
        passwords.append(user_number.scalar())

        for iten in passwords:
            try:
                password_db = iten.password
                if isinstance(password_db, str):
                    password_db = password_db.encode("utf-8")
                    if bcrypt.checkpw(password_input, password_db):
                        token = await encode_token_jwt(iten.id, "user")
                        print(token)
                        return SuccessLoginUser(
                            login=login, message="LOGIN_SUCCESSFUL", token=token
                        )
            except Exception:
                continue

        return Error(
            reason="BAD_REQUEST", message="LOGIN_OR_PASSWORD_INCORRECT", status_code=400
        )


async def login_employee(
    request: LoginUser, session_maker: sessionmaker[AsyncSession]
) -> SuccessLoginEmployee | Error:

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

        passwords: List[Any] = []
        passwords.append(employee_email.scalar())
        passwords.append(employee_cpf.scalar())

        for iten in passwords:
            try:
                password_db = iten.password
                if isinstance(password_db, str):
                    password_db = password_db.encode("utf-8")
                    if bcrypt.checkpw(password_input, password_db):
                        token = await encode_token_jwt(iten.id, "employee")
                        return SuccessLoginEmployee(
                            login=login, message="LOGIN_SUCCESSFUL", token=token
                        )
            except Exception as exc:
                print("exc ", exc)
                continue

        return Error(
            reason="BAD_REQUEST", message="LOGIN_OR_PASSWORD_INCORRECT", status_code=400
        )


async def forgot_password_verify(
    request: SearchPasswordInput, session_maker: sessionmaker[AsyncSession]
) -> SuccessForgotPassword | Error:

    token_email = await create_token_email()

    async with session_maker() as session:
        user_forgot = await (
            session.execute(
                select(User).where(User.email == request.email, User.cpf == request.cpf)
            )
        )

    user = user_forgot.scalar()

    if user:
        forgot_add = ForgotPassword(
            token=token_email, user=user.id, requisition_date=datetime.datetime.now()
        )

        async with session_maker() as session:
            session.add(forgot_add)
            await session.commit()

        # Envia e-mail para usuario.

        token_jwt = await encode_token_jwt(user.id, "user")

        return SuccessForgotPassword(cpf=user.cpf, token=token_jwt)
    else:
        return Error(reason="NOT_FOUND", message="USER_NOT_FOUND", status_code=403)


async def change_password(
    request: ChagedPasswordInput,
    user_request: UserToken,
    session_maker: sessionmaker[AsyncSession],
) -> SuccessChangePassword | Error:
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

            return SuccessChangePassword(
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
