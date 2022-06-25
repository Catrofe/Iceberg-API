import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app, startup_event
from app.user import return_token_tests

client = TestClient(app)


@pytest.fixture
def drop_database():
    asyncio.run(startup_event(True))


def test_create_user_should_success(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "email@email.com"}


def test_create_user__should_conflict(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)
    response = client.post("/register/user", json=body)

    assert response.status_code == 409
    assert response.json() == {"detail": "EMAIL_ALREADY_EXISTS"}


def test_create_employee_should_success(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
        "manager": True,
        "attendant": False,
    }

    response = client.post("/register/employee", json=body)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "email@email.com"}


def test_create_employee__should_conflict(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)
    response = client.post("/register/user", json=body)

    assert response.status_code == 409
    assert response.json() == {"detail": "EMAIL_ALREADY_EXISTS"}


def test_create_employee_occupation_duplicated_true(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
        "manager": True,
        "attendant": True,
    }

    response = client.post("/register/employee", json=body)

    assert response.status_code == 400
    assert response.json() == {"detail": "USER_MUST_HAVE_ONLY_ONE_ROLE"}


def test_create_employee_occupation_duplicated_false(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
    }

    response = client.post("/register/employee", json=body)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "email@email.com"}


def test_login_user_should_success(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}

    response = client.post("/login/user", json=body)

    obj_json = response.json()

    assert response.status_code == 200

    assert response.json() == {
        "login": "email@email.com",
        "message": "LOGIN_SUCCESSFUL",
        "token": obj_json["token"],
    }


def test_login_user_with_number_should_success(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)

    body = {"login": "21999999999", "password": "12345678"}

    response = client.post("/login/user", json=body)

    obj_json = response.json()

    assert response.status_code == 200

    assert response.json() == {
        "login": "21999999999",
        "message": "LOGIN_SUCCESSFUL",
        "token": obj_json["token"],
    }


def test_login_user_with_cpf_should_success(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)

    body = {"login": "17410599090", "password": "12345678"}

    response = client.post("/login/user", json=body)

    obj_json = response.json()

    assert response.status_code == 200

    assert response.json() == {
        "login": "17410599090",
        "message": "LOGIN_SUCCESSFUL",
        "token": obj_json["token"],
    }


def test_login_user_should_bad_request(drop_database):

    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }

    response = client.post("/register/user", json=body)

    body = {"login": "17410599090", "password": "123456789"}

    response = client.post("/login/user", json=body)

    assert response.status_code == 400
    assert response.json() == {"detail": "INVALID_CREDENTIALS"}


def test_login_employee_should_success(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
    }

    response = client.post("/register/employee", json=body)

    body = {"login": "email@email.com", "password": "12345678"}

    response = client.post("/login/employee", json=body)

    obj_json = response.json()

    assert response.status_code == 200

    assert response.json() == {
        "login": "email@email.com",
        "message": "LOGIN_SUCCESSFUL",
        "token": obj_json["token"],
    }


def test_login_employee_with_cpf_should_success(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
    }

    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "12345678"}

    response = client.post("/login/employee", json=body)

    obj_json = response.json()

    assert response.status_code == 200

    assert response.json() == {
        "login": "17410599090",
        "message": "LOGIN_SUCCESSFUL",
        "token": obj_json["token"],
    }


def test_login_employee_should_bad_request(drop_database):

    body = {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "17410599090",
        "password": "12345678",
    }

    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "123456789"}

    response = client.post("/login/employee", json=body)

    assert response.status_code == 400
    assert response.json() == {"detail": "INVALID_CREDENTIALS"}


def test_forgot_password_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"cpf": "17410599090", "email": "email@email.com"}
    response = client.post("/forgot/password", json=body)

    obj_json = response.json()

    assert response.status_code == 200
    assert response.json() == {"cpf": "17410599090", "token": obj_json["token"]}


def test_forgot_password_should_error(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"cpf": "17410599099", "email": "email@email.com"}
    response = client.post("/forgot/password", json=body)

    assert response.status_code == 403
    assert response.json() == {"detail": "USER_NOT_FOUND"}


def test_change_password_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"cpf": "17410599090", "email": "email@email.com"}
    response = client.post("/forgot/password", json=body)

    response = response.json()
    header = {
        "Authorization": response["token"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    token = return_token_tests()
    token = token["token"]

    body = {"password": "123456789", "token": str(token)}
    response = client.patch("/change/password", json=body, headers=header)

    assert response.status_code == 200

    # realiza login com nova senha
    body = {"login": "17410599090", "password": "123456789"}
    response = client.post("/login/user", json=body)

    assert response.status_code == 200
    assert response.json() == {
        "login": "17410599090",
        "message": "LOGIN_SUCCESSFUL",
        "token": response.json()["token"],
    }


def test_edit_user_account_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "17410599090", "password": "12345678"}
    response = client.post("/login/user", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"email": "email2@email.com", "password": "987654321"}
    response = client.put("/edit/account", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "SUCCESS_UPDATE_ACCOUNT"}

    body = {"login": "email2@email.com", "password": "987654321"}
    response = client.post("/login/user", json=body)

    assert response.status_code == 200


def test_edit_employee_account_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    body = {"email": "email2@email.com", "password": "987654321"}
    response = client.put("/edit/account", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "SUCCESS_UPDATE_ACCOUNT"}

    body = {"login": "email2@email.com", "password": "987654321"}
    response = client.post("/login/employee", json=body)

    assert response.status_code == 200


def test_get_all_employees(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "email2@email.com", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = client.get("/employees", headers=header)

    assert response.status_code == 200
    assert response.json() == {
        "ListEmployees": [
            {"name": "Christian Lopes", "occupation": "Attendant"},
            {"name": "Christian Lopes", "occupation": "Manager"},
        ]
    }


def test_get_all_employees_should_error_account_user(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "number": "21999999999",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = client.get("/employees", headers=header)

    assert response.status_code == 401
    assert response.json() == {"detail": "ACCESS_DENIED"}


def test_get_employee_loged_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = client.get("/employee/logged", headers=header)

    assert response.status_code == 200
    assert response.json() == {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "cpf": "12345678901",
        "occupation": "Manager",
    }


def test_get_user_loged_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "number": "21999999999",
        "cpf": "12345678901",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = client.get("/user/logged", headers=header)

    assert response.status_code == 200
    assert response.json() == {
        "name": "Christian Lopes",
        "email": "email@email.com",
        "number": "21999999999",
        "cpf": "12345678901",
    }


def test_change_occupation_employee_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "email2@email.com", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {"cpf": "17410599090", "manager": True}

    response = client.put("/edit/occupation", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {
        "cpf": "17410599090",
        "old_occupation": "Attendant",
        "new_occupation": "Manager",
    }


def test_change_occupation_employee_should_unauthorized(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {"cpf": "12345678901", "manager": True}

    response = client.put("/edit/occupation", json=body, headers=header)

    assert response.status_code == 404
    assert response.json() == {"detail": "UNAUTHORIZED_ACCESS"}


def test_change_occupation_employee_duplicate_true_should_error(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {"cpf": "12345678901", "manager": True, "attendant": True}

    response = client.put("/edit/occupation", json=body, headers=header)

    assert response.status_code == 400
    assert response.json() == {"detail": "USER_MUST_HAVE_ONLY_ONE_ROLE"}


def test_change_occupation_employee_duplicate_false_should_error(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "email": "email2@email.com",
        "name": "Christian Lopes",
        "cpf": "12345678901",
        "password": "12345678",
        "manager": True,
    }
    response = client.post("/register/employee", json=body)

    body = {"login": "17410599090", "password": "12345678"}
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = {"cpf": "12345678901", "manager": False, "attendant": False}

    response = client.put("/edit/occupation", json=body, headers=header)

    assert response.status_code == 400
    assert response.json() == {"detail": "USER_MUST_HAVE_ONLY_ONE_ROLE"}
