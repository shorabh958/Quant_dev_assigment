from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass
class OrderRequest:
    client_order_id: str
    side: str
    quantity: int
    price: Decimal | None = None
    order_type: OrderType = OrderType.MARKET


class OrderManager:
    def __init__(self):
        self.orders: dict[str, OrderRequest] = {}

    def place(self, request: OrderRequest) -> OrderRequest:
        # Idempotency: same client ID cannot create a duplicate order.
        if request.client_order_id in self.orders:
            return self.orders[request.client_order_id]

        self.orders[request.client_order_id] = request
        return request

    def get(self, client_order_id: str) -> OrderRequest | None:
        return self.orders.get(client_order_id)