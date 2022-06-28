from dataclasses import dataclass

from fastapi import FastAPI, HTTPException

from app.database import setup_db
from app.models import Error, UserOutput, UserRegister
from app.repository import UserRepository
from app.settings import Settings
from app.user import create_user


def create_app() -> FastAPI:
    app = FastAPI()

    @dataclass
    class ServerContext:
        user_repository: UserRepository

    settings = Settings()
    context = ServerContext(user_repository=UserRepository(settings.db_url))

    @app.on_event("startup")
    async def startup() -> None:
        await setup_db(settings.db_url)

    @app.post("/users", status_code=201, response_model=UserOutput)
    async def register_user(user: UserRegister) -> UserOutput:
        response = await create_user(user, context.user_repository)

        if isinstance(response, UserOutput):
            return response

        if isinstance(response, Error):
            raise HTTPException(response.status_code, response.message)

    return app
