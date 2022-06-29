import logging

from app.models import Error, UserOutput, UserRegister
from app.repository import UserRepository

logger = logging.getLogger()


async def create_user(
    user: UserRegister, repository: UserRepository
) -> UserOutput | Error:
    try:
        id = await repository.create_user(user)
        return UserOutput(id=id, email=user.email)
    except Exception as exc:
        logger.exception("here")
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)
