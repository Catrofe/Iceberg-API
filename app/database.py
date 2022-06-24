from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# postgresql+asyncpg://root:root@localhost:5432/Iceberg
ENGINE = create_async_engine("sqlite+aiosqlite:///db.db", echo=True)

ASYNC_SESSION = sessionmaker(ENGINE, expire_on_commit=False, class_=AsyncSession)


async def setup_db() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///db.db", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def async_main() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://root:root@localhost:5432/Iceberg", echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    number = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    manager = Column(Boolean, default=False)
    attendant = Column(Boolean, default=False)


class ForgotPassword(Base):
    __tablename__ = "forgot_password"
    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False)
    user = Column(Integer, ForeignKey("user.id"), nullable=False)
    requisition_date = Column(DateTime, nullable=False)
    utilized = Column(Boolean, default=False)
