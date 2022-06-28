from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://root:root@localhost:5432/Iceberg"
