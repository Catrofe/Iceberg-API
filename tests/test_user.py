import asyncio

import pytest
from fastapi.testclient import TestClient

from app.database import setup_db
from app.main import app

client = TestClient(app)


@pytest.fixture
def drop_database():
    asyncio.run(setup_db())


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
