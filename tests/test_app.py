import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.app import create_app
from app.database import User
from app.settings import Settings

db_url = "sqlite+aiosqlite:///tests/db.sqlite"


@pytest.fixture
def db() -> None:
    async def _setup():
        engine = create_async_engine(db_url, echo=False)
        async with engine.connect() as conn:
            await conn.run_sync(User.metadata.drop_all)
            await conn.run_sync(User.metadata.create_all)

    asyncio.run(_setup())


@pytest.fixture
def app(db: None) -> FastAPI:
    app = create_app(Settings(db_url=db_url))
    return app


def test_create_user_should_success(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "email": "email@email.com",
            "name": "Christian Lopes",
            "cpf": "17410599090",
            "phone": "21999999999",
            "password": "12345678",
        }

        response = client.post("/users", json=body)

        assert response.status_code == 201
        assert response.json() == {"id": 1, "email": "email@email.com"}


def test_create_user_conflict(app: FastAPI):
    with TestClient(app) as client:
        body = {
            "email": "email@email.com",
            "name": "Christian Lopes",
            "cpf": "17410599090",
            "phone": "21999999999",
            "password": "12345678",
        }

        client.post("/users", json=body)
        response = client.post("/users", json=body)

        assert response.status_code == 500
