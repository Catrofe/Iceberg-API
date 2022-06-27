from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Product
from app.dataclass import Error
from app.models import CreateProductInput, CreateProductOutput


async def product_create(
    request: CreateProductInput, session_maker: sessionmaker[AsyncSession]
) -> CreateProductOutput | Error:
    try:
        if isinstance(request.price, str):
            request.price = float(request.price.replace(".", "").replace(",", "."))

            user_add = Product(
                name=request.name,
                description=request.description,
                image_url=request.image_url,
                price=request.price,
                activate=request.activate,
            )
        async with session_maker() as session:
            session.add(user_add)
            await session.commit()

        return CreateProductOutput(id=user_add.id, message="CREATE_PRODUCT_SUCCESS")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)
