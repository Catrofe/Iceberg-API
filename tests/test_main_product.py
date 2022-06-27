import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app, startup_event

client = TestClient(app)


@pytest.fixture
def drop_database():
    asyncio.run(startup_event(True))


"""
Testes a realizar para o POST.
Teste 1: Teste para verificar se o produto está sendo criado corretamente.
Teste 2: Teste passando parametros inválidos.
"""


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
