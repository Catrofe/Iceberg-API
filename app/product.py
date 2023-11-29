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
    GetAllProductsOutput,
    GetProductIdOutput,
    GetProductsActivesOutput,
    InactivateProductInput,
    InactivateProductOutput,
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


async def update_product_status(
    request: InactivateProductInput, session_maker: sessionmaker[AsyncSession]
) -> InactivateProductOutput | Error:
    try:
        async with session_maker() as session:
            product_select = await session.execute(
                select(Product).where(Product.id == request.id)
            )
            product = product_select.scalar()

        if not product:
            return Error(
                reason="NOT_FOUND", message="PRODUCT_NOT_FOUND", status_code=404
            )

        async with session_maker() as session:
            await session.execute(
                update(Product)
                .where(Product.id == request.id)
                .values(activate=request.status)
            )
            await session.commit()

        return (
            InactivateProductOutput(
                id=request.id, message="ACTIVATE_PRODUCT_SUCCESS"
            )
            if request.status
            else InactivateProductOutput(
                id=request.id, message="INACTIVATE_PRODUCT_SUCCESS"
            )
        )
    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_product(
    id: int, session_maker: sessionmaker[AsyncSession]
) -> GetProductIdOutput | Error:
    try:
        async with session_maker() as session:
            product_select = await session.execute(
                select(Product).where(Product.id == id)
            )
            product = product_select.scalar()

        if product:
            return GetProductIdOutput(
                id=product.id,
                name=product.name,
                price=str(product.price).replace(".", ","),
                description=product.description,
                image_url=product.image_url,
                activated=product.activate,
            )

        else:
            return Error(
                reason="NOT_FOUND", message="PRODUCT_NOT_FOUND", status_code=404
            )

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_products_actives(
    session_maker: sessionmaker[AsyncSession],
) -> GetProductsActivesOutput | Error:
    try:
        async with session_maker() as session:
            product_select = await session.execute(
                select(Product).where(Product.activate)
            )
            products = product_select.scalars()

        list_products = []
        for iten in products:
            product_json = {
                "id": iten.id,
                "name": iten.name,
                "description": iten.description,
                "price": str(iten.price).replace(".", ","),
                "image_url": iten.image_url,
                "activated": iten.activate,
            }

            list_products.append(product_json)

        return GetProductsActivesOutput(products=list_products)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)


async def get_all_products(
    session_maker: sessionmaker[AsyncSession],
) -> GetAllProductsOutput | Error:
    try:
        async with session_maker() as session:
            product_select = await session.execute(select(Product).where())
            products = product_select.scalars()

        list_products = []
        for iten in products:
            product_json = {
                "id": iten.id,
                "name": iten.name,
                "description": iten.description,
                "price": str(iten.price).replace(".", ","),
                "image_url": iten.image_url,
                "activated": iten.activate,
            }

            list_products.append(product_json)

        return GetAllProductsOutput(products=list_products)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=repr(exc), status_code=500)
