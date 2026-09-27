from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator, Callable


class OrderStatus(str, Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class BrokerOrder:
    client_order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    status: OrderStatus = OrderStatus.NEW


class SimulatedBroker:

    def __init__(self):
        self.orders = {}
        self.positions = {}

    def place_order(self, order):

        if order.client_order_id in self.orders:
            return self.orders[
                order.client_order_id
            ]

        order.status = OrderStatus.FILLED

        self.orders[
            order.client_order_id
        ] = order

        signed_qty = (
            order.quantity
            if order.side == "BUY"
            else -order.quantity
        )

        self.positions[
            order.symbol
        ] = (
            self.positions.get(
                order.symbol,
                0,
            )
            + signed_qty
        )

        return order

    def cancel_order(
        self,
        client_order_id,
    ):

        order = self.orders.get(
            client_order_id
        )

        if order is None:
            return False

        if order.status == OrderStatus.FILLED:
            return False

        order.status = (
            OrderStatus.CANCELLED
        )

        return True

    def get_position(self, symbol):
        return self.positions.get(
            symbol,
            0,
        )

    def reconcile(self):
        return {
            "orders": dict(self.orders),
            "positions": dict(self.positions),
        }


@dataclass(frozen=True)
class Tick:
    symbol: str
    price: float
    timestamp: float


class TickStream:

    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, tick):
        await self.queue.put(tick)

    async def consume(self):
        return await self.queue.get()


class ResilientTickStream:

    """
    Local WebSocket-style market-data abstraction.

    A real Zerodha WebSocket implementation can later
    provide the same async tick interface.
    """

    def __init__(
        self,
        source_factory: Callable[
            [],
            AsyncIterator[Tick],
        ],
        reconnect_attempts: int = 3,
    ):
        self.source_factory = source_factory
        self.reconnect_attempts = (
            reconnect_attempts
        )

    async def stream(self):

        attempts = 0

        while attempts < self.reconnect_attempts:

            try:

                source = self.source_factory()

                async for tick in source:
                    attempts = 0
                    yield tick

                attempts += 1

            except Exception:

                attempts += 1

                if (
                    attempts
                    >= self.reconnect_attempts
                ):
                    raise

                await asyncio.sleep(
                    0.05 * attempts
                )