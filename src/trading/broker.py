from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum


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
    """Free local broker simulator for development/testing."""

    def __init__(self):
        self.orders: dict[str, BrokerOrder] = {}
        self.positions: dict[str, int] = {}

    def place_order(self, order: BrokerOrder) -> BrokerOrder:
        # Idempotency: same client ID never creates a second order.
        if order.client_order_id in self.orders:
            return self.orders[order.client_order_id]

        order.status = OrderStatus.FILLED
        self.orders[order.client_order_id] = order

        signed_qty = order.quantity if order.side == "BUY" else -order.quantity
        self.positions[order.symbol] = (
            self.positions.get(order.symbol, 0) + signed_qty
        )

        return order

    def cancel_order(self, client_order_id: str) -> bool:
        order = self.orders.get(client_order_id)

        if order is None:
            return False

        if order.status == OrderStatus.FILLED:
            return False

        order.status = OrderStatus.CANCELLED
        return True

    def get_position(self, symbol: str) -> int:
        return self.positions.get(symbol, 0)

    def reconcile(self) -> dict:
        return {
            "orders": dict(self.orders),
            "positions": dict(self.positions),
        }


@dataclass
class Tick:
    symbol: str
    price: float
    timestamp: float


class TickStream:
    """Async market-data simulator."""

    def __init__(self):
        self.queue: asyncio.Queue[Tick] = asyncio.Queue()

    async def publish(self, tick: Tick):
        await self.queue.put(tick)

    async def consume(self) -> Tick:
        return await self.queue.get()