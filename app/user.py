from collections import deque
from typing import Deque

import bcrypt
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.database import Employee, User
from app.dataclass import (
    Error,
    SuccessCreateEmployee,
    SuccessCreateUser,
    SuccessLoginEmployee,
    SuccessLoginUser,
)
from app.models import EmployeeRegister, LoginUser, UserRegister


async def create_user(
    user: UserRegister, session_maker: sessionmaker
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
    user: EmployeeRegister, session_maker: sessionmaker
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
    request: LoginUser, session_maker: sessionmaker
) -> SuccessLoginUser | Error:
    login = request.login
    password = str(request.password)
    password_input = password.encode("utf8")

    async with session_maker() as session:
        user_email = await session.execute(
            select(User.password).where(User.email == login)
        )
        user_cpf = await session.execute(select(User.password).where(User.cpf == login))
        user_number = await session.execute(
            select(User.password).where(User.number == login)
        )

        print(type(user_number))

        passwords: Deque = deque()
        passwords.append(user_email.scalar())
        passwords.append(user_cpf.scalar())
        passwords.append(user_number.scalar())

        for iten in passwords:
            try:
                password_db = iten
                password_db = password_db.encode("utf-8")
                if bcrypt.checkpw(password_input, password_db):
                    return SuccessLoginUser(login=login, message="LOGIN_SUCCESSFUL")
            except Exception as exc:
                print(exc)
                continue

        return Error(
            reason="BAD_REQUEST", message="LOGIN_OR_PASSWORD_INCORRECT", status_code=400
        )


async def login_employee(
    request: LoginUser, session_maker: sessionmaker
) -> SuccessLoginEmployee | Error:

    login = request.login
    password = str(request.password)
    password_input = password.encode("utf8")

    async with session_maker() as session:
        employee_email = await (
            session.execute(select(Employee.password).where(Employee.email == login))
        )
        employee_cpf = await (
            session.execute(select(Employee.password).where(Employee.cpf == login))
        )

        passwords: list[str] = []
        passwords.append(employee_email.scalar())
        passwords.append(employee_cpf.scalar())

        for iten in passwords:
            try:
                password_db = iten
                password_db = password_db.encode("utf-8")
                if bcrypt.checkpw(password_input, password_db):
                    return SuccessLoginEmployee(login=login, message="LOGIN_SUCCESSFUL")
            except Exception:
                continue

        return Error(
            reason="BAD_REQUEST", message="LOGIN_OR_PASSWORD_INCORRECT", status_code=400
        )


async def verify_email_already_exists(
    email_user: str, session_maker: sessionmaker
) -> bool:
    async with session_maker() as session:
        user = await session.execute(select(User).where(User.email == email_user))
        return bool(user.scalar())


async def verify_email_alread_exists_to_employee(
    email_user: str, session_maker: sessionmaker
) -> bool:
    async with session_maker() as session:
        employee = await session.execute(
            select(Employee).where(Employee.email == email_user)
        )
        return bool(employee.scalar())


async def encrypt_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf8"), bcrypt.gensalt(8)).decode()
