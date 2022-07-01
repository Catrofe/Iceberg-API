import logging
from typing import Optional, cast

from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.crypto import encrypt_password
from app.database import User
from app.models import UserId, UserRegister

logger = logging.getLogger("synchronizer")

Base = declarative_base()


class UserRepository:
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
        )

    async def create_user(self, new_user: UserRegister) -> Optional[UserId]:
        user = User(
            name=new_user.name,
            email=new_user.email,
            cpf=new_user.cpf,
            phone=new_user.phone,
            password=await encrypt_password(new_user.password),
        )
        async with AsyncSession(self.engine) as session:
            try:
                session.add(user)
                await session.commit()
                created_user = await self.get_user_by_email(new_user.email)
                if created_user is not None:
                    return created_user.id

                raise RuntimeError("Could not retrieve created user.")
            except (
                OperationalError,
                DataError,
                StatementError,
                IntegrityError,
            ):
                logger.exception("Insert failed, rollbacking.")
                await session.rollback()
                raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with AsyncSession(self.engine) as session:
            query = await session.execute(select(User).where(User.email == email))
            maybe_user = query.scalars().first()
            if maybe_user is not None:
                return cast(User, maybe_user)
            else:
                return None
