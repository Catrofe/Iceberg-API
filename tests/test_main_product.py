import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app, startup_event

client = TestClient(app)


@pytest.fixture
def drop_database():
    asyncio.run(startup_event(True))


def register_user():
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "number": "21999999999",
        "password": "12345678",
    }
    client.post("/register/user", json=body)


def login_user() -> str:
    body = {
        "login": "email@email.com",
        "password": "12345678",
    }
    response = client.post("/login/user", json=body)
    print("RESPONSE LOGIN USER", response.text)
    return response.json()["token"]


def register_employee():
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    client.post("/register/employee", json=body)


def login_employee() -> str:
    body = {
        "login": "17410599090",
        "password": "12345678",
    }
    response = client.post("/login/employee", json=body)
    return response.json()["token"]


def create_product(token):
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10,00",
    }
    client.post("/create/product", json=body, headers=header)


def test_create_product_should_success(drop_database):
    # login employee
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }

    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }

    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10.00",
        "activated": True,
    }

    response = client.post("/create/product", json=body, headers=header)

    assert response.status_code == 201
    assert response.json() == {"id": 1, "message": "CREATE_PRODUCT_SUCCESS"}


def test_create_product_should_access_denied(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "number": "21999999999",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }

    response = client.post("/login/user", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }

    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10.00",
        "activated": True,
    }

    response = client.post("/create/product", json=body, headers=header)

    assert response.status_code == 403
    assert response.json() == {"detail": "ACCESS_DENIED"}


def test_update_product_name_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10.00",
        "activated": True,
    }
    response = client.post("/create/product", json=body, headers=header)

    body = {"id": 1, "name": "Açai 200ml"}
    response = client.put("/update/product/1", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "UPDATE_PRODUCT_SUCCESS"}


def test_update_product_description_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10.00",
        "activated": True,
    }
    response = client.post("/create/product", json=body, headers=header)

    body = {"id": 1, "description": "Açai gelado de 200ml"}
    response = client.put("/update/product/1", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "UPDATE_PRODUCT_SUCCESS"}


def test_update_product_image_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10.00",
        "activated": True,
    }
    response = client.post("/create/product", json=body, headers=header)

    body = {"id": 1, "image_url": "11111"}
    response = client.put("/update/product/1", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "UPDATE_PRODUCT_SUCCESS"}


def test_update_product_price_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "password": "12345678",
    }
    response = client.post("/register/employee", json=body)

    body = {
        "login": "17410599090",
        "password": "12345678",
    }
    response = client.post("/login/employee", json=body)
    token = response.json()["token"]

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    body = {
        "name": "Açai 200ml",
        "description": "Açai 200ml",
        "image_url": "http://www.google.com",
        "price": "10,00",
    }
    response = client.post("/create/product", json=body, headers=header)

    body = {"id": 1, "price": "11,99"}
    response = client.put("/update/product/1", json=body, headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "UPDATE_PRODUCT_SUCCESS"}


def test_delete_product_should_success(drop_database):
    register_employee()
    token = login_employee()
    create_product(token)

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    response = client.delete("/delete/product/1", headers=header)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "message": "DELETE_PRODUCT_SUCCESS"}


def test_delete_product_nonexistent_should_fail(drop_database):
    register_employee()
    token = login_employee()
    create_product(token)

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    response = client.delete("/delete/product/208", headers=header)

    assert response.status_code == 404
    assert response.json() == {"detail": "PRODUCT_NOT_FOUND"}


def test_delete_product_without_token_should_fail(drop_database):
    register_user()
    token = login_user()
    print(token)

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": token,
    }
    response = client.delete("/delete/product/1", headers=header)

    assert response.status_code == 403
    assert response.json() == {"detail": "ACCESS_DENIED"}
