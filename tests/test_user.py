import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.user import create_token_email, encrypt_password

client = TestClient(app)


def test_create_token_email():
    token = asyncio.run(create_token_email())

    assert token is not None
    assert isinstance(token, str)


def test_verify_encrypt_password_should_success():
    password = asyncio.run(encrypt_password("12345678"))

    assert password is not None
    assert isinstance(password, str)
