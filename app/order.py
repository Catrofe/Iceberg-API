from __future__ import annotations

from datetime import date

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from app.database import ItemOrder, Order, Product
from app.models import (
    Error,
    GetAllOrdersOutput,
    GetOrderOutputToUser,
    ItemsOrders,
    OrderInput,
    OrderOutput,
    UserToken,
)


async def order_create(
    request: OrderInput, user: UserToken, session_maker: sessionmaker[AsyncSession]
) -> OrderOutput | Error:
    """
    status ->:
    WS - waiting store
    OR - Order refused
    OK - Order accepted
    OC - Order canceled
    OF - Order finished
    """
    try:
        order_create = Order(user=user.id, status="WS", requisition_date=date.today())

        async with session_maker() as session:
            session.add(order_create)
            await session.commit()

        for order in request.items:
            async with session_maker() as session:
                product_select = await session.execute(
                    select(Product).where(Product.id == order.id)
                )
                product = product_select.scalar()

                if not product:
                    return Error(
                        reason="NOT_FOUND", message="PRODUCT_NOT_FOUND", status_code=404
                    )

                item_order = ItemOrder(
                    order=order_create.id,
                    product=order.id,
                    quantity=order.quantity,
                    price=(product.price * order.quantity),
                )

                session.add(item_order)
                await session.commit()

        async with session_maker() as session:
            items_orders = await session.execute(
                select(func.sum(ItemOrder.price)).where(
                    ItemOrder.order == order_create.id
                )
            )
            price_general = items_orders.scalar()

            await (
                session.execute(
                    update(Order)
                    .where(Order.id == order_create.id)
                    .values(price=price_general)
                )
            )
            await session.commit()

        return OrderOutput(id=order_create.id, message="ORDER_CREATED_WITH_SUCCESS")
    except Exception as exc:
        return Error(reason="UNKNOWN", message=str(exc), status_code=500)


async def cancel_order(
    id: int, session_maker: sessionmaker[AsyncSession]
) -> OrderOutput | Error:
    try:
        async with session_maker() as session:
            order_select = await session.execute(
                select(Order).where(Order.id == id, Order.status == "WS")
            )
            order = order_select.scalar()

            if not order:
                return Error(
                    reason="NOT_FOUND", message="ORDER_NOT_FOUND", status_code=404
                )

            if order.finished:
                return Error(
                    reason="BAD_REQUEST",
                    message="ORDER_ALREADY_FINISHED",
                    status_code=400,
                )

            await (
                session.execute(update(Order).where(Order.id == id).values(status="OC"))
            )
            await session.commit()

            return OrderOutput(id=order.id, message="ORDER_CANCELED_WITH_SUCCESS")
    except Exception as exc:
        return Error(reason="UNKNOWN", message=str(exc), status_code=500)


async def return_order_by_id(
    id: int, session_maker: sessionmaker[AsyncSession]
) -> GetOrderOutputToUser | Error:
    """
    status ->:
    WS - waiting store
    OR - Order refused
    OK - Order accepted
    OC - Order canceled
    OF - Order finished
    """
    try:
        async with session_maker() as session:
            order_select = await session.execute(select(Order).where(Order.id == id))
            order = order_select.scalar()

            items_select = await session.execute(
                select(ItemOrder).where(ItemOrder.order == id)
            )
            items = items_select.scalars()

        if not order:
            return Error(reason="NOT_FOUND", message="ORDER_NOT_FOUND", status_code=404)

        list_products = [
            ItemsOrders(id=item.id, quantity=item.quantity) for item in items
        ]
        return GetOrderOutputToUser(
            id=order.id,
            status=order.status,
            price=order.price,
            requisition_date=order.requisition_date,
            finished=order.finished,
            products=list_products,
        )

    except Exception as exc:
        return Error(reason="UNKNOWN", message=str(exc), status_code=500)


async def return_all_orders(
    user: UserToken, session_maker: sessionmaker[AsyncSession]
) -> GetAllOrdersOutput | Error:
    """
    status ->:
    WS - waiting store
    OR - Order refused
    OK - Order accepted
    OC - Order canceled
    OF - Order finished
    """
    try:
        async with session_maker() as session:
            orders_select = await session.execute(
                select(Order).where(Order.user == user.id)
            )
            orders = orders_select.scalars()

        list_orders = []

        for order in orders:

            async with session_maker() as session:
                items_select = await session.execute(
                    select(ItemOrder).where(ItemOrder.order == order.id)
                )
                items = items_select.scalars()

            for iten in items:
                list_products = [ItemsOrders(id=iten.id, quantity=iten.quantity)]
            list_orders.append(
                GetOrderOutputToUser(
                    id=order.id,
                    status=order.status,
                    price=order.price,
                    requisition_date=order.requisition_date,
                    finished=order.finished,
                    products=list_products,
                )
            )

        return GetAllOrdersOutput(orders=list_orders)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=str(exc), status_code=500)


async def orders_active(
    user: UserToken, session_maker: sessionmaker[AsyncSession]
) -> GetAllOrdersOutput | Error:
    try:
        async with session_maker() as session:
            orders_select = await session.execute(
                select(Order).where(Order.user == user.id, Order.finished.is_(False))
            )
            orders = orders_select.scalars()

        list_orders = []

        for order in orders:

            async with session_maker() as session:
                items_select = await session.execute(
                    select(ItemOrder).where(ItemOrder.order == order.id)
                )
                items = items_select.scalars()

            for iten in items:
                list_products = [ItemsOrders(id=iten.id, quantity=iten.quantity)]
            list_orders.append(
                GetOrderOutputToUser(
                    id=order.id,
                    status=order.status,
                    price=order.price,
                    requisition_date=order.requisition_date,
                    finished=order.finished,
                    products=list_products,
                )
            )

        return GetAllOrdersOutput(orders=list_orders)

    except Exception as exc:
        return Error(reason="UNKNOWN", message=str(exc), status_code=500)
