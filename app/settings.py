from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://root:root@localhost:5432/Iceberg"
    db_test: str = "sqlite+aiosqlite:///db.db"
