from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from .execution import ManagedOrder, OrderState


class StateStore:

    def __init__(
        self,
        path="data/state.json",
    ):
        self.path = Path(path)

    def save(self, orders):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = {}

        for key, order in orders.items():

            record = asdict(order)

            record["state"] = (
                order.state.value
            )

            payload[key] = record

        self.path.write_text(
            json.dumps(
                payload,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load(self):

        if not self.path.exists():
            return {}

        raw = json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

        result = {}

        for key, value in raw.items():

            result[key] = ManagedOrder(
                client_id=value["client_id"],
                symbol=value["symbol"],
                side=value["side"],
                quantity=value["quantity"],
                filled_quantity=value[
                    "filled_quantity"
                ],
                state=OrderState(
                    value["state"]
                ),
            )

        return result


class RecoveryManager:

    def __init__(self, state_store):
        self.state_store = state_store

    def checkpoint(self, orders):
        self.state_store.save(orders)

    def recover(self):
        return self.state_store.load()


@dataclass
class ReconciliationResult:
    symbol: str
    local_quantity: int
    broker_quantity: int

    @property
    def matched(self):
        return (
            self.local_quantity
            == self.broker_quantity
        )

    @property
    def difference(self):
        return (
            self.broker_quantity
            - self.local_quantity
        )


def reconcile_position(
    symbol: str,
    local_quantity: int,
    broker_quantity: int,
):
    return ReconciliationResult(
        symbol=symbol,
        local_quantity=local_quantity,
        broker_quantity=broker_quantity,
    )