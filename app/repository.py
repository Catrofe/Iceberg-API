import logging

from sqlalchemy.exc import DataError, IntegrityError, OperationalError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.crypto import encrypt_password
from app.database import User
from app.models import UserRegister

logger = logging.getLogger("synchronizer")

Base = declarative_base()


class UserRepository:
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
        )

    async def create_user(self, user: UserRegister) -> int:
        user_to_insert = User(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            number=user.number,
            password=await encrypt_password(user.password),
        )

        async with AsyncSession(self.engine) as session:
            try:
                session.add(user_to_insert)
                await session.commit()
                return user_to_insert.id
            except (
                OperationalError,
                DataError,
                StatementError,
                IntegrityError,
            ):
                logger.exception("Insert failed, rollbacking.")
                session.rollback()
                raise
