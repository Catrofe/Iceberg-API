from typing import Literal, Union

from pydantic import BaseModel, BaseSettings


class TestConfig(BaseSettings):
    env: Literal["test"]
    db_url: str = "sqlite+aiosqlite:///db.db"


class DevConfig(BaseSettings):
    env: Literal["dev"]
    db_url: str = "postgresql+asyncpg://root:root@localhost:5432/Iceberg"


class Config(BaseModel):
    config: Union[DevConfig, TestConfig]
