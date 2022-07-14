from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


async def setup_db_tests(url_db: str) -> Any:
    engine = create_async_engine(url_db, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return async_session


async def setup_db_main(url_db: str) -> Any:
    engine = create_async_engine(url_db, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_session


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
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


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    activate = Column(Boolean, default=False)


class Order(Base):
    """
    status ->:
    WS - waiting store
    OR - Order refused
    OK - Order accepted
    OC - Order canceled
    OF - Order finished
    """

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("user.id"), nullable=False)
    price = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    requisition_date = Column(Date, nullable=False)
    finished = Column(Boolean, default=False)


class ItemOrder(Base):
    __tablename__ = "items_orders"
    id = Column(Integer, primary_key=True)
    order = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
