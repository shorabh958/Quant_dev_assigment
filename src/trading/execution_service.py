from __future__ import annotations

from dataclasses import dataclass

from .broker_adapter import RESTBrokerClient
from .execution import (
    ManagedOrder,
    OrderState,
    OrderStateMachine,
)


@dataclass(frozen=True)
class ExecutionRequest:
    client_order_id: str
    symbol: str
    side: str
    quantity: int
    price: float


class OrderExecutionService:

    def __init__(
        self,
        broker: RESTBrokerClient,
        state_machine: OrderStateMachine | None = None,
    ):
        self.broker = broker
        self.state_machine = (
            state_machine
            or OrderStateMachine()
        )

    def submit(
        self,
        request: ExecutionRequest,
    ) -> ManagedOrder:

        # ----------------------------------------------
        # Idempotency:
        # repeated client_order_id returns the
        # existing local order.
        # ----------------------------------------------

        existing = self.state_machine.orders.get(
            request.client_order_id
        )

        if existing is not None:
            return existing

        order = ManagedOrder(
            client_id=request.client_order_id,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
        )

        self.state_machine.submit(order)

        try:

            response = self.broker.place_order(
                client_order_id=request.client_order_id,
                symbol=request.symbol,
                side=request.side,
                quantity=request.quantity,
                price=request.price,
            )

            filled_quantity = int(
                response.get(
                    "filled_quantity",
                    request.quantity,
                )
            )

            status = response.get(
                "status",
                "FILLED",
            )

            if status == "FILLED":
                state = OrderState.FILLED

            elif status == "PARTIAL":
                state = OrderState.PARTIAL

            elif status == "REJECTED":
                state = OrderState.REJECTED

            else:
                state = OrderState.SUBMITTED

            return self.state_machine.update(
                request.client_order_id,
                filled_quantity,
                state,
            )

        except Exception:

            self.state_machine.update(
                request.client_order_id,
                0,
                OrderState.REJECTED,
            )

            raise

    def reconcile(self, broker_orders):
        self.state_machine.reconcile(
            broker_orders
        )

        return self.state_machine.orders