import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app, startup_event

client = TestClient(app)


@pytest.fixture
def drop_database():
    asyncio.run(startup_event(True))


def test_create_token_valid_should_success(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "phone": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)

    token = response.json()["token"]

    # get user logged
    response = client.get("/account/logged", headers={"Authorization": token})

    assert response.status_code == 200
    assert response.json() == {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "phone": "21999999999",
    }


def test_verify_token_expired(drop_database):
    # criar usuario
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "phone": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)

    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidHlwZSI6InVzZXIiLCJleHAiOjE2NTU2NTY\
wOTl9.sHjnzgmREKKbF26AXZjFFo-VNp2T_o8rS6mKUaZimjw"

    print(token)

    response = client.get("/account/logged", headers={"Authorization": token})

    assert response.status_code == 401
    assert response.json() == {"detail": "TOKEN_HAS_EXPIRED"}


def test_verify_token_invalid(drop_database):
    # criar usuario
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "phone": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)

    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwidHlw6InVzZXIiLCJleHAiOjE2NTU2NTYwOTl9.\
sHjnzgmREKKbF26AXZjFFo-VNp2T_o8rS6mKUaZimjw"

    # get user logged
    response = client.get("/account/logged", headers={"Authorization": token})

    assert response.status_code == 401
    assert response.json() == {"detail": "TOKEN_INVALID"}


def test_verify_token_invalid_signature(drop_database):
    body = {
        "email": "email@email.com",
        "name": "Christian Lopes",
        "cpf": "17410599090",
        "phone": "21999999999",
        "password": "12345678",
    }
    response = client.post("/register/user", json=body)

    body = {"login": "email@email.com", "password": "12345678"}
    response = client.post("/login/user", json=body)

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYxNmY4Y2NlMjdjNmI1OWRlNzFmM2FkMCIsImlhdC\
I6MTY1NTkzMTE1MywiZXhwIjoxNjU2NTM1OTUzfQ.xCbYI_aEhEVYagoeuL5peUuU4k2c32sNivkYIJfPoWE"

    response = client.get("/account/logged", headers={"Authorization": token})

    assert response.status_code == 401
    assert response.json() == {"detail": "INVALID_SIGNATURE"}
