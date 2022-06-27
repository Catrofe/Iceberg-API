from __future__ import annotations

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.database import Product
from app.models import (
    CreateProductInput,
    CreateProductOutput,
    Error,
    UpdateProductInput,
    UpdateProductOutput,
)


async def product_create(
    request: CreateProductInput, session_maker: sessionmaker[AsyncSession]
) -> CreateProductOutput | Error:
    try:
        if "," in request.price:
            price = float(request.price.replace(".", "").replace(",", "."))
        else:
            price = float(request.price)

        product_add = Product(
            name=request.name,
            description=request.description,
            image_url=request.image_url,
            price=price,
            activate=request.activate,
        )
        async with session_maker() as session:
            session.add(product_add)
            await session.commit()

        return CreateProductOutput(id=product_add.id, message="CREATE_PRODUCT_SUCCESS")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def update_product(
    request: UpdateProductInput, id: int, session_maker: sessionmaker[AsyncSession]
) -> UpdateProductOutput | Error:
    try:
        async with session_maker() as session:
            if request.name:
                await session.execute(
                    update(Product).where(Product.id == id).values(name=request.name)
                )

            if request.description:
                await session.execute(
                    update(Product)
                    .where(Product.id == id)
                    .values(description=request.description)
                )

            if request.image_url:
                await session.execute(
                    update(Product)
                    .where(Product.id == id)
                    .values(image_url=request.image_url)
                )

            if request.price:
                if "," in request.price:
                    price = float(request.price.replace(".", "").replace(",", "."))
                else:
                    price = float(request.price)

                await session.execute(
                    update(Product).where(Product.id == id).values(price=price)
                )

                await session.commit()

        return UpdateProductOutput(id=id, message="UPDATE_PRODUCT_SUCCESS")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def delete_product(
    id: int, session_maker: sessionmaker[AsyncSession]
) -> UpdateProductOutput | Error:
    try:
        async with session_maker() as session:
            product_select = await session.execute(
                select(Product.id).where(Product.id == id)
            )
            product = product_select.scalar()

            if not product:
                return Error(
                    reason="NOT_FOUND", message="PRODUCT_NOT_FOUND", status_code=404
                )

            await session.execute(delete(Product).where(Product.id == id))
            await session.commit()

        return UpdateProductOutput(id=id, message="DELETE_PRODUCT_SUCCESS")

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)
