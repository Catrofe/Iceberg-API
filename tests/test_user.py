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

    print(response)

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
