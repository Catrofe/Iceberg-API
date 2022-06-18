from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# def build_engine(db_url: str) -> Engine:
#     return create_async_engine(db_url)


# def build_session_maker(engine: Engine) -> sessionmaker:
#     async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
#     return async_session


# async def setup_db(engine: Engine) -> None:
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.MetaData.create_all())

ENGINE = create_async_engine(
    "postgresql+asyncpg://root:root@localhost:5432/Iceberg", echo=True
)

ASYNC_SESSION = sessionmaker(ENGINE, expire_on_commit=False, class_=AsyncSession)


async def async_main() -> None:
    async with ENGINE.begin() as conn:
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
