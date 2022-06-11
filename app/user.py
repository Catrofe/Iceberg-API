from sqlalchemy.orm import sessionmaker
from app.database import User, Employee
from app.dataclass import Error, SuccessCreateUser, SuccessCreateEmployee, SuccessLoginUser, SuccessLoginEmployee
from app.models import UserRegister, EmployeeRegister, LoginUser
import bcrypt
from collections import deque

def create_user(user: UserRegister, session_maker: sessionmaker) -> SuccessCreateUser | Error:
    if verify_email_already_exists(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    try:
        user_add = User(
            name=user.name, email=user.email, cpf=user.cpf, number=user.number, password=encrypt_password(user.password)
        )
        with session_maker() as session:
            session.add(user_add)
            session.commit()

            return SuccessCreateUser(id=user_add.id, email=user_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)

def create_employee(user: EmployeeRegister, session_maker: sessionmaker) -> SuccessCreateEmployee | Error:
    if verify_email_alread_exists_to_employee(user.email, session_maker):
        return Error(reason="CONFLICT", message="EMAIL_ALREADY_EXISTS", status_code=409)

    if user.manager == user.attendant:
        return Error(reason="BAD_REQUEST", message="USER_MUST_HAVE_ONLY_ONE_ROLE", status_code=400)

    try:
        employee_add = Employee(
            name=user.name, email=user.email, cpf=user.cpf, password=encrypt_password(user.password), manager=user.manager, attendant=user.attendant
        )

        with session_maker() as session:
            session.add(employee_add)
            session.commit()

            return SuccessCreateEmployee(id=employee_add.id, email=employee_add.email)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)

def login_user(request: LoginUser, session_maker: sessionmaker) -> SuccessLoginUser | Error:
    login = request.login
    password = str(request.password)
    password_input = password.encode('utf8')

    with session_maker() as session:
            user_email = session.query(User.password).filter_by(email=login).one_or_none()
            user_cpf = session.query(User.password).filter_by(cpf=login).one_or_none()
            user_number = session.query(User.password).filter_by(number=login).one_or_none()

            password_deque = deque()
            password_deque.append(user_email)
            password_deque.append(user_cpf)
            password_deque.append(user_number)

            for iten in password_deque:
                try:
                    password_db = iten[0]
                    password_db = iten.password.encode('utf-8')
                    if bcrypt.checkpw(password_input, password_db):
                        return SuccessLoginUser(login=login, message='LOGIN_SUCCESSFUL')
                except Exception as exc:
                    print(exc)
                    continue
            
            return Error(reason='BAD_REQUEST', message='LOGIN_OR_PASSWORD_INCORRECT', status_code=400)

def login_employee(request: LoginUser, session_maker: sessionmaker) -> SuccessLoginEmployee | Error:
    login = request.login
    password = str(request.password)
    password_input = password.encode('utf8')

    with session_maker() as session:
            employee_email = session.query(Employee.password).filter_by(email=login).one_or_none()
            employee_cpf = session.query(Employee.password).filter_by(cpf=login).one_or_none()

            password_deque = deque()
            password_deque.append(employee_email)
            password_deque.append(employee_cpf)

            for iten in password_deque:
                try:
                    password_db = iten[0]
                    password_db = iten.password.encode('utf-8')
                    if bcrypt.checkpw(password_input, password_db):
                        return SuccessLoginEmployee(login=login, message='LOGIN_SUCCESSFUL')
                except Exception as exc:
                    continue
            
            return Error(reason='BAD_REQUEST', message='LOGIN_OR_PASSWORD_INCORRECT', status_code=400)

def verify_email_already_exists(email_user: str, session_maker: sessionmaker) -> bool:
    with session_maker() as session:
       return bool(session.query(User.email).filter_by(email=email_user).count()) 

def verify_email_alread_exists_to_employee(email_user: str, session_maker: sessionmaker) -> bool:
    with session_maker() as session:
       return bool(session.query(Employee.email).filter_by(email=email_user).count()) 

def encrypt_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf8"), bcrypt.gensalt(8)).decode()