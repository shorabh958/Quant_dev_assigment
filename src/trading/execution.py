from dataclasses import dataclass
from enum import Enum


class OrderState(str, Enum):
    NEW = "NEW"
    SUBMITTED = "SUBMITTED"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class ManagedOrder:
    client_id: str
    symbol: str
    side: str
    quantity: int
    filled_quantity: int = 0
    state: OrderState = OrderState.NEW


class OrderStateMachine:
    TERMINAL = {
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.REJECTED,
    }

    def __init__(self):
        self.orders: dict[str, ManagedOrder] = {}

    def submit(self, order: ManagedOrder) -> ManagedOrder:
        if order.client_id in self.orders:
            return self.orders[order.client_id]

        order.state = OrderState.SUBMITTED
        self.orders[order.client_id] = order
        return order

    def update(
        self,
        client_id: str,
        filled_quantity: int,
        state: OrderState,
    ):
        order = self.orders[client_id]

        if order.state in self.TERMINAL:
            return order

        if filled_quantity > order.quantity:
            raise ValueError("Filled quantity exceeds order quantity")

        order.filled_quantity = filled_quantity
        order.state = state
        return order

    def reconcile(self, broker_orders: list[ManagedOrder]):
        for broker_order in broker_orders:
            local = self.orders.get(broker_order.client_id)

            if local is None:
                self.orders[broker_order.client_id] = broker_order
            else:
                local.filled_quantity = broker_order.filled_quantity
                local.state = broker_order.state