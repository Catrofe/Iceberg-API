from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.database import ItemOrder, Order
from app.models import (
    Error,
    GetAllOrdersOutput,
    GetOrderOutputToUser,
    InputOrderShop,
    ItemsOrders,
)

"""
status ->:
WS - waiting store
OR - Order refused
OK - Order accepted
OC - Order canceled
OF - Order finished
"""


async def return_open_orders(
    session_maker: sessionmaker[AsyncSession],
) -> GetAllOrdersOutput | Error:
    try:
        async with session_maker() as session:
            orders_select = await session.execute(
                select(Order).where(Order.status == "WS")
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
                list_products = []
                list_products.append(ItemsOrders(id=iten.id, quantity=iten.quantity))

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

    except Exception:
        return Error(reason="UNKNOWN", message="UNKNOWN_ERROR", status_code=500)


async def accepted_or_recused_order(
    order_input: InputOrderShop, session_maker: sessionmaker[AsyncSession]
) -> GetOrderOutputToUser | Error:
    try:
        async with session_maker() as session:
            if order_input.accepted:
                await session.execute(
                    update(Order)
                    .where(Order.id == order_input.id, Order.status == "WS")
                    .values(status="OK")
                )
            else:
                await session.execute(
                    update(Order)
                    .where(Order.id == order_input.id, Order.status == "WS")
                    .values(status="OR", finished=True)
                )

            await session.commit()

            order_select = await session.execute(
                select(Order).where(Order.id == order_input.id)
            )
            order = order_select.scalar()

            items_select = await session.execute(
                select(ItemOrder).where(ItemOrder.order == order_input.id)
            )
            items = items_select.scalars()

        if not order:
            return Error(reason="NOT_FOUND", message="ORDER_NOT_FOUND", status_code=404)

        list_products = []
        for iten in items:
            list_products.append(ItemsOrders(id=iten.id, quantity=iten.quantity))

        return GetOrderOutputToUser(
            id=order.id,
            status=order.status,
            price=order.price,
            requisition_date=order.requisition_date,
            finished=order.finished,
            products=list_products,
        )

    except Exception:
        return Error(reason="UNKNOWN", message="UNKNOWN_ERROR", status_code=500)


async def cancel_order_accepted(
    order_id: int, session_maker: sessionmaker[AsyncSession]
) -> GetOrderOutputToUser | Error:
    try:
        async with session_maker() as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id, Order.status == "OK")
                .values(status="OC", finished=True)
            )
            await session.commit()

            order_select = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            order = order_select.scalar()

            items_select = await session.execute(
                select(ItemOrder).where(ItemOrder.order == order_id)
            )
            items = items_select.scalars()

        if not order:
            return Error(reason="NOT_FOUND", message="ORDER_NOT_FOUND", status_code=404)

        list_products = []
        for iten in items:
            list_products.append(ItemsOrders(id=iten.id, quantity=iten.quantity))

        return GetOrderOutputToUser(
            id=order_id,
            status=order.status,
            price=order.price,
            requisition_date=order.requisition_date,
            finished=order.finished,
            products=list_products,
        )

    except Exception:
        return Error(reason="UNKNOWN", message="UNKNOWN_ERROR", status_code=500)


async def finish_order_accepted(
    order_id: int, session_maker: sessionmaker[AsyncSession]
) -> GetOrderOutputToUser | Error:
    try:
        async with session_maker() as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id, Order.status == "OK")
                .values(status="OF", finished=True)
            )
            await session.commit()

            order_select = await session.execute(
                select(Order).where(Order.id == order_id)
            )
            order = order_select.scalar()

            items_select = await session.execute(
                select(ItemOrder).where(ItemOrder.order == order_id)
            )
            items = items_select.scalars()

        if not order:
            return Error(reason="NOT_FOUND", message="ORDER_NOT_FOUND", status_code=404)

        list_products = []
        for iten in items:
            list_products.append(ItemsOrders(id=iten.id, quantity=iten.quantity))

        return GetOrderOutputToUser(
            id=order_id,
            status=order.status,
            price=order.price,
            requisition_date=order.requisition_date,
            finished=order.finished,
            products=list_products,
        )

    except Exception:
        return Error(reason="UNKNOWN", message="UNKNOWN_ERROR", status_code=500)
